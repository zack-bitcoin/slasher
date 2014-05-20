""" This file explains how we talk to the database. It explains the rules for
    adding blocks and transactions.
"""
import time
import copy
import custom
import tools
import networking
import transactions
import random
import gui

def db_get(n, DB, db='db'):
    n = str(n)
    try:
        return tools.unpackage(DB[db].Get(n))
    except:
        db_put(n, {'count': 0, 'amount': 0, 'secret_hashes':[], 'secrets':[]}, DB, db)  # Everyone defaults with
        # having zero money, and having broadcast zero transcations.
        return db_get(n, DB)
def db_put(key, dic, DB, db='db'): return DB[db].Put(str(key), tools.package(dic))
def db_delete(key, DB, db='db'): return DB[db].Delete(str(key))

def count_func(address, DB): # Returns the number of transactions that pubkey has broadcast.
    def zeroth_confirmation_txs(address, DB):
        def func(t): address == tools.addr(t)
        return len(filter(func, DB['txs']))
    current = db_get(address, DB)['count']
    return current+zeroth_confirmation_txs(address, DB)

def add_tx(tx, DB): # Attempt to add a new transaction into the pool.
    if DB['db']==DB['db_old']: return
    address = tools.addr(tx)
    def verify_count(tx, txs): 
        if not tools.E_check(tx, 'count', int): 
            return False
        if tx['count'] != count_func(address, DB):
            return False
        return True
    def tx_type_check(tx, txs): return not isinstance(tx, dict)
    def type_check(tx, txs):
        if 'type' not in tx:
            return True
        return tx['type'] not in transactions.tx_check
    def too_big_block(tx, txs):
        return len(tools.package(txs+[tx])) > networking.MAX_MESSAGE_SIZE - 5000
    def verify_tx(tx, txs):
        if type_check(tx, txs): 
            print('type')
            return False
        if tx in txs: 
            print('already have')
            return False
        if not verify_count(tx, txs): 
            print('count')
            return False
        if too_big_block(tx, txs): 
            print('too big')
            return False
        if 'start' in tx and DB['length'] < tx['start']: return False
        if 'end' in tx and DB['length'] > tx['end']: return False
        return transactions.tx_check[tx['type']](tx, txs, DB)
    #print('try add tx: ' +str(tx))
    if verify_tx(tx, DB['txs']):
        print('add tx: ' +str(tx))
        DB['txs'].append(tx)
    else:
        print('TX DID NOT GET ADDED: ' +str(tx))
E_check=tools.E_check
def bothchains(DB, func, block):
    func(block, DB)
    print('in bothchains')
    if DB['length']>2000:
        DB['db_new']=DB['db']
        DB['db']=DB['db_old']
        DB['length']-=2000
        old_block=db_get(DB['length'])
        func(old_block, DB)
        DB['db_old']=DB['db']
        DB['db']=DB['db_new']
        DB['length']+=2000
def add_block(block, DB): return bothchains(DB, add_block_, block)
def add_block_(block, DB):
    # Attempts adding a new block to the blockchain.
    # Median is good for weeding out liars, so long as
    def block_check(block, DB):
        if not isinstance(block, dict):
            return False
        if 'error' in block:
            return False
        def accumulate(data):
            if len(data)==0: return 0
            if len(data)==1: return data[0]
            return accumulate([data[0]+data[1]]+data[2:])
        def tx_check(block, DB):
            if not E_check(block, 'txs', list): return False
            start = copy.deepcopy(DB['txs'])
            out = []
            start_copy = []
            while True:
                if start == []:
                    return True  # Block passes this test
                if transactions.tx_check[start[-1]['type']](start[-1], out, DB):
                    out.append(start.pop())
                else: return False  # Block is invalid
        def fee_check(block, DB):
            fees=[tx['fee'] if E_check(tx, 'fee', int) else 0 for tx in block['txs']]
            #print('out of: '+str(block['txs']))
            #print('fees: ' +str(fees))
            return accumulate(fees)>=custom.create_block_fee
        def length_check(block, DB):
            if not E_check(block, 'length', DB['length']+1): return False
            return True
        def reference_previous_block(block, DB):
            if DB['length'] >= 0:#first block is first.
                if tools.det_hash(db_get(DB['length'], DB)) != block['prevHash']:
                    return False
            return True
        def census_check(block, DB):
            census_txs=filter(lambda tx: tx['type']=='census', block['txs'])
            total=accumulate(map(lambda x: blockchain.db_get(tools.addr(x))['amount'], census_txs))
            return total>DB['all_money']*0.4
        tests=[length_check, reference_previous_block, tx_check, fee_check]
        if block['length']%1000==999: tests.append(census_check)
        for test in tests:
            if not test(block, DB): 
                print('failed on test: ' +str(test))
                return False
        return True
    def update(block, DB):
        db_put(block['length'], block, DB)
        DB['length'] = block['length']
        DB['txs'] = []
        for tx in block['txs']:
            DB['add_block']=True
            transactions.update[tx['type']](copy.deepcopy(tx), DB)
    print('trying to add: ' +str(block))
    if block_check(block, DB):
        print('add_block: ' + str(block))
        orphans = copy.deepcopy(DB['txs'])
        update(block, DB)
        secret=str(random.random())
        tx={'type':'sign', 'secret_hash':tools.make_address([secret], 1), 'pubkeys':[custom.pubkey], 'sign_on':DB['length']-3}
        #tx['signatures']=[tools.sign(tools.det_hash(tx), custom.privkey)]
        #print('making sign tx: ' +str(tx))
        gui.easy_add_transaction(tx, custom.privkey, DB)
        for tx in orphans:
            add_tx(tx, DB)
def delete_block(DB): return bothchains(DB, delete_block_)
def delete_block_(DB):
    if DB['length'] < 0:
        return
    block = db_get(DB['length'], DB)
    orphans = copy.deepcopy(DB['txs'])+block['txs']
    DB['txs'] = []
    for tx in block['txs']:
        DB['add_block']=False
        transactions.update[tx['type']](copy.deepcopy(tx), DB)
    db_delete(DB['length'], DB)
    DB['length'] -= 1
    for orphan in sorted(orphans, key=lambda x: x['count']):
        add_tx(orphan, DB)
