"""
Example: Interactive CLI Session

This file demonstrates how to use the Eternal Math CLI for interactive exploration.
Run this with: python -m eternal_math.cli
"""

# This is a sample CLI session transcript showing various commands:

"""
🧮 Welcome to Eternal Math Interactive CLI
==================================================
Explore mathematical concepts interactively!
Type 'help' for available commands or 'quit' to exit.

eternal-math> help
📚 Eternal Math CLI Commands:
----------------------------------------
🔢 Number Theory:
  primes <n>        - Generate primes up to n
  fibonacci <n>     - Generate first n Fibonacci numbers
  perfect <n>       - Find perfect numbers up to n
  twins <n>         - Find twin prime pairs up to n
  goldbach <n>      - Verify Goldbach conjecture up to n
  euler <n>         - Calculate Euler's totient function φ(n)
  collatz <n>       - Generate Collatz sequence for n
  crt <a1,n1,a2,n2> - Chinese Remainder Theorem solver

🎓 Proof System:
  theorem           - Show Fundamental Theorem of Arithmetic

❓ General:
  examples          - Show usage examples
  help              - Show this help
  quit/exit         - Exit the CLI

eternal-math> primes 50
🔍 Prime numbers up to 50:
   [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
   Found 15 primes

eternal-math> fibonacci 10
🌀 First 10 Fibonacci numbers:
   [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
   Golden ratio approximation: 1.619048

eternal-math> perfect 100
✨ Perfect numbers up to 100:
   [6, 28]
   Found 2 perfect numbers

eternal-math> twins 50
👯 Twin prime pairs up to 50:
   [(3, 5), (5, 7), (11, 13), (17, 19), (29, 31), (41, 43)]
   Found 6 twin prime pairs

eternal-math> goldbach 50
🔍 Goldbach conjecture verification up to 50:
   Result: ✅ Holds
   (Every even integer > 2 can be expressed as sum of two primes)

eternal-math> euler 12
🔢 Euler's totient function φ(12):
   φ(12) = 4
   (Count of integers ≤ 12 that are coprime to 12)

eternal-math> collatz 7
🎯 Collatz sequence for 7:
   [7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]
   Sequence length: 17 steps

eternal-math> crt 2,3,3,5
🧮 Chinese Remainder Theorem:
   x ≡ 2 (mod 3)
   x ≡ 3 (mod 5)
   Solution: x ≡ 8 (mod 15)

eternal-math> theorem
📜 Every integer greater than 1 either is prime itself or is the product of prime numbers,
 and this product is unique up to the order of factors.

🎓 Status: Proven ✅

📋 Proof Structure:
   • Axioms used: 3
   • Proof steps: 9
   • Verification: Valid ✅

🔍 Axioms:
   1. Every integer n > 1 has a smallest divisor d > 1
   2. If d is the smallest divisor of n > 1, then d is prime
   3. If n = p1^a1 * p2^a2 * ... * pk^ak and n = q1^b1 * q2^b2 * ... * qm^bm where all p_i and q_j are prime, then k = m and the multisets {p1, p2, ..., pk} and {q1, q2, ..., qm} are identical

eternal-math> examples
💡 Usage Examples:
----------------------------------------
  Find prime numbers................ primes 30
  Generate Fibonacci sequence....... fibonacci 8
  Check perfect numbers............. perfect 50
  Find twin primes.................. twins 30
  Verify Goldbach conjecture........ goldbach 50
  Calculate Euler's totient......... euler 12
  Generate Collatz sequence......... collatz 7
  Solve Chinese Remainder........... crt 2,3,3,5
  View mathematical theorem......... theorem

eternal-math> quit
Goodbye! Thanks for exploring mathematics! 👋
"""

# To start the CLI, run:
if __name__ == "__main__":
    print("To start the interactive CLI, run:")
    print("python -m eternal_math.cli")
    print("\nOr if installed:")
    print("eternal-math")
