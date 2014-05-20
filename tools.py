import pt, hashlib, blockchain
from json import dumps as package, loads as unpackage
#def pub2addr(pubkey): return pt.pubtoaddr(pubkey)
def sign(msg, privkey): return pt.ecdsa_sign(msg, privkey)
def verify(msg, sig, pubkey): return pt.ecdsa_verify(msg, sig, pubkey)
def privtopub(privkey): return pt.privtopub(privkey)
def block_hash(block):
    block=copy.deepcopy(block)
    block.pop('secrets')
    block.pop('secret_hashes')
    return det_hash(block)
def det_hash(x):#deterministically takes sha256 of dict, list, int, or string
    def det_list(l): return '[%s]' % ','.join(map(det, l))
    def det_dict(x): 
        list_=map(lambda p: det(p[0]) + ':' + det(p[1]), sorted(x.items()))
        return '{%s}' % ','.join(list_)
    def det(x): return {list: det_list, dict: det_dict}.get(type(x), str)(x)
    return hashlib.sha256(det(x)).hexdigest()
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
def recent_blockthings(key, DB, start, end):
    # Grabs info from old blocks in range
    storage={}
    if key == 'secret':
        storage = secrets
    def get_val(length):
        leng = str(length)
        if not leng in storage:
            storage[leng] = blockchain.db_get(leng, DB)[key]
        return storage[leng]
    return map(get_val, range(start, end))
def E_check(dic, key, type_):
    if not key in dic: return False
    if isinstance(type_, type):
        if not isinstance(dic[key], type_): return False
    else:
        if not dic[key] == type_: return False
    return True
def target_times_float(target, number):
    print('number: ' +str(number))
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
    if len(mylist) < 1:
        return 0
    return sorted(mylist)[len(mylist) / 2]

