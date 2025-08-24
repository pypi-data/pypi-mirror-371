# Eternal Math

An open-source software platform designed as a comprehensive, ever-evolving toolkit for exploring, proving, and generating mathematical concepts.

## Overview

Eternal Math provides a Python-based framework for mathematical computation, theorem proving, and concept exploration. The platform combines computational tools with formal proof systems to create an integrated environment for mathematical research and education.

## Features

### Core Mathematical Objects
- **Set Theory**: Mathematical sets with standard operations (union, intersection, difference)
- **Function Theory**: Mathematical functions with composition and evaluation
- **Number Theory**: Prime numbers, GCD/LCM, factorization algorithms

### Proof System
- **Formal Proofs**: Structured proof representation with axioms, theorems, and proof steps
- **Theorem Management**: Create, verify, and organize mathematical theorems
- **Logical Framework**: Support for direct proofs, proof by contradiction, and more

### Number Theory Toolkit
- **Prime Generation**: Sieve of Eratosthenes for efficient prime computation
- **Sequences**: Fibonacci numbers, perfect numbers, Collatz sequences
- **Conjectures**: Goldbach conjecture verification, twin prime detection
- **Advanced Tools**: Euler's totient function, Chinese Remainder Theorem

### Visualization & Graphics
- **Function Plotting**: Visualize mathematical functions with customizable ranges
- **Sequence Visualization**: Plot mathematical sequences with annotations
- **Prime Distribution**: Graphical analysis of prime number patterns
- **Collatz Trajectories**: Visualize the famous 3n+1 problem paths
- **Comparative Analysis**: Side-by-side sequence comparisons

## Installation

```bash
# Clone the repository
git clone https://github.com/Vooblin/eternal-math.git
cd eternal-math

# Install dependencies
pip install -e .
```

## Quick Start

### Interactive CLI

Start the interactive command-line interface:

```bash
# After installation
eternal-math

# Or directly with Python
python -m eternal_math.cli
```

The CLI provides interactive access to all mathematical functions:

```
eternal-math> primes 30
🔍 Prime numbers up to 30:
   [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
   Found 10 primes

eternal-math> fibonacci 8
🌀 First 8 Fibonacci numbers:
   [0, 1, 1, 2, 3, 5, 8, 13]
   Golden ratio approximation: 1.625000

eternal-math> help
📚 Eternal Math CLI Commands:
[... complete help menu ...]
```

### Python API

```python
from eternal_math import sieve_of_eratosthenes, fibonacci_sequence, twin_primes

# Generate prime numbers up to 50
primes = sieve_of_eratosthenes(50)
print(f"Primes: {primes}")

# Generate Fibonacci sequence
fib = fibonacci_sequence(10)
print(f"Fibonacci: {fib}")

# Find twin prime pairs
twins = twin_primes(30)
print(f"Twin primes: {twins}")
```

### Visualization Features

Create stunning mathematical visualizations:

```python
from eternal_math import MathVisualizer

# Initialize visualizer
viz = MathVisualizer()

# Plot mathematical functions
viz.plot_function("x**2", title="Quadratic Function")
viz.plot_function("sin(x)", x_range=(-6, 6))

# Visualize sequences
from eternal_math import fibonacci_sequence, sieve_of_eratosthenes

fib = fibonacci_sequence(15)
viz.plot_sequence([float(x) for x in fib], title="Fibonacci Numbers")

# Prime distribution analysis
primes = sieve_of_eratosthenes(100)
viz.plot_prime_distribution(primes, 100)

# Interactive CLI visualization commands
# eternal-math> plot sin(x)
# eternal-math> plotseq fibonacci 10
# eternal-math> plotprimes 50
# eternal-math> plotcollatz 3,7,15
```
```

## Examples

Run the number theory exploration example:

```bash
python examples/number_theory_exploration.py
```

## Testing

Run the complete test suite:

```bash
# Run all tests
pytest tests/

# Run specific test modules
pytest tests/test_core.py
pytest tests/test_number_theory.py
pytest tests/test_proofs.py
pytest tests/test_cli.py

# Or run individual modules (legacy method)
python -m tests.test_core
python -m tests.test_number_theory
```

## Project Structure

```
eternal-math/
├── eternal_math/          # Main package
│   ├── core.py           # Core mathematical objects
│   ├── proofs.py         # Proof system and logic
│   ├── number_theory.py  # Number theory utilities
│   └── cli.py           # Interactive command-line interface
├── tests/                # Test suite
│   ├── test_cli.py      # CLI functionality tests
│   └── ...              # Other test modules
├── examples/             # Usage examples
└── pyproject.toml       # Project configuration
```

## Contributing

This is an open-source project. Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

MIT License - see LICENSE file for details.
