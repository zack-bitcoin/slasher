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
def make_block(pubkey, DB, bonus_txs=[]):
    length = DB['length']
    out = {'version': custom.version,
           'secret_hashes':[],
           'secrets':[],
           'txs': DB['txs']+bonus_txs,
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
            print('DOWNLOAD BLOCKS')
            def fork_check(hashes, DB):
                length = copy.deepcopy(DB['length'])
                block = blockchain.db_get(length, DB)
                recent_hash = tools.det_hash(block)
                return recent_hash not in hashes
            def bounds(length, peers_block_count, DB):
                if peers_block_count['length'] - length > custom.download_many:
                    end = length + custom.download_many - 1
                else:
                    end = peers_block_count['length']
                return [max(length - 2, 0), end]
            try: blocks = cmd({'type': 'rangeRequest',
                          'range': bounds(length, peers_block_count, DB)})
            except: blocks=[]
            if type(blocks) != type([1, 2]):
                return []
            hashes = map(tools.det_hash, blocks)                
            for i in range(2):  # Only delete a max of 2 blocks, otherwise a
                # peer might trick us into deleting everything over and over.
                print('ABOUT TO FORK CHECK')
                if fork_check(hashes, DB):
                    print('PASSED FORK CHECK')
                    blockchain.delete_block(DB)
                else:
                    print('DID NOT PASS FORK CHECK')
            DB['suggested_blocks']+=blocks
            return
        def ask_for_txs(peer, DB):
            try: txs = cmd({'type': 'txs'})
            except: return []
            print('txs: ' +str(txs))
            for tx in txs:
                DB['suggested_txs'].append(tx)
            pushers = [x for x in DB['txs'] if x not in txs]
            for push in pushers:
                try: cmd({'type': 'pushtx', 'tx': push})
                except: pass
            return []
        def give_block(peer, DB, block_count):
            try: cmd({'type': 'pushblock',
                 'block': blockchain.db_get(block_count['length'] + 1, DB)})
            except: pass
            return []
        try: block_count = cmd({'type': 'blockCount'})
        except: block_count=[]
        if type(block_count) != type({'a': 1}):
            return
        if 'error' in block_count.keys():
            print('error 2')
            return
        length = DB['length']
        us = DB['sigLength']#-(DB['length']*1.0/1000)
        them = block_count['sigLength']#-(block_count['length']*1.0/1000)
        print('US THEM: ' +str(us)+ ' ' + str(them))
        if them < us:
            print('GIVE BLOCK')
            return give_block(peer, DB, block_count)
        if us == them:
            print('EQUAL')
            return ask_for_txs(peer, DB)
        print('ASK FOR BLOCKS')
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
        #tools.tryPass(peers_check, {'peers':peers, 'DB':DB})
        #tools.tryPass(suggestions, DB)
        suggestions(DB)
#        try: print('BLOCKCHAIN: ' +str(blockchain.db_get('0', DB)))
#        except: pass
        time.sleep(2)
