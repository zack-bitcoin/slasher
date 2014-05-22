hash-slinging-slasher
=====================

based on [slasher](http://blog.ethereum.org/2014/01/15/slasher-a-punitive-proof-of-stake-algorithm/)

Donations: 1GbpRPE83Vjg73KFvTVZ4EnS2qNkiLY5TT

INSTALL (for ubuntu)

    sudo apt-get install git
    sudo apt-get install python-leveldb
    git clone https://github.com/zack-bitcoin/slasher.git
    cd basiccoin/

To run 1 node

    python threads.py

To quickly run 5 nodes (linux/mac only)

    ./go.sh

Then send your browser to 

    http://localhost:8700 <---- this one has the money
    http://localhost:8701
    http://localhost:8702
    http://localhost:8703
    http://localhost:8704
    http://localhost:8705

###types of interactions that users can have with the blockchain:

1) If you own money, you can create valid transactions to spend it.

2) Anyone can create a block, but at least 0.21 coins of fees are destroyed.

3) People with money are selected at random to sign on blocks, for this they recieve a reward. These signatures determine chain-length see [slasher](http://blog.ethereum.org/2014/01/15/slasher-a-punitive-proof-of-stake-algorithm/)

4) If you catch a pos signer trying to sign 2 opposing forks, you can take his reward from him. see [slasher](http://blog.ethereum.org/2014/01/15/slasher-a-punitive-proof-of-stake-algorithm/)

(not yet implemented) 5) Several thousand people are in a seperate class from the rest of us. These people own a second type of money which is non-transferable. It was given to them on the genesis block. Every thousandth block of the blockchain is a census block. A census block requires at least 51% of the special class of people to sign it. Upon signing the census block, they recieve a reward.

(not yet implemented) 6) If a member from the special class is ever caught signing competing census blocks, his special-money can be destroyed.


###Types of attack, and why we are secure from them:

1) simple double-spend. Spend a large amount of money in a single block, quickly mine 2 blocks to create a longer chain and un-spend your money.

* This cannot happen because length is measured in POS signatures, not POW. A person with >51% of all money could do this attack, because he would own most of the signatures. 

2) nothing-at-stake. If there are thousands of optional chains, any of which could eventually become valid, we have to keep track of all of them. Eventually, the real chain is lost among the copies.

* This cannot happen because pos signers are only able to sign once, so only one chain will be paid attention to.

3) long-range double-spend. Spend a large amount of money in a single block, and then rebuild a massive amount of the chain to create a fork which is longer than the real chain. In slasher, if you create a long chain, eventually you get to the point where you know all the secrets. You are able to select who is the pos signer. If you own only 0.0001% of all money, you can still select youself as signer every time.

* This cannot happen because there is a census block between when the pos signer is given duty, and when he performs his duty. You cannot create a census block without knowing 51% of the private keys controlling the non-transferable money. 