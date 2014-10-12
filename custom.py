"""This is to make magic numbers easier to deal with."""
import tools, hashlib
peers = [['192.241.212.114', 8900]]#,['69.164.196.239', 8900]]
database_name = 'DB.db'
port=8900
api_port=8899
database_port=8898
version = "0.0001"
#block_reward = [1,1]
premine = [1000000,1]
buy_block_fee=[10,1]
fee=[1,10]
# Lower limits on what the "time" tag in a block can say.
mmm = 100
# Take the median of this many of the blocks.
# How far back in history do we look when we use statistics to guess at
# the current blocktime and difficulty.
history_length = 400
# This constant is selected such that the 50 most recent blocks count for 1/2 the
# total weight.
download_many = 50  # Max number of blocks to request from a peer at the same time.
max_download = 58000
def blocktime(length): return 60
