import tools#, hashlib
#This is for easy customization of new currencies.
#def hash_(x): return hashlib.sha256(x).hexdigest()
database_name='DB.db'
listen_port=8900
gui_port=8700
version="VERSION"
#block_reward=10**5
initial_money=10**16
create_block_fee=10**8#transaction fees must sum to larger than this
#fee=10**3
#history_length=400#how far back in history do
#we look when we use statistics to guess at 
#the current blocktime and difficulty.
download_many=500#max number of blocks to request
#from a peer at the same time.
max_download=50000
brainwallet='brain wallet'
privkey=tools.det_hash(brainwallet)
pubkey=tools.privtopub(privkey)
peers=[['localhost', 8900],
       ['localhost', 8901],
       ['localhost', 8902],
       ['localhost', 8903],
       ['localhost', 8904],
       ['localhost', 8905]]

