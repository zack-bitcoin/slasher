Slasher
=====================

based on [slasher](http://blog.ethereum.org/2014/01/15/slasher-a-punitive-proof-of-stake-algorithm/) from the Ethereum team.

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

5) Several thousand people are in a seperate class from the rest of us. These people own a second type of money which is non-transferable. It was given to them on the genesis block. Every thousandth block of the blockchain is a census block. A census block requires at least 2/3rds of the special class of people to sign it. Upon signing the census block, they recieve a reward.

6) If a member from the special class is ever caught signing competing census blocks, his special-money can be destroyed. Once a census-singer signs a block, he is only allowed to sign children of that block from then on.


###Types of attack, and why we are secure from them:

A comprehensive explanation of why the ideal proof-of-stake system is impossible: http://download.wpsoftware.net/bitcoin/pos.pdf

1) simple double-spend. Spend a large amount of money in a single block, quickly mine 2 blocks to create a longer chain and un-spend your money.

* This cannot happen because length is measured in POS signatures, not POW. A person with >51% of all money could do this attack, because he would own most of the signatures. 

2) nothing-at-stake. If there are thousands of optional chains, any of which could eventually become valid, we have to keep track of all of them. Eventually, the real chain is lost among the copies.

* This cannot happen because pos signers are only able to sign once, so only one chain will be paid attention to.

3) long-range double-spend. Spend a large amount of money in a single block, and then rebuild a massive amount of the chain to create a fork which is longer than the real chain. In slasher, if you create a long chain, eventually you get to the point where you know all the secrets. You are able to select who is the pos signer. If you own only 0.0001% of all money, you can still select youself as signer every time.

* This cannot happen because there is a census block between when the pos signer is given duty, and when he performs his duty. You cannot create a census block without knowing 51% of the private keys controlling the non-transferable money. 

4) reveal keys that control non-transferable money. When these keys are revealed, it suddenly becomes possible to commit long-range double-spend. 

* If the same non-transferable money is used in conflicting ways, it destroys the contested money. If 1/3rd of non-transferable coins are destroyed, the blockchain freezes. It is possible to use this frozen blockchain to create or verify the creation of a new currency. 

** Case 1: over 1/2 of non-transferable coins are still secure. Use proof-of-burn to allow people to choose which new currency they want to join, or create new currencies where everyone owns money in the same amounts as the destroyed currency.

** Case 2: over 1/2 of non-transferable coins are revealed to adversaries. Can create new currencies where everyone owns money in the same amounts as the destroyed currency.


TODO list:
1) POS signers need to be more intelligent. If they miss out on signing a block, they should re-write their signature, and try including it in the next block.
2) POS signers should collect their rewards.

