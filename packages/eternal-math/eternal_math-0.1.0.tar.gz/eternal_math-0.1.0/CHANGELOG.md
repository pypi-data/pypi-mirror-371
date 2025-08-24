# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-23

### Added

- Initial release of eternal-math
- **Core Mathematical Objects**:
  - Set theory with standard operations (union, intersection, difference)
  - Function theory with composition and evaluation
  - Basic number theory utilities (GCD, LCM, prime testing)

- **Number Theory Toolkit**:
  - Sieve of Eratosthenes for prime generation
  - Fibonacci sequence generation
  - Perfect number detection
  - Euler's totient function
  - Collatz sequence generation
  - Twin prime detection
  - Goldbach conjecture verification
  - Chinese Remainder Theorem solver

- **Proof System**:
  - Formal proof representation with axioms and theorems
  - Structured proof steps with verification
  - Fundamental Theorem of Arithmetic implementation
  - Support for direct proofs and proof by contradiction

- **Symbolic Mathematics**:
  - Expression parsing and simplification
  - Algebraic expansion and factorization
  - Equation solving
  - Calculus operations (differentiation and integration)
  - Limit computation
  - Taylor series expansion
  - Variable substitution

- **Visualization Engine**:
  - Mathematical function plotting
  - Sequence visualization with annotations
  - Prime distribution analysis
  - Collatz trajectory visualization
  - Comparative sequence analysis

- **Interactive CLI**:
  - 25+ mathematical commands
  - Real-time computation and visualization
  - Command help and examples
  - Integrated with all core features

- **Package Infrastructure**:
  - Comprehensive test suite (72 tests)
  - Complete documentation and examples
  - GitHub Actions CI/CD pipeline
  - PyPI-ready packaging configuration

### Technical Details

- **Python Version**: Requires Python 3.12+
- **Dependencies**: NumPy, SymPy, Matplotlib
- **Installation**: `pip install eternal-math`
- **CLI Command**: `eternal-math`
- **License**: MIT

### Usage Examples

```bash
# Install the package
pip install eternal-math

# Use the CLI
eternal-math
> primes 30
> fibonacci 10
> plot sin(x)

# Use the Python API
from eternal_math import sieve_of_eratosthenes, fibonacci_sequence
primes = sieve_of_eratosthenes(100)
fib = fibonacci_sequence(15)
```
