"""This is to make magic numbers easier to deal with."""
import multiprocessing, os
peers = [['192.241.212.114', 7900]]#,['69.164.196.239', 8900]]
current_loc=os.path.dirname(os.path.abspath(__file__))
database_name = os.path.join(current_loc, 'DB')
log_file=os.path.join(current_loc, 'log')
port=7900
api_port=7899
database_port=7898
version = "0.0001"
all_money=21*10**15
creator='115nxUddLmxijWskiz5znHxk1KdMZpS'
max_key_length=6**4
block_reward = 10 ** 5
fee = 10 ** 3
signers=64
# Lower limits on what the "time" tag in a block can say.
#get rid of decimal.
long_time=3000
medium_time=1000
short_time=100
maximum_deposit=all_money/signers/long_time/2
minimum_deposit=maximum_deposit/100
mmm = 100
download_many = 50  # Max number of blocks to request from a peer at the same time.
max_download = 58000
#buy_shares_target='0'*4+'1'+'9'*59
blocktime=60
DB = {
    'reward_peers_queue':multiprocessing.Queue(),
    'suggested_blocks': multiprocessing.Queue(),
    'suggested_txs': multiprocessing.Queue(),
    'heart_queue': multiprocessing.Queue(),
}


