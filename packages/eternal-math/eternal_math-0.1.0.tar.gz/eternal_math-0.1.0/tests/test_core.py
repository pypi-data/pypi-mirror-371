"""
Tests for the core mathematical utilities.
"""

import pytest
from eternal_math.core import Set, Function, gcd, lcm, is_prime, prime_factorization


def test_set_operations():
    """Test basic set operations."""
    set_a = Set([1, 2, 3])
    set_b = Set([3, 4, 5])
    
    # Test union
    union = set_a.union(set_b)
    assert set(union.elements) == {1, 2, 3, 4, 5}
    
    # Test intersection
    intersection = set_a.intersection(set_b)
    assert intersection.elements == [3]
    
    # Test difference
    difference = set_a.difference(set_b)
    assert set(difference.elements) == {1, 2}
    
    # Test membership
    assert 2 in set_a
    assert 6 not in set_a


def test_function_operations():
    """Test function composition and evaluation."""
    # Create simple functions
    square = Function(lambda x: x ** 2, name="square")
    add_one = Function(lambda x: x + 1, name="add_one")
    
    # Test function evaluation
    assert square(3) == 9
    assert add_one(5) == 6
    
    # Test function composition
    composed = square.compose(add_one)
    assert composed(3) == 16  # (3 + 1)^2 = 16


def test_gcd_lcm():
    """Test greatest common divisor and least common multiple."""
    assert gcd(48, 18) == 6
    assert gcd(17, 13) == 1  # Coprime numbers
    assert gcd(0, 5) == 5
    
    assert lcm(12, 8) == 24
    assert lcm(17, 13) == 221  # Coprime numbers
    assert lcm(0, 5) == 0


def test_prime_functions():
    """Test prime-related functions."""
    # Test is_prime
    assert is_prime(2) == True
    assert is_prime(3) == True
    assert is_prime(4) == False
    assert is_prime(17) == True
    assert is_prime(25) == False
    assert is_prime(1) == False
    assert is_prime(0) == False
    
    # Test prime_factorization
    assert prime_factorization(12) == [2, 2, 3]
    assert prime_factorization(17) == [17]
    assert prime_factorization(1) == []
    assert prime_factorization(100) == [2, 2, 5, 5]


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    test_set_operations()
    test_function_operations()
    test_gcd_lcm()
    test_prime_functions()
    print("All core tests passed!")
