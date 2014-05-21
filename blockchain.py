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

def add_tx(tx, DB): # Attempt to add a new transaction into the pool.
    if DB['db']==DB['db_old']: return
    address = tools.addr(tx)
    def type_check(tx, txs):
        if not tools.E_check(tx, 'type', str): return False
        if tx['type'] not in transactions.tx_check: return False
        return True
    def too_big_block(tx, txs):
        return len(tools.package(txs+[tx])) > networking.MAX_MESSAGE_SIZE - 5000
    def verify_tx(tx, DB):
        txs=DB['txs']
        if not type_check(tx, txs): 
            print('type')
            return False
        if len(filter(lambda t: tools.addr(t)==tools.addr(tx), 
                      filter(lambda t: t['count']==tx['count'], txs)))>0:
            print('already have')
            return False
        if not tools.verify_count(tx, DB): 
            print('tx: ' +str(tx))
            print('DB: ' +str(DB))
            print('count')
            return False
        if too_big_block(tx, txs): 
            print('too big')
            return False
        if 'start' in tx and DB['length'] < tx['start']: return False
        if 'end' in tx and DB['length'] > tx['end']: return False
        return transactions.tx_check[tx['type']](tx, txs, DB)
    if verify_tx(tx, DB):
        print('add tx: ' +str(tx))
        DB['txs'].append(tx)
    else:
        print('TX DID NOT GET ADDED: ' +str(tx))
def bothchains(DB, func, block):
    func(block, DB)
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
        def tx_check(block, DB):
            if not tools.E_check(block, 'txs', list): return False
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
            '''
            print('in fee check')
            print('sumfees: ' +str(tools.sumFees(block)))
            print('convert: ' +str(tools.coins2satoshis(custom.create_block_fee, DB)))
            print('block: ' +str(block))'''
            return tools.sumFees(block)>=tools.coins2satoshis(custom.create_block_fee, DB)
        def length_check(block, DB):
            if not tools.E_check(block, 'length', DB['length']+1): return False
            return True
        def reference_previous_block(block, DB):
            if DB['length'] >= 0:#first block is first.
                if tools.det_hash(db_get(DB['length'], DB)) != block['prevHash']:
                    return False
            return True
        def census_check(block, DB):
            census_txs=filter(lambda tx: tx['type']=='census', block['txs'])
            total=tools.accumulate(map(lambda x: blockchain.db_get(tools.addr(x))['amount'], census_txs))
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
    if block_check(block, DB):
        print('add_block: ' + str(block))
        orphans = copy.deepcopy(DB['txs'])
        update(block, DB)
        secret=str(random.random())
        tx={'type':'sign', 'secret_hash':tools.make_address([secret], 1), 'pubkeys':[custom.pubkey], 'sign_on':DB['length']-3}
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
