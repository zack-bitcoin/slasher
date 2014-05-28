import pt, hashlib, blockchain, custom, copy
from json import dumps as package, loads as unpackage
#def pub2addr(pubkey): return pt.pubtoaddr(pubkey)
def sign(msg, privkey): return pt.ecdsa_sign(msg, privkey)
def verify(msg, sig, pubkey): return pt.ecdsa_verify(msg, sig, pubkey)
def privtopub(privkey): return pt.privtopub(privkey)
def multi_pop(x, l):
    x=copy.deepcopy(x)
    [x.pop(i) for i in l]
    return x
def det_hash(x):#deterministically takes sha256 of dict, list, int, or string
    def det_list(l): return '[%s]' % ','.join(map(det, sorted(l)))
    def det_dict(x): 
        list_=map(lambda p: det(p[0]) + ':' + det(p[1]), sorted(x.items()))
        return '{%s}' % ','.join(list_)
    def det(x): return {list: det_list, dict: det_dict}.get(type(x), str)(x)
    return hashlib.sha256(det(unpackage(package(x)))).hexdigest()
def block_hash(block): return det_hash(multi_pop(block, ['secrets, secret_hashes']))#these lists have to be removed, becuase det_hash 
def tx_hash(tx): return det_hash(multi_pop(tx, ['signatures']))
def base58_encode(num):
    num=int(num, 16)
    alphabet = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    base_count = len(alphabet)
    encode = ''
    if (num < 0): return ''
    while (num >= base_count):
        mod = num % base_count
        encode = alphabet[mod] + encode
        num = num / base_count
    if (num): encode = alphabet[num] + encode
    return encode

secrets = {}
def recent_blockthings(key, DB, start, end, step_size=1):
    # Grabs info from old blocks in range
    storage={}
    if key == 'secret':
        storage = secrets
    def get_val(length):
        leng = str(length)
        if not leng in storage:
            storage[leng] = blockchain.db_get(leng, DB)[key]
        return storage[leng]
    return map(get_val, range(start, end, step_size))
def accumulate(data):
    if len(data)==0: return 0
    if len(data)==1: return data[0]
    return accumulate([data[0]+data[1]]+data[2:])
def sum_fees(block): return accumulate([tx['fee'] if E_check(tx, 'fee', int) else 0 for tx in block['txs']])
def E_check(dic, key, type_):
    if not isinstance(type_, list): type_=[type_]
    if len(type_)==0: return False#to end the recursion.
    if not key in dic: return False
    if isinstance(type_[0], type):
        if not isinstance(dic[key], type_[0]): return E_check(dic, key, type_[1:])
    else:
        if not dic[key] == type_[0]: return E_check(dic, key, type_[1:])
    return True
def target_times_float(target, number):
    a = int(str(target), 16)
    b = int(a * number)
    return str(hex(b))[2: -1]
#n is the number of pubkeys required to spend from this address
def make_address(pubkeys, n): return str(len(pubkeys))+str(n)+base58_encode(det_hash({str(n):pubkeys}))[0:29]
def addr(tx): return make_address(tx['pubkeys'], len(tx['signatures']))
def buffer_(str, size):
    if len(str)<size: return buffer_('0'+str, size)
    return str
def tryPass(func, dic):
    try: func(dic)
    except: pass
def median(mylist):  # the liars don't have 51% hashpower.
    return 0 if len(mylist) < 1 else sorted(mylist)[len(mylist) / 2]
def count_func(address, DB): # Returns the number of transactions that pubkey has broadcast.
    def zeroth_confirmation_txs(address, DB):
        return len(filter(lambda tx: address==addr(tx), DB['txs']))
    current = blockchain.db_get(address, DB)['count']
    return current+zeroth_confirmation_txs(address, DB)
def verify_count(tx, DB): 
    if not E_check(tx, 'count', int): 
        return False
    address=addr(tx)
    if tx['count'] != count_func(address, DB): 
        return False
    return True
def satoshis2coins(satoshis, DB):
    return satoshis*1.0*custom.total_coins/DB['all_money']
def coins2satoshis(coins, DB):
    return int(coins*DB['all_money']/custom.total_coins)
def sign_broadcast_tx(tx_orig, privkey, DB, count_bump=0):
    tx=copy.deepcopy(tx_orig)
    pubkey=privtopub(privkey)
    address=make_address([pubkey], 1)
    tx['count']=count_func(address, DB)+count_bump
    tx['signatures']=[sign(det_hash(tx), privkey)]
    DB['suggested_txs'].append(tx)#maybe this line is bad
    return tx
    #blockchain.add_tx(tx, DB)#maybe this line is better

