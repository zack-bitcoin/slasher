size=50#in bits, this number is small enough to fit: 1000000000000000=10^15
def gcd(a, b): return a if b==0 else gcd(b, a%b)
def simplify_gcd(n): return (lambda c: [n[0]/c, n[1]/c])(gcd(n[0], n[1]))
def simplify_sign(n): return [-n[0], -n[1]] if n[1]<0 else n
def need_simplify_p(n): return abs(n[0]*n[1])>2**size
def simplify_magnitude(n): return simplify_magnitude([n[0]/2, n[1]/2]) if need_simplify_p(n) else n
def simplify(n): return simplify_sign(simplify_gcd(simplify_magnitude(n)))
def inv(n): return [n[1], n[0]]
def plus(na, nb): return simplify([na[0]*nb[1]+nb[0]*na[1], na[1]*nb[1]])
def neg(n): return [-n[0], n[1]]
def sub(na, nb): return plus(na, neg(nb))
def mul(na, nb): return simplify([na[0]*nb[0], na[1]*nb[1]])
def div(na, nb): return mul(na, inv(nb))
def average(na, nb): return div(plus(na, nb), [2, 1])
def sqrt_improve(n, guess): return average(div(n, guess), guess)
def sqrt(n, guess=[1, 1], counter=1, limit=7): return guess if counter==limit else sqrt(n, sqrt_improve(n, guess), counter+1, limit)
def to_decimal(n): return 'inf' if n[1]==0 else n[0]*1.0/n[1]
def accumulate(f, l, o): return o if len(l)==0 else accumulate(f, l[1:], f(o, l[0]))
def sum(l): return accumulate(plus, l, [0,1])
#print(sum([[1,1],[2,3],[1,3]]))
