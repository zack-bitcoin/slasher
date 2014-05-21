import tools#, hashlib
#This is for easy customization of new currencies.
min_fee=10**6#ignore txs with fee lower than this
database_name='DB.db'
listen_port=8900
gui_port=8700
version="VERSION"
initial_money=10**16
create_block_fee=10**8#transaction fees must sum to larger than this
download_many=500#max number of blocks to request
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

