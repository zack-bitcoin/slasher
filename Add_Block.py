import custom, tools, transactions, copy, blockchain, random
def tx_check(block, DB):
    if not tools.E_check(block, 'txs', list): return False
    start = copy.deepcopy(DB['txs'])
    out = []
    start_copy = []
    while True:
        if start == []: return True  # Block passes this test
        if transactions.tx_check[start[-1]['type']](start[-1], out, DB):
            out.append(start.pop())
        else: 
            return False  # Block is invalid
def fee_check(block, DB): 
    return tools.sum_fees(block)>=tools.coins2satoshis(custom.create_block_fee, DB)
def length_check(block, DB): return tools.E_check(block, 'length', DB['length']+1) 
def reference_previous_block(block, DB):
    if DB['length'] >= 0:#first block is first.
        if tools.det_hash(blockchain.db_get(DB['length'], DB)) != block['prevHash']:
            return False
    return True
def check_point_check(block, DB):
    check_point_txs=filter(lambda tx: tx['type']=='check_point', block['txs'])
    def acc(x): return blockchain.db_get(tools.addr(x), DB)
    check_point_txs=filter(lambda tx: acc(tx)['stake_flag'], check_point_txs)
    total=tools.accumulate(map(lambda x: acc(x)['stake'], check_point_txs))
    return total>DB['all_stake']*0.666

Tests=[length_check, reference_previous_block, tx_check, fee_check]

def update(block, DB):
    blockchain.db_put(block['length'], block, DB)
    DB['length'] = block['length']
    DB['txs'] = []
    for tx in block['txs']:
        DB['add_block']=True
        transactions.update[tx['type']](copy.deepcopy(tx), DB)
def downdate(block, DB):
    DB['txs'] = []
    for tx in block['txs']:
        DB['add_block']=False
        transactions.update[tx['type']](copy.deepcopy(tx), DB)
    blockchain.db_delete(DB['length'], DB)
    DB['length'] -= 1

def signature_txs(block, DB):
    secret=str(random.random())
    for i in range(5):
        tx={'type':'sign', 'secret_hash':tools.make_address([secret], 1), 'pubkeys':[custom.pubkey], 'sign_on':DB['length']-(5+i)}
        tools.sign_broadcast_tx(tx, custom.privkey, DB)
    if check_point_p(DB):
        tx={'type':'check_point', 'sign_on':DB['length']+1, 'pubkeys':[custom.pubkey]}
        if DB['length']>custom.check_point_length:
            tx['prev_check_point_hash']=blockchain.db_get(block['length']+2-custom.check_point_length, DB)['prevHash']
        tools.sign_broadcast_tx(tx, custom.privkey, DB, 1)

def block_check(block, DB):
    if not isinstance(block, dict): return False
    if 'error' in block: return False
    tests=copy.deepcopy(Tests)
    if check_point_p(DB):
        tests.append(check_point_check)
        tests.remove(fee_check)
    for test in tests:
        if not test(block, DB): 
            return False
    return True
def bothchains(DB, func, block):
    func(block, DB)
    if DB['length']>2000:
        DB['db_new']=DB['db']
        DB['db']=DB['db_old']
        DB['length']-=2000
        old_block=blockchain.db_get(DB['length'])
        func(old_block, DB)
        DB['db_old']=DB['db']
        DB['db']=DB['db_new']
        DB['length']+=2000
