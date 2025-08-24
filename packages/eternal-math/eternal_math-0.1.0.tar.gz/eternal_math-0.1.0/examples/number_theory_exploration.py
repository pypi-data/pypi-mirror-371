"""
Example: Basic Number Theory Exploration

This example demonstrates how to use Eternal Math to explore basic number theory concepts.
"""

from eternal_math import (
    sieve_of_eratosthenes, fibonacci_sequence, is_perfect_number,
    twin_primes, verify_goldbach_conjecture, create_fundamental_theorem_of_arithmetic
)


def main():
    """Demonstrate various number theory features."""
    print("=== Eternal Math: Number Theory Exploration ===\n")
    
    # Generate prime numbers
    print("1. Prime Numbers (up to 50):")
    primes = sieve_of_eratosthenes(50)
    print(f"   {primes}\n")
    
    # Fibonacci sequence
    print("2. Fibonacci Sequence (first 12 numbers):")
    fib_seq = fibonacci_sequence(12)
    print(f"   {fib_seq}\n")
    
    # Perfect numbers
    print("3. Perfect Numbers (checking first 30 numbers):")
    perfect_nums = []
    for n in range(1, 31):
        if is_perfect_number(n):
            perfect_nums.append(n)
    print(f"   {perfect_nums}\n")
    
    # Twin primes
    print("4. Twin Prime Pairs (up to 50):")
    twins = twin_primes(50)
    print(f"   {twins}\n")
    
    # Goldbach conjecture verification
    print("5. Goldbach Conjecture Verification (up to 100):")
    goldbach_holds = verify_goldbach_conjecture(100)
    print(f"   Goldbach conjecture holds for all even numbers up to 100: {goldbach_holds}\n")
    
    # Demonstrate theorem system
    print("6. Mathematical Theorem Example:")
    fundamental_theorem = create_fundamental_theorem_of_arithmetic()
    print(f"   Theorem: {fundamental_theorem.description}")
    print(f"   Proven: {fundamental_theorem.proven}")
    print(f"   Proof steps: {len(fundamental_theorem.proof.steps) if fundamental_theorem.proof else 0}")
    print(f"   Axioms used: {len(fundamental_theorem.proof.axioms) if fundamental_theorem.proof else 0}\n")
    
    print("=== End of Exploration ===")


if __name__ == "__main__":
    main()
