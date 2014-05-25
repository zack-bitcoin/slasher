import tools#, hashlib
#This is for easy customization of new currencies.
min_fee=10**6#ignore txs with fee lower than this
database_name='DB.db'
listen_port=8900
gui_port=8700
version="VERSION"
total_coins=21*10**6
initial_money=10**16#total_satoshis
create_block_fee=0.21#in coins
check_point_reward=10#in coins
download_many=500#max number of blocks to request
max_download=50000
check_point_length=5
brainwallet='brain wallet'
privkey=tools.det_hash(brainwallet)
pubkey=tools.privtopub(privkey)
peers=[['localhost', 8900],
       ['localhost', 8901],
       ['localhost', 8902],
       ['localhost', 8903],
       ['localhost', 8904],
       ['localhost', 8905]]

