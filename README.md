hash-slinging-slasher
=====================

Hash-slinging-slasher is an alternative to POW for maintaining consensus. There is zero POW mining. The only major difference from slasher(1) is that the mining reward is a negative number.

fork: when there are 2 alternative choices for the next block

blocklength: to decide which fork is better, we prefer the longer one.

POW: proof-of-work. Requires a lot of computational power to produce.

POS: proof-of-stake. Requires prolonged investment in currency to produce.

POB: proof-of-burn. Requires the destruction of currency to produce. 

### POW consensus

blocklength: The number of hashes it takes to create a valid chain of equal length. Length is measured in blocks.

security: A transaction isn't secure until it is buried under enough blocks that a fork becomes improbable.

drawbacks: Wastes a ton of electricity.

The only secure method so far.

### POB consensus

blocklength: Each block requires the burning of a certain percentage of all coins, which causes the total number of coins to decrease exponanetially according to a half-life. Length is measured by how many coins were burned to produce the chain.

security: A N coin transaction isn't secure until it is buried under at least N coins of length.

drawbacks: If a person spends 100 N coin transactions in the same block, the recipients might think it is secure after only N length, but it really requires 100xN length. Double-spend is far too easy. It resembles how double-spend would work in a perfectly liquid market for mining hardware.

### POS consensus via representative democracy

blocklength: The number of times the representatives signed this particular chain. Length is measured in signatures.

security: A transactions isn't secure until it is buried under enough signatures that a fork becomes improbable.

drawbacks: Long-range attack. If you mine a ton of blocks, eventually you have control of all the pieces to hand-select the POS signers. You can select yourself as signer every single time. This attack is very profitable because you collect so many blockrewards.

nothing-at-stake. All POS besides slasher suffer this problem. Signers have incentive to sign on every fork that has even the smallest possibility of being the legitimate chain. The real chain gets lost among the many copies.

### hash-slinging-slasher POS+POB

blocklength: The total number of coins decreases every block according to a half-life. blocklength is measured in signatures.

security: A transactions isn't secure until it is buried under enough signatures that a fork becomes improbable.

Honest miners can only afford to build blocks because they collects so many transaction fees. If you try building a fake chain, you wont get any transaction fees, so it is incredibly expensive. Even if you did build this fake chain, you wont have any signatures on it. Long-range attacks are too expensive to pull off.

hash-slinging-slasher does not suffer the nothing-at-stake problem, because it borrows the punitive measures from slasher.

There is no longer a set blocktime. Instead, new blocks are created as soon as there are enough transactions to make it profitable.



### links

1) http://blog.ethereum.org/2014/01/15/slasher-a-punitive-proof-of-stake-algorithm/