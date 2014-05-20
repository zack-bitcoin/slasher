import blockchain, custom, copy, tools
#This file explains how we tell if a transaction is valid or not, it explains 
#how we update the system when new transactions are added to the blockchain.
def signatures_check(tx):
    def sigs_match(sigs, pubs, msg):
        sigs=copy.deepcopy(sigs)
        sigs2=copy.deepcopy(sigs)
        pubs=copy.deepcopy(pubs)
        pubs2=copy.deepcopy(pubs)
        for sig in sigs:
            for pub in pubs:
                if tools.verify(msg, sig, pub):
                    sigs2.remove(sig)
                    pubs2.remove(pub)
        return len(sigs2)==0
    tx_copy=copy.deepcopy(tx)
    tx_copy.pop('signatures')
    msg=tools.det_hash(tx_copy)
    print(' in sig check: ' +str(tx))
    if not sigs_match(tx['signatures'], tx['pubkeys'], msg): 
        print('bad sig')
        return False
    return True

def spend_verify(tx, txs, DB): 
    tx_copy_2=copy.deepcopy(tx)
    if len(tx['pubkeys'])==0: return False
    if len(tx['signatures'])>len(tx['pubkeys']): return False
    if not signatures_check(tx): return False
    address=tools.addr(tx_copy_2)
    total_cost=0
    for Tx in filter(lambda t: address==tools.addr(t), [tx]+txs):
        if Tx['type']=='spend':
            total_cost+=Tx['amount']
    return int(blockchain.db_get(address, DB)['amount'])>=total_cost

def census_verify(tx, txs, DB):
    if not signatures_check(tx): return False
    return True

def sign_verify(tx, txs, DB):
    #print('tx: ' +str(tx))
    if not tools.E_check(tx, 'sign_on', int):
        print('no sign on')
        return False
    if DB['length']< tx['sign_on']: 
        print('1')
        return False
    if DB['length']>tx['sign_on']+10: 
        print('2')
        return False
    if not signatures_check(tx): 
        print('3')
        return False
    if not tools.E_check(tx, 'secret_hash', str): 
        print('4')
        return False
    if len(tx['secret_hash']) != 31: 
        print('5')
        return False
    print('tx: ' +str(tx))
    if tools.addr(tx) in map(lambda t: t['address'], blockchain.db_get(tx['sign_on'], DB)['secret_hashes']):
        print('Each address can sign each block a maximum of 1 time')
        return False
    address=tools.addr(tx)
    a=tools.det_hash({'address': address,
                      'length': DB['length'],
        'secrets':tools.recent_blockthings('secrets', DB, tx['sign_on']-2000, tx['sign_on']-1900)})
    balance=blockchain.db_get(address, DB, 'db_old')['amount']
    target=tools.target_times_float('f'*64, 64*balance/DB['all_money'])
    
    print('DB: ' +str(DB))
    print('target: ' +str(target))
    print('hash: ' +str(a))
    size=max(len(a), len(target))
    if tools.buffer_(a, size)>=tools.buffer_(target, size):
        print('6')
        return False
    return True
def reveal_secret_verify(tx, txs, DB):
    if DB['length']< tx['sign_on']+100: 
        print('too soon')
        return False
    if DB['length']>tx['sign_on']+900: 
        print('too late')
        return False
    if not tools.make_address([tx['secret']], 1)==tx['secret_hash']: 
        print('secret does not match')
        return False
    address=tools.addr(tx)
    secret_hash=filter(lambda t: t['address']==address and t['hash']==tx['secret_hash'], blockchain.db_get(tx['sign_on'])['secret_hashes'])
    if len(secret_hash)<1:
        print('did not sign that block...')
        return False
    return True
def slasher_verify(tx, txs, DB):
    if not signatures_check(tx): return False
    if not signatures_check(tx['tx1']): return False
    if not signatures_check(tx['tx2']): return False
    if tools.addr(tx['tx1'])!=tools.addr(tx['tx2']): return False
    if tx['tx1']['sign_on'] != tx['tx2']['sign_on']: return False
    return True

tx_check={'spend':spend_verify, 
          'sign':sign_verify, 
          'reveal_secret':reveal_secret_verify, 
          'slasher':slasher_verify, 
          'census':census_verify}####
#------------------------------------------------------

def adjust_int(key, pubkey, amount, DB):
    acc=blockchain.db_get(pubkey, DB)
    n=0
    if key=='amount': n=amount
    sign=-1
    if DB['add_block']: sign=1
    acc[key]+=(sign*amount)
    DB['all_money']+=(sign*n)
    blockchain.db_put(pubkey, acc, DB)
def adjust_list(key, pubkey, remove, item, DB):
    acc=blockchain.db_get(pubkey, DB)
    if remove != (DB['add_block']):# 'xor' == '!='
        acc[key].append(item)
    else: acc[key].remove(item)
    blockchain.db_put(pubkey, acc, DB)    
def spend(tx, DB):
    address=tools.addr(tx)
    adjust_int('amount', address, -tx['amount']-tx['fee'], DB)
    adjust_int('amount', tx['to'], tx['amount'], DB)
    adjust_int('count', address, 1, DB)
def secret(tx): return {'hash':tx['secret_hash'], 
                        'address':tools.addr(tx)}
def sign(tx, DB):
    adjust_int('count', tools.addr(tx), 1, DB)
    adjust_list('secret_hashes', tx['sign_on'], False, secret(tx), DB)
    if DB['add_block']: DB['sigLength']+=1
    else: DB['sigLength']-=1
def reveal_secret(tx, DB):
    address=tools.addr(tx)
    adjust_int('count', address, 1, DB)
    adjust_int('amount', address, custom.pos_reward, DB)
    adjust_list('secret_hashes', tx['sign_on'], True, secret(tx), DB)
    adjust_list('secrets', tx['sign_on'], False, tx['secret'], DB)
    
def slasher(tx, DB):
    address=tools.addr(tx)
    criminal=tools.addr(tx['tx1'])
    adjust_int('amount', criminal, custom.pos_reward/3, DB)
    adjust_list('secret_hashes', tx['tx1']['sign_on'], False, tx['secret_hash'], DB)

def census(tx, DB):
    pass



update={'spend':spend,
        'sign':sign,
        'reveal_secret':reveal_secret,
        'slasher':slasher,
        'census':census}####
#-----------------------------------------
