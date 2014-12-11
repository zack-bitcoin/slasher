"""This file explains how we tell if a transaction is valid or not, it explains
how we update the database when new transactions are added to the blockchain."""

#steps
#K-3000: based on how much money you had at this point in time
#K-2000: using random numbers from this point in time
#K: sign on block and make a deposit
#K+3000 to K+3100: get reward
#K to K+3000: it is possible to slasher the deposit
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
    B=tools.db_get(a)['amount']
    M=custom.all_money
    address=tools.addr(tx)
    #B is balance from 3000 blocks ago.
    if 'secret_hash' not in tx:
        tools.log('need the hash of a secret')
        return False
    if 'entropy' not in tx or tx['entropy'] not in [0, 1]:
        tools.log('needs a bit of entropy:  '+str(tx))
        return False
    for t in txs:
        if tools.addr(t)==address:
            tools.log('can only have one sign tx per block')
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
        out[0]+='tx: ' +str(tx)
        out[0]+='should be: ' +str(length+1)
        return False
    if tx['on_block']>0:
        if not tx['prev']==tools.db_get(length)['block_hash']:
            tools.log('must give hash of previous block')
            return False
    ran=det_random(tx['on_block'])
    for j in tx['jackpots']:
        if type(j)!=int or j not in range(200):
               tools.log('bad jackpot')
               return False
        if len(filter(lambda x: x==j, tx['jackpots']))!=1:
               tools.log('no repeated jackpots')
               return False
        if not winner(B, M, ran, address, j):
            tools.log('that jackpot is not valid: '+str(j))
            return False
    if tx['amount']<custom.minimum_deposit:
        tools.log('you have to deposit more than that')
        return False
    return True
def det_random(length):#this is very slow. we should memoize entropy somewhere.
    def mean(l): return sorted(l)[len(l)/2]
    ran=[]
    m=custom.long_time-custom.medium_time
    for i in range(custom.medium_time/2):
        a=length-m-i
        if a<0:
            ran.append(a)
        else:
            a=tools.db_get(a)
            ran.append(a['entropy'])
    out=[]
    while ran!=[]:
        a=min(17, len(ran))
        l=ran[0:a]
        ran=ran[a:]
        out.append(mean(l))
    return tools.det_hash(out)
def winner(B, M, ran, my_address, j):
    b=tools.hash2int('f'*64)*64*B/(200*M)
    a=tools.hash2int(tools.det_hash(str(ran)+str(my_address)+str([j])))
    return a<b
def slasher_verify(tx, txs, out, DB):
    #were the rewards paid out already?
    #are both tx valid?
    #do they both sign on the same length?
    #are the tx identical?
    pass
def reward_verify(tx, txs, out, DB):
    #make sure they revealed.
    #make sure they were not slashed.
    #reward is proportional to percentage of total deposit.
    pass
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
    adjust_int(['amount'], address, -custom.fee, DB, add_block)
def sign(tx, DB, add_block):
    address = tools.addr(tx)
    adjust_int(['amount'], address, -tx['amount'], DB, add_block)
    adjust_int(['amount'], address, -custom.deposit_fee, DB, add_block)
    #record somewhere. maybe on the block in the future?
def slasher(tx, DB, add_block):
    address = tools.addr(tx)
    #destroy the deposit. give a portion of it as a reward to the person who caught the criminal.
    #record
def reward(tx, DB, add_block):
    address = tools.addr(tx)
    #if they successfully signed, then reward them. otherwise punish them by taking 2 times the reward from their deposit, and returning the rest to them.
    #record
    pass
update = {'spend':spend,
          'sign':sign,
          'slasher':slasher,
          'reward':reward}
