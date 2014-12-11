import transactions, tools, custom, time, sys, api, random
def create_sign_tx():
    on_block=tools.local_get('length')+1
    r=transactions.det_random(on_block)
    jackpots=[]
    address=tools.local_get('address')
    B=tools.db_get(address)['amount']
    M=custom.all_money
    for j in range(custom.jackpot_nonces):
        if transactions.winner(B, M, r, address, j):
            jackpots.append(j)
    if len(jackpots)>0:
        #proot=get_proof(on_block)
        proof=tools.db_proof(address)
        a=tools.local_get('balance_proofs')
        proof=a[max(on_block-custom.long_time, 0)]
        tx={'on_block':on_block, 'proof':proof, 'jackpots':jackpots, 'type':'sign', 'amount':M/3000/3}
        secret=str(random.random())+str(random.random())
        secrets=tools.local_get('secrets')
        secrets[str(on_block)]=secret
        tools.local_put('secrets', secrets)
        tx['secret_hash']=tools.det_hash(secret)
        if on_block>0:
            tx['prev']=tools.db_get(on_block-1)['block_hash']
    else:
        tx= {'error':'no jackpots'}
    tx['entropy']=random.randint(0,1)
    return tx
#first off, I need to collect a proof of how much money I had at every single block. Deal with jackpots in a seperate thread.
def mainloop():
    while True:
        time.sleep(2)
        txs=tools.local_get('txs')
        address=tools.local_get('address')
        txs=filter(lambda x: address==tools.addr(x), txs)
        txs=filter(lambda x: x['type']=='sign', txs)
        if len(txs)==0:
            api.easy_add_transaction(create_sign_tx())
        else:
            time.sleep(0.1)

