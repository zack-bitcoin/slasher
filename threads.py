import consensus, listener, threading, custom, leveldb, gui, networking, time, sys, tools, blockchain

db=leveldb.LevelDB(custom.database_name)
db_old=leveldb.LevelDB('old_'+custom.database_name)
brainwallet='brain wallet'
privkey=tools.det_hash(brainwallet)
pubkey=tools.privtopub(privkey)
DB={'db':db, 
    'db_old':db_old,
    'recentHash':0, 
    'length':-1, 
    'sigLength':0, 
    'txs':[], 
    'suggested_blocks':[], 
    'suggested_txs':[], 
    'all_stake':1,
    'all_money':custom.initial_money}
blockchain.db_put(tools.make_address([pubkey],1), {'count':0, 'amount':custom.initial_money, 'stake':1, 'stake_flag':True}, DB)
blockchain.db_put(tools.make_address([pubkey],1), {'count':0, 'amount':custom.initial_money, 'stake':1, 'stake_flag':True}, DB, 'db_old')
todo=[
#keeps track of blockchain database, checks on peers for new 
#blocks and transactions.
    #[consensus.miner, 
    # (custom.pubkey, custom.peers, custom.hashes_per_check, DB), True],
    [listener.server, (DB, ), True],
    [consensus.mainloop, 
     (custom.peers, DB), True],
#listens for peers. Peers might ask us for our blocks and our pool ofrecent 
#transactions, or peers could suggest blocks and transactions to us.
    [gui.main, (custom.gui_port, custom.brainwallet, DB), True]]
networking.kill_processes_using_ports([str(custom.gui_port),
                                       str(custom.listen_port)])
for i in todo:
    t = threading.Thread(target=i[0], args = i[1])
    t.setDaemon(i[2])
    t.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print('exiting')
        sys.exit(1)
    
