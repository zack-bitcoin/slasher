import transactions, tools, custom, time, sys, api, random
def create_sign_tx():
    on_block=tools.local_get('length')+1
    if on_block==0:
        time.sleep(1)
        return{'error':'not ready'}
    r=tools.det_random(on_block)
    jackpots=[]
    address=tools.local_get('address')
    #B=tools.db_get(address)['amount']#we should be looking into history instead.
    #we need to grab the proof from our local
    l=max(-1, on_block-1-(custom.long_time*2-custom.medium_time))
    election_block=tools.db_get(l+1)
    proof=tools.local_get('balance_proofs'+str(l))
    a=tools.db_verify(election_block['root_hash'], address, proof)
    B=a['amount']
    #tools.log('CREATE TX a: ' +str(a))
    M=custom.all_money
    for j in range(custom.jackpot_nonces):
        if tools.winner(B, M, r, address, j):
            jackpots.append(j)
    if len(jackpots)>0:
        #proot=get_proof(on_block)
        #proof=tools.db_proof(address)
        tx={'on_block':on_block, 'jackpots':jackpots, 'type':'sign', 'amount':M/3000/3}
        tx['B']=B
        tx['proof']=proof
        if proof=='empty':
            time.sleep(1)
            return {'error':'not ready'}
        secret=str(random.random())+str(random.random())
        secrets=tools.local_get('secrets')
        secrets[str(on_block)]=secret
        tools.local_put('secrets', secrets)
        tx['secret_hash']=tools.det_hash(secret)
        if on_block>0:
            tx['prev']=tools.db_get(on_block-1)['block_hash']
    else:
        tx= {'error':'no jackpots'}
    #tx['entropy']=random.randint(0,1)
    return tx
#first off, I need to collect a proof of how much money I had at every single block. Deal with jackpots in a seperate thread.
def mainloop():
    while True:
        time.sleep(0.5)
        txs=tools.local_get('txs')
        address=tools.local_get('address')
        txs=filter(lambda x: address==tools.addr(x), txs)
        txs=filter(lambda x: x['type']=='sign', txs)
        if len(txs)==0:
            tx=create_sign_tx()
            #tools.log('tx: ' +str(tx))
            api.easy_add_transaction(tx)
        else:
            time.sleep(0.1)

