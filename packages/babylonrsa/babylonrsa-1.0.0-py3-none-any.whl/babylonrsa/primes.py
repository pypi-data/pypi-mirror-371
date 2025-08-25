import random, math

def _modinv(a, m):
    a %= m
    if a == 0: raise ValueError("no inverse")
    lm, hm = 1, 0
    low, high = a, m
    while low > 1:
        r = high // low
        nm, new = hm - lm*r, high - low*r
        lm, low, hm, high = nm, new, lm, low
    return lm % m

def _is_probable_prime(n: int, k: int = 16) -> bool:
    if n < 2: return False
    small_primes = [2,3,5,7,11,13,17,19,23,29,31,37]
    for p in small_primes:
        if n % p == 0:
            return n == p
    r, d = 0, n-1
    while d % 2 == 0:
        d //= 2; r += 1
    for _ in range(k):
        a = random.randrange(2, n-2)
        x = pow(a, d, n)
        if x == 1 or x == n-1: continue
        for __ in range(r-1):
            x = pow(x, 2, n)
            if x == n-1: break
        else: return False
    return True

def _gen_prime(bits: int) -> int:
    assert bits >= 16
    while True:
        cand = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if _is_probable_prime(cand):
            return cand
