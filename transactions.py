import blockchain, custom, copy, tools, Add_Block
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
    msg=tools.tx_hash(tx)
    if not sigs_match(tx['signatures'], tx['pubkeys'], msg): 
        print('bad sig')
        return False
    return True
def spend_verify(tx, txs, DB): 
    tx_copy_2=copy.deepcopy(tx)
    if not tools.E_check(tx, 'fee', int): return False
    if tx['fee']<custom.min_fee: return False
    if len(tx['pubkeys'])==0: return False
    if len(tx['signatures'])>len(tx['pubkeys']): return False
    if not signatures_check(tx): return False
    address=tools.addr(tx_copy_2)
    total_cost=0
    for Tx in filter(lambda t: address==tools.addr(t), [tx]+txs):
        if Tx['type']=='spend':
            total_cost+=Tx['amount']
            total_cost+=Tx['fee']
    return int(blockchain.db_get(address, DB)['amount'])>=total_cost
def sign_verify(tx, txs, DB):
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
    if not tools.E_check(tx, 'secret_hash', [str, unicode]): 
        #print('no secret hash')
        #print('tx: ' +str(tx))
        #print('4')
        return False
    if len(tx['secret_hash']) != 31: 
        print('5')
        return False
    print('tx: ' +str(tx))
    if tools.addr(tx) in map(lambda t: t['address'], blockchain.db_get(tx['sign_on'], DB)['secret_hashes']):
        print('Each address can sign each block a maximum of 1 time')
        return False
    address=tools.addr(tx)
    secrets=tools.recent_blockthings('secrets', DB, tx['sign_on']-2000, tx['sign_on']-1900)
    secrets_={}#we need this to stay in the same order. det_hash normally uses sorted on lists.
    for i in range(len(secrets)):
        secrets_[str(i)]=secrets[i]
    a=tools.det_hash({'address': address,
                      'length': DB['length'],
                      'secrets':secrets_})
    balance=blockchain.db_get(address, DB, 'db_old')['amount']
    target=tools.target_times_float('f'*64, 64*balance/DB['all_money'])
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
    
def check_point_verify(tx, txs, DB):
    print('CHECK POINT VERIFY')
    if not tools.E_check(tx, 'sign_on', int):
        print('no sign on')
        return False
    if not Add_Block.check_point_p(DB): return False
    address=tools.addr(tx)
    acc=blockchain.db_get(address, DB)
    if DB['length']>custom.check_point_length:
        if not tools.E_check(tx, 'prev_check_point_hash', [str, unicode]): return False
    if not tools.E_check(acc, 'stake', int): return False
    if not tools.E_check(acc, 'stake_flag', bool): return False
    if not acc['stake_flag']: return False
    if not signatures_check(tx): return False
    return True
def check_point_slasher_verify(tx, txs, DB):
    if not tools.E_check(tx, 'tx', dict): return False
    if tools.E_check(tx, 'tx2', dict):
        if not tools.E_check(tx, 'tx', dict): return False
        for i in ['tx', 'tx2']:
            if not check_point_verify(tx[i], [], DB): return False
        def g(x): return tx[x]['prev_check_point_hash']
        if g('tx') != g('tx2'): return False
        def f(x): return tools.tx_hash(tx[x])
        if f('tx')==f('tx2'): return False
    else:
        if not check_point_verify(tx['tx'], [], DB): return False
        check_point_hashes=tools.recent_blockthings('prev_block_hash', DB, custom.check_point_length, DB['length'], custom.check_point_length)
        if not tx['tx']['prev_check_point_hash'] in check_point_hashes: return False
    if not signatures_check(tx): return False
    address=tools.addr(tx['tx_'])
    acc=blockchain.db_get(address, DB)
    if not E_check(acc, 'stake', int): return False
    if not E_check(acc, 'stake_flag', bool): return False
    if not acc['stake_flag']: return False
    #more checks...
    
    return True

tx_check={'spend':spend_verify, 
          'sign':sign_verify, 
          'reveal_secret':reveal_secret_verify, 
          'slasher':slasher_verify, 
          'check_point_slasher':check_point_slasher_verify, 
          'check_point':check_point_verify}####
#------------------------------------------------------
#The following functions are reversible by changing the flag DB['add_block']
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
    if remove != (DB['add_block']):# 'xor' and '!=' are the same.
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
    adjust_int('count', address, 1, DB)
    adjust_int('amount', criminal, custom.pos_reward/3, DB)
    adjust_list('secret_hashes', tx['tx1']['sign_on'], False, tx['secret_hash'], DB)
def check_point(tx, DB):
    address=tools.addr(tx)
    acc=blockchain.db_get(address, DB)
    adjust_int('count', address, 1, DB)
    adjust_int('amount', address, tools.coins2satoshis(custom.check_point_reward*acc['stake']/DB['all_stake'], DB), DB)
def check_point_slasher(tx, DB):
    cp_address=tools.addr(tx['tx'])
    acc=blockchain.db_get(cp_address, DB)
    address=tools.addr(tx)
    adjust_int('count', address, 1, DB)
    adjust_int('amount', address, 3*tools.coins2satoshis(custom.check_point_reward*acc['stake']/DB['all_stake']), DB)
    acc['stake_flag']=not DB['add_block']
    blockchain.db_put(address, acc, DB)

update={'spend':spend,
        'sign':sign,
        'reveal_secret':reveal_secret,
        'slasher':slasher,
        'check_point_slasher':check_point_slasher,
        'check_point':check_point}####
#-----------------------------------------
