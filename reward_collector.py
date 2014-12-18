import api, custom, tools, time, random

def create_reward_tx():
    tx={}
    tx['type']='reward'
    length=tools.local_get('length')
    tx['on_block']=length-custom.long_time+random.randint(-custom.medium_time/2, custom.medium_time/2)
    if tx['on_block']<=0:
        time.sleep(1)
        return {'error':'no rewards to collect'}
    txs=tools.db_get(tx['on_block'])['txs']
    txs=filter(lambda t: t['type']=='sign', txs)
    address=tools.local_get('address')
    tools.log('on block: ' +str(tx['on_block']))
    sign_tx=filter(lambda t: tools.addr(t)==address, txs)[0]
    relative_reward=tools.relative_reward(tx['on_block'], address)
    
    tx['amount']=relative_reward+sign_tx['amount']
    return tx
def mainloop():
    while True:
        time.sleep(1)
        tx=create_reward_tx()
        if 'error' not in tx:
            tools.log('reward collector tx: ' +str(tx))
            api.easy_add_transaction(tx)
def doit():
    try:
        mainloop()
    except Exception as exc:
        tools.log('reward collector error')
        tools.log(exc)
        
