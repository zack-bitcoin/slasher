import copy, tools, blockchain, custom, http_server, consensus
#the easiest way to understand this file is to try it out and have a look at 
#the html it creates. It creates a very simple page that allows you to spend 
#money.
def make_block(pubkey, privkey, DB):
    tx={'type':'spend', 'pubkeys':[pubkey], 'to':'none', 'amount':0, 'fee':10**8, 'count':blockchain.count_func(tools.make_address([custom.pubkey], 1), DB)}
    easy_add_transaction(tx, privkey, DB)
    block=consensus.make_block(pubkey, DB)
    blockchain.add_block(block, DB)

def spend(amount, pubkey, privkey, to_pubkey, DB):
    amount=int(amount*(10**5))
    tx={'type':'spend', 'pubkeys':[pubkey], 'amount':amount, 'to':to_pubkey, 'fee':0}
    easy_add_transaction(tx, privkey, DB)

def easy_add_transaction(tx_orig, privkey, DB):
    tx=copy.deepcopy(tx_orig)
    pubkey=tools.privtopub(privkey)
    address=tools.make_address([pubkey], 1)
    try:
        tx['count']=blockchain.count_func(address, DB)
    except:
        tx['count']=1
    tx['signatures']=[tools.sign(tools.det_hash(tx), privkey)]
    blockchain.add_tx(tx, DB)

submit_form='''
<form name="first" action="{}" method="{}">
<input type="submit" value="{}">{}
</form> {}
'''
empty_page='<html><body>{}</body></html>'

def easyForm(link, button_says, moreHtml='', typee='post'):
    a=submit_form.format(link, '{}', button_says, moreHtml, "{}")
    if typee=='get':
        return a.format('get', '{}')
    else:
        return a.format('post', '{}')

linkHome = easyForm('/', 'HOME', '', 'get')

def page1(brainwallet=custom.brainwallet):
    out=empty_page
    txt='<input type="text" name="BrainWallet" value="{}">'
    out=out.format(easyForm('/home', 'Play Go!', txt.format(brainwallet)))
    return out.format('')

def home(DB, dic):
    if 'BrainWallet' in dic:
        dic['privkey']=tools.det_hash(dic['BrainWallet'])
    elif 'privkey' not in dic:
        return "<p>You didn't type in your brain wallet.</p>"
    privkey=dic['privkey']
    pubkey=tools.privtopub(dic['privkey'])
    address=tools.make_address([pubkey], 1)
    if 'do' in dic.keys():
        if dic['do']=='make_block':
            make_block(pubkey, privkey, DB)
        if dic['do']=='spend':
            spend(float(dic['amount']), pubkey, privkey, dic['to'], DB)
    out=empty_page
    out=out.format('<p>your address: ' +str(address)+'</p>{}')
    out=out.format('<p>current block: ' +str(DB['length'])+'</p>{}')
    balance=blockchain.db_get(address, DB)['amount']
    for tx in DB['txs']:
        if tx['type'] == 'spend' and tx['to'] == address:
            if tools.E_check(tx, 'fee', int): balance -= tx['fee']
            balance += tx['amount']
        if tx['type'] == 'spend' and tx['pubkeys'][0] == pubkey:
            balance -= tx['amount']
    out=out.format('<p>current balance is: ' +str(balance/100000.0)+'</p>{}')
    if balance>0:
        out=out.format(easyForm('/home', 'spend money', '''
        <input type="hidden" name="do" value="spend">
        <input type="text" name="to" value="address to give to">
        <input type="text" name="amount" value="amount to spend">
        <input type="hidden" name="privkey" value="{}">'''.format(privkey)))    
    if balance>=10**8:
        out=out.format(easyForm('/home', 'make block', '''
        <input type="hidden" name="do" value="make_block">
        <input type="hidden" name="privkey" value="{}">'''.format(privkey)))    
    txt='''    <input type="hidden" name="privkey" value="{}">'''
    s=easyForm('/home', 'Refresh', txt.format(privkey))
    return out.format(s)

def hex2htmlPicture(string, size):
    txt='<img height="{}" src="data:image/png;base64,{}">{}'
    return txt.format(str(size), string, '{}')

def main(port, brain_wallet, db):
    global DB
    DB = db
    ip = ''
    def post(dic): return home(DB, dic)
    def get(dic): return page1(DB, dic)
    http_server.serve(port, page1, post)

