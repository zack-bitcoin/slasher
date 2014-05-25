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
import Add_Block
import Add_Tx

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
    if Add_Tx.verify_tx(tx, DB):
        DB['txs'].append(tx)
    else:
        pass
def orphan_junk(orphans, update, block, DB):
    orphans+=copy.deepcopy(DB['txs'])
    update(block, DB)
    for orphan in sorted(orphans, key=lambda x: x['count']):
        add_tx(orphan, DB)
def add_block(block, DB): return Add_Block.bothchains(DB, add_block_, block)
def add_block_(block, DB):
    # Attempts adding a new block to the blockchain.
    print('attempt to add: ' +str(block))
    if Add_Block.block_check(block, DB):
        print('add_block: ' + str(block))
        orphan_junk([], Add_Block.update, block, DB)
        Add_Block.signature_txs(block, DB)
def delete_block(DB): return add_block.bothchains(DB, delete_block_)
def delete_block_(DB):
    if DB['length'] < 0:
        return
    block = db_get(DB['length'], DB)
    orphan_junk(copy.deepcopy(block['txs']), add_block.downdate, block, DB)
