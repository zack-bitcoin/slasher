import trie, rlp
from json import dumps as package, loads as unpackage

state=trie.Trie('db', trie.BLANK_ROOT)
def get(key): return unpackage(rlp.decode(state.get(key)))
def put(key, val): return state.update(key, rlp.encode(package(val)))
def delete(key):  return state.delete(key)
def root(key):  return state.root_hash.encode('hex')
def prove(key): return state.produce_spv_proof(key)
def verify(root, key, proof): return trie.verify_spv_proof(root.decode('hex'), key, proof)

def test():
    put('a', 123)
    print(get('a'))
    a=prove('a')
    print('proof a: ' +str(a))
    print('verify: ' +str(verify(root('a'), 'a', a)))

