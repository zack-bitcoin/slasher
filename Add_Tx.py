import tools, transactions, networking
def type_check(tx, txs):
    if not tools.E_check(tx, 'type', [str, unicode]): return False
    if tx['type'] not in transactions.tx_check: return False
    return True
def too_big_block(tx, txs):
    return len(tools.package(txs+[tx])) > networking.MAX_MESSAGE_SIZE - 5000
def verify_tx(tx, DB):
    txs=DB['txs']
    if not type_check(tx, txs): return False
    if len(filter(lambda t: tools.addr(t)==tools.addr(tx), 
                  filter(lambda t: t['count']==tx['count'], txs)))>0: 
        #no repeated tx in same block.
        return False
    if not tools.verify_count(tx, DB): 
        address=tools.addr(tx)
        #print('count'+str(tools.count_func(address, DB)))
        return False
    if too_big_block(tx, txs): return False
    if 'start' in tx and DB['length'] < tx['start']: return False
    if 'end' in tx and DB['length'] > tx['end']: return False
    return transactions.tx_check[tx['type']](tx, txs, DB)
