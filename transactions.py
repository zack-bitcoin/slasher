"""This file explains how we tell if a transaction is valid or not, it explains
how we update the database when new transactions are added to the blockchain."""
import blockchain, custom, copy, tools, txs_tools
E_check=tools.E_check
def sigs_match(Sigs, Pubs, msg):
    pubs=copy.deepcopy(Pubs)
    sigs=copy.deepcopy(Sigs)
    def match(sig, pubs, msg):
        for p in pubs:
            if tools.verify(msg, sig, p):
                return {'bool':True, 'pub':pub}
        return {'bool':False}
    for sig in sigs:
        a=match(sig, pubs, msg)
        if not a['bool']:
            return False
        sigs.pop(sig)
        pubs.pop(a['pub'])
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
def spend_verify(tx, txs, DB):
    if not E_check(tx, 'to', [str, unicode]):
        tools.log('no to')
        return False
    if not signature_check(tx):
        tools.log('signature check')
        return False
    if len(tx['to'])<=30:
        tools.log('that address is too short')
        tools.log('tx: ' +str(tx))
        return False
        return False
    if not E_check(tx, 'amount', int):
        tools.log('no amount')
        return False
    tx_copy.pop('signatures')
    if not txs_tools.fee_check(tx, txs, DB):
        tools.log('fee check error')
        return False
    return True
def sign_verify(tx, txs, DB):
    return True
def reveal_secret_verify(tx, txs, DB):
    return True
def sign_slasher_verify(tx, txs, DB):
    if not signatures_check(tx): return False
    if not signatures_check(tx['tx1']): return False
    if not signatures_check(tx['tx2']): return False
    if tools.addr(tx['tx1'])!=tools.addr(tx['tx2']): return False
    if tx['tx1']['sign_on'] != tx['tx2']['sign_on']: return False
    return True
def pledge_verify(tx, txs, DB):
    return True
def pledge_slasher_verify(tx, txs, DB):
    return True
tx_check = {'spend':spend_verify,
            'sign':sign_verify,
            'reveal_secret':reveal_secret_verify,
            'sign_slasher':sign_slasher_verify,
            'pledge':pledge_verify,
            'pledge_slasher':plege_slasher_verify}
#------------------------------------------------------
adjust_int=txs_tools.adjust_int
adjust_dict=txs_tools.adjust_dict
adjust_list=txs_tools.adjust_list
symmetric_put=txs_tools.symmetric_put
#def mint(tx, DB):
#    address = tools.addr(tx)
#    adjust_int(['amount'], address, custom.block_reward, DB)
#    adjust_int(['count'], address, 1, DB)
def spend(tx, DB):
    address = tools.addr(tx)
    adjust_int(['amount'], address, -tx['amount'], DB)
    adjust_int(['amount'], tx['to'], tx['amount'], DB)
    adjust_int(['amount'], address, -custom.fee, DB)
    adjust_int(['count'], address, 1, DB)
def sign(tx, DB):
    '''
    print('DOING SIGN')
    address=tools.addr(tx)
    start=blockchain.db_get(tx['sign_on'], DB)
    print('start: ' +str(start))
    balance=blockchain.db_get(address, DB, 'db_old')['amount']
    adjust_int('count', tools.addr(tx), 1, DB)
    adjust_list('secret_hashes', tx['sign_on'], False, secret(tx), DB)
    signers=custom.normal_ns
    if tools.check_point_p({'length': DB['length']+10}): 
        print('THIS IS THE HUGE BLOCK, it is number: ' +str(DB['length']))
        signers=custom.large_ns
    sig_length=signers*balance/DB['all_money']
    if sig_length<1: sig_length=1
    if DB['add_block']: DB['sigLength']+=sig_length
    else: DB['sigLength']-=sig_length
    start=blockchain.db_get(tx['sign_on'], DB)
    print('end: ' +str(start))
    '''
def reveal_secret(tx, DB):
    address=tools.addr(tx)
    '''
    adjust_int('count', address, 1, DB)
    adjust_int('amount', address, custom.pos_reward, DB)
    adjust_list('secret_hashes', tx['sign_on'], True, secret(tx), DB)
    adjust_list('secrets', tx['sign_on'], False, tx['secret'], DB)
    '''
def slasher(tx, DB):
    '''
    address=tools.addr(tx)
    criminal=tools.addr(tx['tx1'])
    adjust_int('count', address, 1, DB)
    adjust_int('amount', criminal, custom.pos_reward/3, DB)
    adjust_list('secret_hashes', tx['tx1']['sign_on'], False, tx['secret_hash'], DB)
    '''
def pledge(tx, DB):
    pass

update = {'spend':spend,
          'sign':sign,
          'reveal_secret':reveal_secret,
          'slasher':slasher,
          'pledge':pledge}
