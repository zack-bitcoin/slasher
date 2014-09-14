"""This is to make magic numbers easier to deal with."""
import tools, hashlib
peers = [['127.0.0.1', 8900]]
database_name = 'DB.db'
old_database_name = 'old_DB.db'
port=8901
slasherd_port=8801
version = "VERSION"
block_reward = 10 ** 5
premine = 5 * 10 ** 6
fee = 10 ** 3
# Lower limits on what the "time" tag in a block can say.
mmm = 100
# Take the median of this many of the blocks.
# How far back in history do we look when we use statistics to guess at
# the current blocktime and difficulty.
history_length = 400
# This constant is selected such that the 50 most recent blocks count for 1/2 the
# total weight.
inflection = 0.985
download_many = 50  # Max number of blocks to request from a peer at the same time.
max_download = 50000
total_money=10**15
block_fee=total_money/(10**6) #gives us 100 years until 1/2 the money is gone, if we do 1 block per 10 min.
pledge_fee=block_fee/10000 
def blocktime(length): return 30
