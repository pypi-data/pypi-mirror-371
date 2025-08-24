"""
Example: Symbolic Mathematics with Eternal Math

This example demonstrates the symbolic mathematics capabilities using SymPy integration.
"""

from eternal_math import SymbolicMath, CalculusUtils, AlgebraUtils


def main():
    """Demonstrate symbolic mathematics features."""
    print("=== Eternal Math: Symbolic Mathematics ===\n")
    
    # 1. Basic symbolic operations
    print("1. Basic Symbolic Operations:")
    print("   Expression: (x + 1)^2")
    expanded = SymbolicMath.expand_expression("(x + 1)**2")
    print(f"   Expanded: {expanded}")
    
    simplified = SymbolicMath.simplify_expression("x**2 + 2*x + 1 - (x + 1)**2")
    print(f"   Simplification test: {simplified}")
    
    factored = SymbolicMath.factor_expression("x**2 - 1")
    print(f"   Factored x² - 1: {factored}\n")
    
    # 2. Equation solving
    print("2. Equation Solving:")
    solutions = SymbolicMath.solve_equation("x**2 - 4")
    print(f"   Solutions to x² - 4 = 0: {solutions}")
    
    # System of equations
    system_solution = AlgebraUtils.solve_system(
        ["x + y - 5", "2*x - y - 1"], 
        ["x", "y"]
    )
    print(f"   System solution: {system_solution}\n")
    
    # 3. Calculus operations
    print("3. Calculus Operations:")
    
    # Differentiation
    derivative = SymbolicMath.differentiate("x**3 + 2*x**2 + x", "x")
    print(f"   d/dx(x³ + 2x² + x) = {derivative}")
    
    # Integration
    integral = SymbolicMath.integrate("2*x + 1", "x")
    print(f"   ∫(2x + 1)dx = {integral} + C")
    
    # Limits
    limit_result = CalculusUtils.limit("sin(x)/x", "x", 0)
    print(f"   lim(x→0) sin(x)/x = {limit_result}")
    
    # Taylor series
    taylor = CalculusUtils.taylor_series("exp(x)", "x", 0, 5)
    print(f"   Taylor series of eˣ: {taylor}\n")
    
    # 4. Advanced features
    print("4. Advanced Symbolic Features:")
    
    # Critical points
    critical_points = CalculusUtils.find_critical_points("x**3 - 3*x", "x")
    print(f"   Critical points of x³ - 3x: {critical_points}")
    
    # Substitution
    expr = SymbolicMath.parse_expression("x**2 + y")
    substituted = SymbolicMath.substitute(expr, {"x": 2, "y": 3})
    print(f"   Substitute x=2, y=3 in x² + y: {substituted}")
    
    # Numerical evaluation
    value = SymbolicMath.evaluate_expression("pi/4")
    print(f"   Numerical value of π/4: {value:.6f}")
    
    # LaTeX conversion
    latex = SymbolicMath.to_latex("x**2 + sqrt(y)")
    print(f"   LaTeX format: {latex}\n")
    
    # 5. Integration with Number Theory
    print("5. Number Theory + Symbolic Math:")
    
    # Euler's prime-generating polynomial: n² - n + 41
    prime_poly = SymbolicMath.parse_expression("n**2 - n + 41")
    print(f"   Euler's polynomial: {prime_poly}")
    
    print("   Values for n = 1 to 5:")
    for n in range(1, 6):
        value = SymbolicMath.evaluate_expression(prime_poly, {"n": n})
        print(f"   n={n}: {int(value)}")
    
    print("\n" + "="*50)
    print("Symbolic mathematics greatly expands Eternal Math's capabilities!")
    print("• Algebraic manipulation and simplification")
    print("• Equation solving (single equations and systems)")  
    print("• Calculus operations (derivatives, integrals, limits)")
    print("• Taylor series expansions")
    print("• Critical point analysis")
    print("• LaTeX output for publication")
    print("• Seamless integration with number theory")
    print("="*50)


if __name__ == "__main__":
    main()
