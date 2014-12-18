"""This file explains how we tell if a transaction is valid or not, it explains
how we update the database when new transactions are added to the blockchain."""
#Whether you are a signer depends on:
#5000=long_time*2-medium_time
#500=medium_time/2
#K-5000: how much money you had at this point.
#K-5000, -4500: random numbers selected here
#K-2500, -1000: random numbers revealed in this range
#K: sign on this block and make deposit and give hash(secret)
#K+2500, +3500: get reward. slasher is no longer possible. reveals secret

import blockchain, custom, copy, tools
E_check=tools.E_check
def sigs_match(Sigs, Pubs, msg):
    pubs=copy.deepcopy(Pubs)
    sigs=copy.deepcopy(Sigs)
    def match(sig, pubs, msg):
        for p in pubs:
            if tools.verify(msg, sig, p):
                return {'bool':True, 'pub':p}
        return {'bool':False}
    for sig in sigs:
        a=match(sig, pubs, msg)
        if not a['bool']:
            return False
        sigs.remove(sig)
        pubs.remove(a['pub'])
    return True
def signature_check(tx):
    tx_copy = copy.deepcopy(tx)
    if not E_check(tx, 'signatures', list):
        tools.log('no signautres')
        return False
    if not E_check(tx, 'pubkeys', list):
        tools.log('no pubkeys')
        return False
    tx_copy.pop('signatures')
    if len(tx['pubkeys']) == 0:
        tools.log('pubkey error')
        return False
    if len(tx['signatures']) > len(tx['pubkeys']):
        tools.log('sigs too long')
        return False
    msg = tools.det_hash(tx_copy)
    if not sigs_match(copy.deepcopy(tx['signatures']),
                      copy.deepcopy(tx['pubkeys']), msg):
        tools.log('sigs do not match')
        return False
    return True

def spend_verify(tx, txs, out, DB):
    if not E_check(tx, 'to', [str, unicode]):
        out[0]+='no to'
        return False
    if not signature_check(tx):
        out[0]+='signature check'
        return False
    if len(tx['to'])<=30:
        out[0]+='that address is too short'
        out[0]+='tx: ' +str(tx)
        return False
    if not E_check(tx, 'amount', int):
        out[0]+='no amount'
        return False
    if not tools.fee_check(tx, txs, DB):
        out[0]+='fee check error'
        return False
    if 'vote_id' in tx:
        if not tx['to'][:-29]=='11':
            out[0]+='cannot hold votecoins in a multisig address'
            return False
    return True
def sign_verify(tx, txs, out, DB):
    a=tools.addr(tx)
    B=tx['B']#verify a proof that addr(tx) actually owned that much money long*2-medium ago.
    M=custom.all_money
    address=tools.addr(tx)
    block=tools.db_get(tx['on_block'])
    num=max(0,tx['on_block']-(custom.long_time*2-custom.medium_time))
    election_block=tools.db_get(num)
    if 'root_hash' not in election_block:
        return False
    v=tools.db_verify(election_block['root_hash'], address, tx['proof'])
    if v==False:
        tools.log('your address did not exist that long ago.')
        tools.log(tools.db_root()+' '+address+' '+tx['proof'])
        return False
    if v['amount']!=tx['B']:
        tools.log('that is not how much money you had that long ago')
        return False
    if 'secret_hash' not in tx:
        tools.log('need the hash of a secret')
        return False
    for t in txs:
        if tools.addr(t)==address and tx['type']=='sign':
            #tools.log('can only have one sign tx per block')
            return False
    if len(tx['jackpots'])<1: 
        tools.log('insufficient jackpots')
        return False
    if not signature_check(tx):
        out[0]+='signature check'
        return False
    length=tools.local_get('length')
    if tx['on_block']!=length+1:
        out[0]+='this tx is for the wrong block'
        return False
    if tx['on_block']>0:
        if not tx['prev']==tools.db_get(length)['block_hash']:
            tools.log('must give hash of previous block')
            return False
    ran=tools.det_random(tx['on_block'])
    for j in tx['jackpots']:
        if type(j)!=int or j not in range(200):
               tools.log('bad jackpot')
               return False
        if len(filter(lambda x: x==j, tx['jackpots']))!=1:
               tools.log('no repeated jackpots')
               return False
        if not tools.winner(B, M, ran, address, j):
            tools.log('that jackpot is not valid: '+str(j))
            return False
    if tx['amount']<custom.minimum_deposit:
        tools.log('you have to deposit more than that')
        return False
    return True
