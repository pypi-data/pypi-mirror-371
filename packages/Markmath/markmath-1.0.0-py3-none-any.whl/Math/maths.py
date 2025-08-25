import math


def cot(n):
    return 1 / math.tan(n)


def acot(n):
    return math.atan2(1, n)


def coth(n):
    return 1 / math.tanh(n)


def acoth(n):
    return math.atanh(1 / n)


def rooting(n, a):
    return math.pow(n, 1 / a)


def titration(c, a, n):
    if not isinstance(n, int) or n <= 0:
        raise ValueError("迭代次数必须是正整数!")
    q = 1
    m = a
    while True:
        if q < n:
            m = a ** m
            q = q + 1
        else:
            m = c ** m
            break
    return m


phi = (math.sqrt(5) - 1) / 2
golden_ratio = (1 + math.sqrt(5)) / 2


def eta(a, an, d):
    n = 1
    while True:
        if a * d ** n == an:
            break
        else:
            n = n + 1
    h = a
    q = 1
    while True:
        if a * d ** q == an:
            h = h + (a * d ** q)
            break
        else:
            h = h + (a * d ** q)
            q = q + 1
    return h


def etas(a, n, r):
    if r == 0:
        return 0 if n > 1 else a
    return (a ** n) * (r ** (n * (n - 1) // 2))


def sigma(a, n, d):
    return n * (2 * a + (n - 1) * d) / 2


def sigmas(a, n, r):
    if r == 1:
        return a * n
    return a * (1 - r ** n) / (1 - r)
