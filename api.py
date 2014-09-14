"""This is the internal API for slashershell. These are the words that are used to interact with the blockchain.
"""
import copy, tools, blockchain, custom, random, transactions, sys, txs_tools, time, networking, blockchain
def sign_tx(tx_orig, DB):
    tx = copy.deepcopy(tx_orig)
    if 'pubkeys' not in tx:
        tx['pubkeys']=[DB['pubkey']]
    try:
        tx['count'] = tools.count(DB['address'], DB)
    except:
        tx['count'] = 1
    tx['signatures'] = [tools.sign(tools.det_hash(tx), DB['privkey'])]
    return tx
def easy_add_transaction(tx_orig, DB):
    tx = copy.deepcopy(tx_orig)
    tx=sign_tx(tx, DB)
    return(blockchain.add_tx(tx, DB))
def help_(DB):      
    tell_about_command={
        'help':'type "./slasherd.py help <cmd>" to learn about <cmd>. type "./slasherd.py commands" to get a list of all slashershell commands',
        'commands':'returns a list of the slashershell commands',
        'info':'prints the contents of an entree in the hashtable. If you want to know what the first block was: info 0, if you want to know about a particular address <addr>: info <addr>, if you want to know about yourself: info my_address',
        'times':'for example "times 4 info my_address" would be the same as running "info my_address" 4 times in a row',
        'info2':'prints the contents of an entree in the hashtable in the database from 2000 blocks ago. If you want to know what the first block was: info 0, if you want to know about a particular address <addr>: info <addr>, if you want to know about yourself: info my_address',
        'my_address':'tells you your own address',
        'spend':'spends money, in satoshis, to an address <addr>. Example: spend 1000 11j9csj9802hc982c2h09ds',
        'blockcount':'returns the number of blocks since the genesis block',
        'txs':'returns a list of the zeroth confirmation transactions that are expected to be included in the next block',
        'my_balance':'the amount of slashercoin that you own',
        'balance':'if you want to know the balance for address <addr>, type: ./slasherd.py balance <addr>',
        'log':'records the following words into the file "log.py"',
        'stop':'This is the correct way to stop slashercoin. If you turn off in any other way, then you are likely to corrupt your database, and you have to redownload all the blocks again.',
        'DB':'returns a database of information that is shared between threads'
    }
    if len(DB['args'])==0:
        return("needs 2 words. example: 'help help'")
    try:
        return tell_about_command[DB['args'][0]]    
    except:
        return(str(DB['args'][0])+' is not yet documented')
def DB_print(DB):
    return(str(DB))
def info(DB): 
    if len(DB['args'])<1:
        return ('not enough inputs')
    if DB['args'][0]=='my_address':
        address=DB['address']
    else:
        address=DB['args'][0]
    return(str(tools.db_get(address, DB)))   
def info2(DB): 
    if len(DB['args'])<1:
        return ('not enough inputs')
    if DB['args'][0]=='my_address':
        address=DB['address']
    else:
        address=DB['args'][0]
    return(str(blockchain.old_chain(lambda DB: tools.db_get(address, DB), DB)))
def my_address(DB):
    return(str(DB['address']))
def accumulate_words(l, out=''):
    if len(l)>0: return accumulate_words(l[1:], out+' '+l[0])
    return out
def blockcount(DB): return(str(DB['length']))
def txs(DB):        return(str(DB['txs']))
def my_balance(DB, address='default'): 
    if address=='default':
        address=DB['address']
    return(str(tools.db_get(address, DB)['amount']-txs_tools.cost_0(DB['txs'], DB)))
def balance(DB): 
    if len(DB['args'])<1:
        return('what address do you want the balance for?')
    return(str(my_balance(DB, DB['args'][0])))
def log(DB): tools.log('FROM SHELL: ' + str(accumulate_words(DB['args'])[1:]))
def stop_(DB): 
    DB['stop']=True
    return('turning off all threads')
def commands(DB): return str(Do.keys())
def spend(DB): 
    if len(DB['args'])<2:
        return('not enough inputs')
    return easy_add_transaction({'type': 'spend', 'amount': int(DB['args'][0]), 'to':DB['args'][1]}, DB)
def buy_block(DB):
    prev_block=tools.db_get(DB['length'], DB)
    block=tools.default_block(DB['length']+1, DB, DB['sig_length']+len(filter(lambda tx: tx['type']=='sign', DB['txs'])), DB['txs'])
    if DB['length']>=0:
        to_hash=prev_block['rand_nonce']+tools.package(block['txs'])
    else:
        to_hash=prev_block['txs']
    block['rand_nonce']=tools.det_hash(to_hash)
    block=sign_tx(block, DB)
    block = tools.unpackage(tools.package(block))
    DB['suggested_blocks'].put(block)
    return block
'''
def times(DB):
    if len(DB['args'])<2:
        return('not enough inputs')
    command=DB['args'][1]
    times=DB['args'][0]
    DB['args']=DB['args'][2:]
    out=''
    for i in range(int(times)):
        try:
            out+=str(Do[command](DB))+'\n'
        except:
            out+='error while running command in loop: ' +str(sys.exc_info())+'\n'
    return out
'''
Do={'spend':spend, 'help':help_, 'blockcount':blockcount, 'txs':txs, 'balance':balance, 'my_balance':my_balance, 'b':my_balance, 'info':info, 'info2':info2, '':(lambda DB: ' '), 'DB':DB_print, 'my_address':my_address, 'log':log, 'stop':stop_, 'commands':commands, 'buy_block':buy_block}
def main(DB, heart_queue):
    def responder(dic):
        command=dic['command']
        if command[0] in Do: 
            DB['args']=command[1:]
            try:
                out=Do[command[0]](DB)
            except:
                out='error while running command: ' + str(sys.exc_info())
        else: 
            out=str(command[0]) + ' is not a command. use "./slasherd.py commands" to get the list of slashershell commands. use "./slasherd.py help help" to learn about the help tool.'
        return out
    try:
        return networking.serve_forever(custom.slasherd_port, responder, heart_queue, DB)
    except:
        tools.log('api error: ' +str(sys.exc_info()))