def slasher_verify(tx, txs, out, DB):
    #were the rewards paid out already?
    #are both tx valid?
    #do they both sign on the same length?
    #are the tx identical?
    pass
def reward_verify(tx, txs, out, DB):
    address=tools.addr(tx)
    acc=tools.db_get(address)
    relative_reward=tools.relative_reward(tx)
    txs=tools.db_get(tx['on_block'])['txs']
    txs=filter(lambda t: t==t['sign'], txs)
    sign_tx=filter(lambda t: tools.addr(t)==address, txs)[0]
    length=tools.db_get('length')
    if length-custom.long_time+custom.medium_time/2>tx['on_block']or length-custom.long_time-custom.medium_time/2<tx['on_block']:
        tools.log('you did not wait the correct amount of time')
        return False
    if acc['secrets'][str(tx['on_block'])]['slashed']:
        tools.log('you were slashed, so you cannot collect your reward')
        return False
    if tx['amount']!=relative_reward+sign_tx['amount']:
        tools.log('reward wrong size')
        return False
    if sign_tx['secret_hash']!=det_hash(tx['reveal']):
        tools.log('entropy+salt does not match')
        return False
    if tx['reveal']['entropy'] not in [0,1]:
        tools.log('entropy must be either 0 or 1')
        return False
    return True
tx_check = {'spend':spend_verify,
            'sign':sign_verify,
            'slasher':slasher_verify,
            'reward':reward_verify}
'''
1) give signer's deposit
*reward is proportional to deposit size.
2) sign
3) double-sign slash
4) claim reward
*reveal one bit of entropy
*vote on system constants?
'''
#------------------------------------------------------
adjust_int=tools.adjust_int
adjust_dict=tools.adjust_dict
adjust_list=tools.adjust_list
symmetric_put=tools.symmetric_put
def spend(tx, DB, add_block):
    address = tools.addr(tx)
    adjust_int(['amount'], address, -tx['amount'], DB, add_block)
    adjust_int(['amount'], tx['to'], tx['amount'], DB, add_block)
    #adjust_int(['amount'], address, -custom.fee, DB, add_block)
    adjust_int(['amount'], address, -tx['fee'], DB, add_block)
def sign(tx, DB, add_block):#should include hash(entroy_bit and salt)
    address = tools.addr(tx)
    adjust_int(['amount'], address, -tx['amount'], DB, add_block)
    adjust_dict(['secrets'], address, False, {str(tx['on_block']):{'slashed':False}}, DB, add_block)
def slasher(tx, DB, add_block):
    address = tools.addr(tx)
    adjust_string(['secrets', tx['on_block'], 'slashed'], tools.addr(tx['tx1']), False, True, DB, add_block)
    adjust_int(['amount'], address, tx['amount']/5, DB, add_block)
    #tx={'amount':10000, 'tx1': , 'tx2': , 'reward_address': }
    #record
def reward(tx, DB, add_block):
    address = tools.addr(tx)
    length=tools.db_get('length')
    adjust_dict(['entropy'], address, False, {str(tx['on_block']):{'power':len(tx['jackpots']),'vote':tx['entropy']}}, DB, add_block)
    adjust_int(['amount'], address, tx['amount'], DB, add_block)
    #give them money back, and a proportional part of othe reward.
update = {'spend':spend,
          'sign':sign,
          'slasher':slasher,
          'reward':reward}
