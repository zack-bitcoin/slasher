"""
Scenario
Say there are 100 validators per block. 43% of them want to collude to maintain a fork. On the blocks where they control over 67%, they can create the block on the wrong fork.

odds that out of 100 random draws, 0 are validators:
0.67**100
odds that out of 100 random draws, 1 are validators:
0.43*0.57**99*100

The odds that the attackers control a block?
1-(0.43^0*0.57^100*(choose 100 0))-...-(0.43**67*0.57**33*(choose 100 57))
"""
import math, numpy
def fact(x): return math.factorial(x)
def choose(b, a): return fact(b)/(1.0*fact(a)*fact(b-a))
def sub_range(total, attackers, r):
    p=1.0*attackers/total
    q=1-p#prob that a random validator is not an attacker.
    times=int(total*r)
    return sub_range_helper(total, attackers, p, q, times)
def sub_range_helper(total, attackers, p, q, times):
    if attackers>total: 1
    if times<1: return 0
    a=choose(total, times)*(p**times)*(q**(total-times))
    return a+sub_range_helper(total, attackers, p, q, times-1)
def prob_control_block(total, attackers, p):#if there are exactly total validators selected to control the next block and each has a attackers/100 probability of being an attacker, then this is the probability they will control >p% of the next block.
    return 1-(sub_range(total, attackers, p))
def gamma_control_block(total, attackers, p):# if each person has a small possibility to be a validator, and there are total validators on average, and attackers/100 is the percentage of people who want to attack, then this outputs the probability that the attackers will control >p of the next block
    a=0
    rounds=5000
    for i in range(rounds):
        a+=prob_control_block(int(numpy.random.gamma(total, 1)), attackers, p)
    return(a/rounds)
def gamma_freeze(attackers):
    return gamma_control_block(100, 100-attackers, 2.0/3)
def gamma_fork(attackers):
    return gamma_control_block(100, attackers, 2.0/3)
def test():
    print("given that X% of the validators want to maintain a fork, how often will they control more than 67% of the next block. 100 validators total selected")
    print("assuming that a gap of size 50 is too big to jump")
    print(gamma_freeze(49.7))#0.02
    print("this shows that any 49.7% of validators could freeze the network")
    print(gamma_fork(50.3))#0.02
    print("this shows that any 50.3% of validators could maintain a fork the network")


