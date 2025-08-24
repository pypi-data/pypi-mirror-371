"""
Tests for the number theory module.
"""

from eternal_math.number_theory import (
    sieve_of_eratosthenes, fibonacci, fibonacci_sequence, is_perfect_number,
    euler_totient, collatz_sequence, twin_primes, verify_goldbach_conjecture,
    NumberTheoryUtils
)


def test_sieve_of_eratosthenes():
    """Test the Sieve of Eratosthenes algorithm."""
    primes = sieve_of_eratosthenes(30)
    expected = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert primes == expected
    
    # Test edge cases
    assert sieve_of_eratosthenes(1) == []
    assert sieve_of_eratosthenes(2) == [2]


def test_fibonacci():
    """Test Fibonacci number calculation."""
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55
    
    # Test sequence generation
    seq = fibonacci_sequence(8)
    expected = [0, 1, 1, 2, 3, 5, 8, 13]
    assert seq == expected


def test_perfect_numbers():
    """Test perfect number detection."""
    assert is_perfect_number(6) == True   # 1 + 2 + 3 = 6
    assert is_perfect_number(28) == True  # 1 + 2 + 4 + 7 + 14 = 28
    assert is_perfect_number(12) == False
    assert is_perfect_number(1) == False


def test_euler_totient():
    """Test Euler's totient function."""
    assert euler_totient(1) == 1
    assert euler_totient(9) == 6   # φ(9) = 9 * (1 - 1/3) = 6
    assert euler_totient(10) == 4  # φ(10) = 10 * (1 - 1/2) * (1 - 1/5) = 4


def test_collatz_sequence():
    """Test Collatz sequence generation."""
    seq = collatz_sequence(3)
    expected = [3, 10, 5, 16, 8, 4, 2, 1]
    assert seq == expected
    
    assert collatz_sequence(1) == [1]
    assert collatz_sequence(0) == []


def test_twin_primes():
    """Test twin prime detection."""
    twins = twin_primes(20)
    expected = [(3, 5), (5, 7), (11, 13), (17, 19)]
    assert twins == expected


def test_goldbach_conjecture():
    """Test Goldbach conjecture verification for small numbers."""
    # This should be true for small limits
    assert verify_goldbach_conjecture(100) == True


def test_chinese_remainder_theorem():
    """Test Chinese Remainder Theorem solver."""
    # System: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)
    # Solution: x ≡ 23 (mod 105)
    result = NumberTheoryUtils.chinese_remainder_theorem([2, 3, 2], [3, 5, 7])
    assert result == 23


if __name__ == "__main__":
    # Run tests manually
    test_sieve_of_eratosthenes()
    test_fibonacci()
    test_perfect_numbers()
    test_euler_totient()
    test_collatz_sequence()
    test_twin_primes()
    test_goldbach_conjecture()
    test_chinese_remainder_theorem()
    print("All number theory tests passed!")
