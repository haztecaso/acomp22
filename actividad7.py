#!/usr/bin/env python3

# Adrián Lattes Grassi
# 20/11/22

from enum import Enum
from functools import lru_cache
from math import gcd, isqrt
from random import randint
from typing import Dict, Iterable, Set, Union


@lru_cache(maxsize=2**40)
def pow(b: int, e: int, m: int):
    """
    Implementación de la exponenciación modular rápida usando una cache para
    almacenar resultados.
    """
    r = 1
    if 1 & e:
        r = b
    while e:
        e >>= 1
        b = (b * b) % m
        if e & 1:
            r = (r * b) % m
    return r


class MaybePrime(Enum):
    """
    Enum para almacenar información sobre si un número es compuesto, primo o
    todavía no se ha podido determinar
    """

    UNSURE = -1
    COMPOSITE = 0
    PRIME = 1


# ------------------------------------------------------------------------------
# Empiezo definiendo funciones que funcionan en el caso general, para cualquier
# n. Más abajo las modifico particularizando para el caso n = p(m)+1
# ------------------------------------------------------------------------------

# Caché (almacenamiento en memoria de resultados) que usa la función
# prime_factors para no repetir cuentas
factor_cache: Dict[int, Set[int]] = dict()


def prime_factors(
    n: int,
    cache_save: bool = True,
    n_original: Union[int, None] = None,
):
    """
    Generador de factores primos de un número.

    Implementado usando generadores de python, mediante yield y next. Gracias a
    esto obtenemos una función 'perezosa' y no nos vemos obligados a calcular
    todos los factores primos de antemano si queremos iterar sobre ellos.
    """
    n_original = n if n_original is None else n_original
    if n <= 1:
        return
    global factor_cache
    if n_original not in factor_cache:
        factor_cache[n_original] = set()
    elif n == n_original:
        for p in factor_cache[n_original]:
            yield p
            while n % p == 0:
                n //= p
    p = next((x for x in range(2, isqrt(n) + 1) if n % x == 0), n)
    if cache_save:
        factor_cache[n_original].add(p)
    while n % p == 0:
        n //= p
    yield p
    yield from prime_factors(n, cache_save, n_original)


def rabin_miller_test(n: int, num_intentos: int = 10) -> MaybePrime:
    """Test probabilístico de no primalidad."""
    if n in {2, 3, 5, 7}:
        return MaybePrime.PRIME
    if n < 11 or n % 2 == 0:
        return MaybePrime.COMPOSITE
    r = 0
    m = n - 1
    while m % 2 == 0:
        m //= 2
        r += 1
    for _ in range(num_intentos):
        a = randint(1, n - 1)
        if gcd(a, n) != 1:
            return MaybePrime.COMPOSITE
        x = pow(a, m, n)
        esta_en_T_N = (x == 1) or (x == n - 1)
        t = 0
        while not esta_en_T_N and t < r - 1:
            x = pow(x, 2, n)
            esta_en_T_N = x == n - 1
            t += 1
        if not esta_en_T_N:
            return MaybePrime.COMPOSITE
    return MaybePrime.UNSURE


def lucas_test(n: int, num_intentos: int = 10) -> MaybePrime:
    """Test probabilístico de primalidad."""
    if n in {2, 3, 5, 7}:
        return MaybePrime.PRIME
    if n < 11 or n % 2 == 0:
        return MaybePrime.COMPOSITE
    for _ in range(num_intentos):
        a = randint(2, n - 1)
        if pow(a, n - 1, n) != 1:
            return MaybePrime.COMPOSITE
        check = True
        for p in prime_factors(n - 1):
            if pow(a, n - 1 // p, n) == -1:
                check = False
                break
        if check:
            return MaybePrime.PRIME
    return MaybePrime.UNSURE


def is_prime(n: int, num_intentos: int = 10) -> bool:
    """
    Función que combina los tests probabilísticos para obtener un resultado
    certero
    """
    result = MaybePrime.UNSURE
    while result == MaybePrime.UNSURE:
        result = rabin_miller_test(n, num_intentos)
        if result != MaybePrime.UNSURE:
            break
        result = lucas_test(n, num_intentos)
    return result == MaybePrime.PRIME


def check_n_values(ns: Iterable[int]):
    from time import time

    t0 = time()
    msg = ""
    clear = lambda msg: print(" " * len(msg), end="\r")
    for n in ns:
        msg = f"{n}\t{time()-t0:.2f}s".expandtabs()
        clear(msg)
        print(msg, end="\r")
        t = time()
        if is_prime(n):
            clear(msg)
            print(f"{n}\t{time()-t:.2f}s\t{time()-t0:.2f}s")


# --------------------------------------------------
# Funciones particularizadas para el caso n = p(m)+1
# --------------------------------------------------


def p(m: int):
    r = 1
    for i in range(m):
        r *= 3 * i + 1
    return r


def prime_factors_p_m(m: int):
    global p, factor_cache
    pm = p(m)
    if pm in factor_cache:
        return factor_cache[pm]
    result = set()
    for i in range(m):
        n = 3 * i + 1
        if n in factor_cache:
            result_n = factor_cache[n]
        else:
            result_n = set(prime_factors(n, False))
            factor_cache[n] = result_n
        result = result.union(result_n)
    factor_cache[pm] = result
    return result


def lucas_test_p_m_plus_1(m: int, num_intentos: int = 10) -> MaybePrime:
    global p
    n = p(m) + 1
    if n in {2, 3, 5, 7}:
        return MaybePrime.PRIME
    if n < 11 or n % 2 == 0:
        return MaybePrime.COMPOSITE
    for _ in range(num_intentos):
        a = randint(2, n - 1)
        if pow(a, n - 1, n) != 1:
            return MaybePrime.COMPOSITE
        check = True
        for q in prime_factors_p_m(m):
            if pow(a, n - 1 // q, n) == -1:
                check = False
                break
        if check:
            return MaybePrime.PRIME
    return MaybePrime.UNSURE


def is_prime_pm_plus_1(m: int, num_intentos: int = 10) -> bool:
    global p
    result = MaybePrime.UNSURE
    n = p(m) + 1
    while result == MaybePrime.UNSURE:
        result = rabin_miller_test(n, num_intentos)
        if result != MaybePrime.UNSURE:
            break
        result = lucas_test_p_m_plus_1(m, num_intentos)
    return result == MaybePrime.PRIME


def test_pm_plus_1(m: int) -> bool:
    return is_prime_pm_plus_1(m, 1)


def check_m_values(ms: Iterable[int]):
    from time import time

    t0 = time()
    msg = ""
    clear = lambda msg: print(" " * len(msg), end="\r")
    for m in ms:
        msg = f"{m}\t{time()-t0:.2f}s".expandtabs()
        clear(msg)
        print(msg, end="\r")
        t = time()
        if test_pm_plus_1(m):
            clear(msg)
            print(f"{m}\t{time()-t:.2f}s\t{time()-t0:.2f}s")


if __name__ == "__main__":
    check_m_values([1600])
    # check_m_values([1,2,3,4,14,20,31,59,443,1600,1659])
