""" This file explains explains the rules for adding and removing blocks from the local chain.
"""
import time
import copy
import custom
import networking
import transactions
import sys
import tools
import txs_tools
import multiprocessing
def add_tx(tx, DB):
    out=['']
    if type(tx) != type({'a':1}): 
        return False
    address = tools.make_address(tx['pubkeys'], len(tx['signatures']))
    def verify_count(tx, txs):
        return tx['count'] != tools.count(address, DB)
    def type_check(tx, txs):
        if not tools.E_check(tx, 'type', [str, unicode]):
            out[0]+='blockchain type'
            return False
        if tx['type'] not in transactions.tx_check:
            out[0]+='bad type'
            return False
        return True
    def too_big_block(tx, txs):
        return len(tools.package(txs+[tx])) > networking.MAX_MESSAGE_SIZE - 5000
    def verify_tx(tx, txs, out):
        if not type_check(tx, txs):
            out[0]+='type error'
            return False
        if tx in txs:
            out[0]+='no duplicates'
            return False
        if verify_count(tx, txs):
            out[0]+='count error'
            return False
        if too_big_block(tx, txs):
            out[0]+='too many txs'
            return False
        if not transactions.tx_check[tx['type']](tx, txs, DB):
            out[0]+='update transactions.py to find out why. print statements are no good. ' +str(tx)
            return False
        return True
    if verify_tx(tx, DB['txs'], out):
        DB['txs'].append(tx)
        return('added tx: ' +str(tx))
    else:
        return('failed to add tx because: '+out[0])
def add_block(block_pair, DB):
    """Attempts adding a new block to the blockchain."""
    if DB['length']<-1: return False
    def block_check(block, DB):
        def tx_check(txs):
            start = copy.deepcopy(txs)
            out=[]
            while len(start)>0:
                if transactions.tx_check[start[-1]['type']](start[-1], out, DB):
                    out.append(start.pop())
                else:
                    tools.log('bad block-tx error: '+str(start[-1]))
                    tools.log('in block: ' +str(block_pair))
                    return True
            return False
        if not isinstance(block, dict):
            tools.log('bad block is not dict')
            return False
        if 'error' in block:
            tools.log('bad block error error')
            return False
        if 'length' not in block:
            tools.log('no length')
            return False
        length = DB['length']
        if int(block['length']) != int(length) + 1:
            tools.log('block: ' +str(block))
            tools.log('length: ' +str(length))
            tools.log('wrong length')
            return False
        if length >= 0:
            prev_block=tools.db_get(DB['length'], DB)
            if block['rand_nonce']!=tools.det_hash(prev_block['rand_nonce']+tools.package(block['txs'])):
                tools.log('does not refernce previous block')
                return False
        if tx_check(block['txs']):
            tools.log('fails on a tx')
            return False
        #should fail if the creator of the block cannot afford it
        return True
    if type(block_pair)==type([1,2,3]):
        block=block_pair[0]
        peer=block_pair[1]
    else:
        block=block_pair
        peer=False
    if block_check(block, DB):
        if peer != False:
            talk_to_this_peer_more_frequently(peer)
        orphans = copy.deepcopy(DB['txs'])
        DB['txs'] = []
        update_chain(block, DB)
        txs_tools.adjust_int(['amount'], tools.addr(block), -custom.block_fee, DB)
        if DB['length']>=2000:
            old_block=tools.db_get(DB['length']-2000, DB)
            old_chain(lambda DB: update_chain(old_block, DB), DB)
        for tx in orphans:
            add_tx(tx, DB)
def old_chain(f, DB):
    #if DB['length']<2000:
    #    return({'error', 'not long enough yet'})
    l=multiprocessing.Lock()
    l.acquire()
    DB['db_new']=DB['db']
    DB['db']=DB['old_db']
    DB['length']-=2000
    try:
        out=f(DB)
    except:
        out={'error':'old chain error'}
    DB['old_db']=DB['db']
    DB['db']=DB['db_new']
    DB['length']+=2000
    l.release()
    return out
def talk_to_this_peer_more_frequently(peer):
    i=0
    j='empty'
    for p in DB['peers_ranked']:
        if p[0]==peer:
            j=i
        i+=1
    if j!='empty':
        DB['peers_ranked'][j][1]*=0.1#listen more to people who have newer blocks.
    else:
        #maybe this peer should be added to our list of peers?
        pass
def update_chain(block, DB):
    tools.db_put(block['length'], block, DB)
    #take money away from the person who created the block
    '''
    if block['length']!=DB['length']+1:
        print('block: ' +str(block))
        print('DB: ' +str(DB))
        print('bool: ' +str(block['length']!=DB['length']+1))
        print('first: ' +str(block['length']))
        print('second: ' +str(DB['length']+1))
        print('first: ' +str(type(block['length'])))
        print('second: ' +str(type(DB['length']+1)))
        error('here')
    '''
    for tx in block['txs']:
        DB['add_block']=True
        transactions.update[tx['type']](tx, DB)
    DB['length'] = block['length']
def downdate_chain(DB):
    #give money to the person who created the block
    block=tools.db_get(DB['length'], DB)
    for tx in block['txs']:
        orphans.append(tx)
        DB['add_block']=False
        transactions.update[tx['type']](tx, DB)
    tools.db_delete(DB['length'], DB)
    DB['length'] -= 1
def delete_block(DB):
    """ Removes the most recent block from the blockchain. """
    if DB['length'] < 0:
        return
    block = tools.db_get(DB['length'], DB)
    orphans = copy.deepcopy(DB['txs'])
    DB['txs'] = []
    if DB['length']>=2000:
        old_chain(lambda DB: downdate_chain(DB), DB)
    downdate_chain(DB)
    #bothchains(DB, downdate_chain, block)
    txs_tools.adjust_int(['amount'], tools.addr(block), -custom.block_fee, DB)
    for orphan in sorted(orphans, key=lambda x: x['count']):
        add_tx(orphan, DB)
def suggestions(DB, s, f):
    while True:
        DB['heart_queue'].put(s)
        for i in range(100):
            time.sleep(0.01)
            if DB['stop']: return
            if not DB[s].empty():
                try:
                    f(DB[s].get(False), DB)
                except:
                    tools.log('suggestions ' + s + ' '+str(sys.exc_info()))
def suggestion_txs(DB): 
    return suggestions(DB, 'suggested_txs', add_tx)
def suggestion_blocks(DB): 
    return suggestions(DB, 'suggested_blocks', add_block)
