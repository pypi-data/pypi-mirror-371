#!/usr/bin/env python3
"""
Demonstration of Eternal Math visualization capabilities.

This script showcases the new visualization features added to Eternal Math,
including function plotting, sequence visualization, and mathematical concept
illustrations.
"""

from eternal_math import (
    MathVisualizer, sieve_of_eratosthenes, fibonacci_sequence,
    collatz_sequence, euler_totient, create_output_directory
)
import os


def demo_function_plotting():
    """Demonstrate function plotting capabilities."""
    print("🎨 Function Plotting Demo")
    print("=" * 40)
    
    visualizer = MathVisualizer()
    output_dir = create_output_directory()
    
    # Plot various mathematical functions
    functions = [
        ("x**2", "Quadratic Function"),
        ("sin(x)", "Sine Function"),
        ("exp(x)", "Exponential Function"),
        ("log(x)", "Natural Logarithm"),
        ("x**3 - 3*x + 1", "Cubic Polynomial")
    ]
    
    for i, (expr, title) in enumerate(functions, 1):
        print(f"\n{i}. Plotting {title}: f(x) = {expr}")
        
        # Determine appropriate range for each function
        if "exp" in expr:
            x_range = (-2, 3)
        elif "log" in expr:
            x_range = (0.1, 10)
        else:
            x_range = (-10, 10)
        
        save_path = os.path.join(output_dir, f"function_{i}_{expr.replace('*', 'x').replace('/', 'div')}.png")
        
        success = visualizer.plot_function(
            expr, 
            x_range=x_range,
            title=title,
            save_path=save_path
        )
        
        if success:
            print(f"   ✅ Successfully plotted and saved!")
        else:
            print(f"   ❌ Failed to plot function")


def demo_sequence_visualization():
    """Demonstrate sequence visualization."""
    print("\n\n🔢 Sequence Visualization Demo")
    print("=" * 40)
    
    visualizer = MathVisualizer()
    output_dir = create_output_directory()
    
    # 1. Fibonacci sequence
    print("\n1. Fibonacci Sequence")
    fib_seq = fibonacci_sequence(15)
    fib_floats = [float(x) for x in fib_seq]
    
    success = visualizer.plot_sequence(
        fib_floats,
        title="First 15 Fibonacci Numbers",
        save_path=os.path.join(output_dir, "fibonacci_sequence.png")
    )
    print(f"   Fibonacci sequence: {fib_seq[:10]}...")
    print(f"   ✅ Plot saved!" if success else "   ❌ Plot failed!")
    
    # 2. Prime numbers visualization
    print("\n2. Prime Numbers Distribution")
    primes = sieve_of_eratosthenes(100)
    
    success = visualizer.plot_prime_distribution(
        primes,
        100,
        save_path=os.path.join(output_dir, "prime_distribution.png")
    )
    print(f"   Found {len(primes)} primes up to 100")
    print(f"   First 10 primes: {primes[:10]}")
    print(f"   ✅ Plot saved!" if success else "   ❌ Plot failed!")
    
    # 3. Euler's totient function
    print("\n3. Euler's Totient Function φ(n)")
    totients = [euler_totient(n) for n in range(1, 21)]
    
    success = visualizer.plot_sequence(
        [float(x) for x in totients],
        title="Euler's Totient Function φ(n) for n = 1 to 20",
        save_path=os.path.join(output_dir, "euler_totient.png")
    )
    print(f"   φ(n) values: {totients}")
    print(f"   ✅ Plot saved!" if success else "   ❌ Plot failed!")


def demo_collatz_trajectories():
    """Demonstrate Collatz sequence visualization."""
    print("\n\n🌀 Collatz Conjecture Visualization")
    print("=" * 40)
    
    visualizer = MathVisualizer()
    output_dir = create_output_directory()
    
    # Generate Collatz sequences for different starting values
    starting_values = [3, 7, 15, 27, 31]
    sequences = []
    
    print("\nGenerating Collatz sequences:")
    for start_val in starting_values:
        seq = collatz_sequence(start_val)
        sequences.append(seq)
        print(f"   {start_val} → {seq[:5]}... (length: {len(seq)})")
    
    success = visualizer.plot_collatz_trajectory(
        sequences,
        starting_values,
        save_path=os.path.join(output_dir, "collatz_trajectories.png")
    )
    
    print(f"\n   ✅ Collatz plot saved!" if success else "   ❌ Plot failed!")
    print("   Note: All sequences eventually reach 1 (conjecture holds)")


def demo_comparative_analysis():
    """Demonstrate comparative sequence analysis."""
    print("\n\n📊 Comparative Sequence Analysis")
    print("=" * 40)
    
    visualizer = MathVisualizer()
    output_dir = create_output_directory()
    
    # Compare different mathematical sequences
    n = 15
    
    sequences = {
        "Fibonacci": [float(x) for x in fibonacci_sequence(n)],
        "Primes": [float(x) for x in sieve_of_eratosthenes(n * 10)[:n]],
        "Euler φ(n)": [float(euler_totient(i)) for i in range(1, n + 1)],
        "Powers of 2": [float(2**i) for i in range(n)],
        "Triangular": [float(i * (i + 1) // 2) for i in range(1, n + 1)]
    }
    
    print(f"\nComparing sequences (first {n} terms):")
    for name, seq in sequences.items():
        print(f"   {name}: {seq[:5]}...")
    
    success = visualizer.plot_comparative_sequences(
        sequences,
        title="Comparative Analysis of Mathematical Sequences",
        save_path=os.path.join(output_dir, "sequence_comparison.png")
    )
    
    print(f"\n   ✅ Comparative plot saved!" if success else "   ❌ Plot failed!")


def main():
    """Run all visualization demos."""
    print("🎯 Eternal Math Visualization Showcase")
    print("=" * 50)
    print("Demonstrating the new visualization capabilities!")
    print("All plots will be saved to the 'math_plots' directory.")
    
    # Run all demonstrations
    demo_function_plotting()
    demo_sequence_visualization()
    demo_collatz_trajectories()
    demo_comparative_analysis()
    
    print("\n\n🎉 Visualization Demo Complete!")
    print("=" * 50)
    print("Check the 'math_plots' directory for all generated plots.")
    print("These visualizations showcase the mathematical concepts")
    print("in an accessible and engaging way!")


if __name__ == "__main__":
    main()
