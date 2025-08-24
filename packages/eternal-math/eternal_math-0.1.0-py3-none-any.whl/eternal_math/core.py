"""
Core mathematical utilities and data structures for Eternal Math.
"""

import numpy as np
from typing import List, Union, Callable, Any


class MathematicalObject:
    """Base class for all mathematical objects in the system."""
    
    def __init__(self, name: str = None):
        self.name = name
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name or 'unnamed'})"


class Set(MathematicalObject):
    """Mathematical set implementation."""
    
    def __init__(self, elements: List[Any] = None, name: str = None):
        super().__init__(name)
        self.elements = list(set(elements or []))
    
    def __contains__(self, item):
        return item in self.elements
    
    def __len__(self):
        return len(self.elements)
    
    def __iter__(self):
        return iter(self.elements)
    
    def union(self, other: 'Set') -> 'Set':
        """Return the union of this set with another."""
        return Set(self.elements + other.elements)
    
    def intersection(self, other: 'Set') -> 'Set':
        """Return the intersection of this set with another."""
        return Set([x for x in self.elements if x in other])
    
    def difference(self, other: 'Set') -> 'Set':
        """Return the difference of this set with another."""
        return Set([x for x in self.elements if x not in other])


class Function(MathematicalObject):
    """Mathematical function representation."""
    
    def __init__(self, func: Callable, domain: Set = None, codomain: Set = None, name: str = None):
        super().__init__(name)
        self.func = func
        self.domain = domain
        self.codomain = codomain
    
    def __call__(self, x):
        if self.domain and x not in self.domain:
            raise ValueError(f"{x} is not in the domain {self.domain}")
        return self.func(x)
    
    def compose(self, other: 'Function') -> 'Function':
        """Compose this function with another function."""
        return Function(lambda x: self(other(x)), 
                       other.domain, 
                       self.codomain,
                       f"({self.name} ∘ {other.name})" if self.name and other.name else None)


def gcd(a: int, b: int) -> int:
    """Calculate the greatest common divisor of two integers using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return abs(a)


def lcm(a: int, b: int) -> int:
    """Calculate the least common multiple of two integers."""
    return abs(a * b) // gcd(a, b) if a and b else 0


def is_prime(n: int) -> bool:
    """Check if a number is prime using trial division."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def prime_factorization(n: int) -> List[int]:
    """Return the prime factorization of a positive integer."""
    if n < 2:
        return []
    
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


__all__ = [
    'MathematicalObject', 'Set', 'Function', 
    'gcd', 'lcm', 'is_prime', 'prime_factorization'
]
