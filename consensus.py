""" This file mines blocks and talks to peers. It maintains consensus of the
    blockchain.
"""
import blockchain
import custom
import tools
import networking
import random
import time
import copy
import gui

# Tries to mine the next block hashes_till_check many times.
def make_block(pubkey, DB):
    length = DB['length']
    out = {'version': custom.version,
           'secret_hashes':[],
           'secrets':[],
           'txs': DB['txs'],
           'length': length+1}
    if length>=0:
        prev_block = blockchain.db_get(length, DB)
        out['prevHash']=tools.det_hash(prev_block)
    out = tools.unpackage(tools.package(out))
    return out
def peers_check(dic):
    # Check on the peers to see if they know about more blocks than we do.
    peers=dic['peers']
    DB=dic['DB']
    def peer_check(peer, DB):
        #print('check peer: '+str(peer))
        def cmd(x):
            return networking.send_command(peer, x)
        def download_blocks(peer, DB, peers_block_count, length):
            def fork_check(newblocks, DB):
                length = copy.deepcopy(DB['length'])
                block = blockchain.db_get(length, DB)
                recent_hash = tools.det_hash(block)
                their_hashes = map(tools.det_hash, newblocks)
                return recent_hash not in map(tools.det_hash, newblocks)
            def bounds(length, peers_block_count, DB):
                if peers_block_count['length'] - length > custom.download_many:
                    end = length + custom.download_many - 1
                else:
                    end = peers_block_count['length']
                return [max(length - 2, 0), end]
            blocks = cmd({'type': 'rangeRequest',
                          'range': bounds(length, peers_block_count, DB)})
            if type(blocks) != type([1, 2]):
                return []
            for i in range(2):  # Only delete a max of 2 blocks, otherwise a
                # peer might trick us into deleting everything over and over.
                if fork_check(blocks, DB):
                    blockchain.delete_block(DB)
            DB['suggested_blocks']+=blocks
            return
        def ask_for_txs(peer, DB):
            txs = cmd({'type': 'txs'})
            print('txs: ' +str(txs))
            for tx in txs:
                DB['suggested_txs'].append(tx)
            pushers = [x for x in DB['txs'] if x not in txs]
            for push in pushers:
                cmd({'type': 'pushtx', 'tx': push})
            return []
        def give_block(peer, DB, block_count):
            cmd({'type': 'pushblock',
                 'block': blockchain.db_get(block_count['length'] + 1, DB)})
            return []
        block_count = cmd({'type': 'blockCount'})
        print('block count: ' +str(block_count))
        if type(block_count) != type({'a': 1}):
            return
        if 'error' in block_count.keys():
            print('error 2')
            return
        length = DB['length']
        us = DB['sigLength']
        them = block_count['sigLength']
        if them < us:
            return give_block(peer, DB, block_count)
        if us == them:
            return ask_for_txs(peer, DB)
        return download_blocks(peer, DB, block_count, length)
    for peer in peers:
        peer_check(peer, DB)
def suggestions(DB):
    [blockchain.add_tx(tx, DB) for tx in DB['suggested_txs']]
    DB['suggested_txs'] = []
    [blockchain.add_block(block, DB) for block in DB['suggested_blocks']]
    DB['suggested_blocks'] = []
def mainloop(peers, DB):
    while True:
        peers_check({'peers':peers, 'DB':DB})
        tools.tryPass(suggestions, DB)
        time.sleep(2)
