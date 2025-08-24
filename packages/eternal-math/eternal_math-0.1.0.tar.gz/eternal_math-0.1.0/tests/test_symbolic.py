"""
Test suite for the symbolic mathematics module.
"""

import pytest
import sympy as sp
from eternal_math.symbolic import (
    SymbolicMath, CalculusUtils, AlgebraUtils,
    CONSTANTS, FUNCTIONS
)


class TestSymbolicMath:
    """Test the basic symbolic mathematics functionality."""
    
    def test_create_symbol(self):
        """Test creating symbolic variables."""
        x = SymbolicMath.create_symbol('x')
        assert isinstance(x, sp.Symbol)
        assert str(x) == 'x'
        
        # Test with assumptions
        y = SymbolicMath.create_symbol('y', real=True, positive=True)
        assert isinstance(y, sp.Symbol)
        assert y.is_real is True
        assert y.is_positive is True
    
    def test_create_symbols(self):
        """Test creating multiple symbolic variables."""
        x, y, z = SymbolicMath.create_symbols('x y z')
        assert all(isinstance(var, sp.Symbol) for var in [x, y, z])
        assert [str(var) for var in [x, y, z]] == ['x', 'y', 'z']
    
    def test_parse_expression(self):
        """Test parsing string expressions."""
        expr = SymbolicMath.parse_expression('x**2 + 2*x + 1')
        x = sp.Symbol('x')
        expected = x**2 + 2*x + 1
        assert expr == expected
        
        # Test with trigonometric functions
        expr2 = SymbolicMath.parse_expression('sin(x) + cos(x)')
        expected2 = sp.sin(x) + sp.cos(x)
        assert expr2 == expected2
    
    def test_simplify_expression(self):
        """Test expression simplification."""
        # Test with string input
        simplified = SymbolicMath.simplify_expression('(x + 1)**2 - (x**2 + 2*x + 1)')
        assert simplified == 0
        
        # Test with SymPy expression input
        x = sp.Symbol('x')
        expr = (x + 1)**2 - (x**2 + 2*x + 1)
        simplified = SymbolicMath.simplify_expression(expr)
        assert simplified == 0
    
    def test_expand_expression(self):
        """Test expression expansion."""
        expanded = SymbolicMath.expand_expression('(x + 1)**2')
        x = sp.Symbol('x')
        expected = x**2 + 2*x + 1
        assert expanded == expected
    
    def test_factor_expression(self):
        """Test expression factoring."""
        factored = SymbolicMath.factor_expression('x**2 - 1')
        x = sp.Symbol('x')
        expected = (x - 1) * (x + 1)
        assert factored == expected
    
    def test_solve_equation(self):
        """Test equation solving."""
        # Simple quadratic equation
        solutions = SymbolicMath.solve_equation('x**2 - 4')
        expected = [-2, 2]
        assert sorted(solutions) == sorted(expected)
        
        # Specify variable explicitly
        solutions2 = SymbolicMath.solve_equation('x**2 + y - 4', 'x')
        x, y = sp.symbols('x y')
        expected2 = [-sp.sqrt(4 - y), sp.sqrt(4 - y)]
        assert len(solutions2) == 2
    
    def test_differentiate(self):
        """Test differentiation."""
        # First derivative
        derivative = SymbolicMath.differentiate('x**3 + 2*x**2 + x', 'x')
        x = sp.Symbol('x')
        expected = 3*x**2 + 4*x + 1
        assert derivative == expected
        
        # Second derivative
        second_deriv = SymbolicMath.differentiate('x**3 + 2*x**2 + x', 'x', order=2)
        expected2 = 6*x + 4
        # Use simplify to handle different but equivalent expressions
        assert sp.simplify(second_deriv - expected2) == 0
    
    def test_integrate(self):
        """Test integration."""
        # Indefinite integral
        integral = SymbolicMath.integrate('2*x + 1', 'x')
        x = sp.Symbol('x')
        # Check derivative of result equals original
        assert sp.diff(integral, x) == 2*x + 1
        
        # Definite integral
        definite = SymbolicMath.integrate('x', 'x', (0, 2))
        assert definite == 2  # ∫₀² x dx = [x²/2]₀² = 2
    
    def test_substitute(self):
        """Test variable substitution."""
        x, y = sp.symbols('x y')
        expr = x**2 + y
        
        # Single substitution
        result = SymbolicMath.substitute(expr, {'x': 2})
        expected = 4 + y
        assert result == expected
        
        # Multiple substitutions
        result2 = SymbolicMath.substitute(expr, {'x': 2, 'y': 3})
        assert result2 == 7
    
    def test_to_latex(self):
        """Test LaTeX conversion."""
        latex_str = SymbolicMath.to_latex('x**2 + sqrt(y)')
        assert 'x^{2}' in latex_str
        assert 'sqrt' in latex_str or r'\sqrt' in latex_str
    
    def test_evaluate_expression(self):
        """Test numerical evaluation."""
        # Simple expression
        result = SymbolicMath.evaluate_expression('2 + 3')
        assert result == 5
        
        # Expression with variables
        result2 = SymbolicMath.evaluate_expression('x**2 + 1', {'x': 3})
        assert result2 == 10
        
        # Expression with pi
        result3 = SymbolicMath.evaluate_expression('pi')
        assert abs(result3 - 3.14159265) < 1e-5


class TestCalculusUtils:
    """Test calculus utilities."""
    
    def test_find_critical_points(self):
        """Test finding critical points."""
        # f(x) = x^2, critical point at x = 0
        critical_points = CalculusUtils.find_critical_points('x**2', 'x')
        assert 0 in critical_points
    
    def test_find_inflection_points(self):
        """Test finding inflection points."""
        # f(x) = x^3, inflection point at x = 0
        inflection_points = CalculusUtils.find_inflection_points('x**3', 'x')
        assert 0 in inflection_points
    
    def test_taylor_series(self):
        """Test Taylor series expansion."""
        # Taylor series of e^x around x = 0
        series = CalculusUtils.taylor_series('exp(x)', 'x', point=0, order=4)
        x = sp.Symbol('x')
        # Should be approximately 1 + x + x²/2 + x³/6 + ...
        expected_coeffs = [1, 1, sp.Rational(1, 2), sp.Rational(1, 6)]
        
        # Check if the series is a polynomial with expected leading terms
        poly_coeffs = [series.coeff(x, i) for i in range(4)]
        assert poly_coeffs == expected_coeffs
    
    def test_limit(self):
        """Test limit computation."""
        # lim x→0 sin(x)/x = 1
        limit_result = CalculusUtils.limit('sin(x)/x', 'x', 0)
        assert limit_result == 1
        
        # lim x→∞ 1/x = 0
        limit_inf = CalculusUtils.limit('1/x', 'x', 'oo')
        assert limit_inf == 0


class TestAlgebraUtils:
    """Test algebra utilities."""
    
    def test_solve_system(self):
        """Test solving systems of equations."""
        # Simple 2x2 system: x + y = 3, x - y = 1
        system = ['x + y - 3', 'x - y - 1']
        variables = ['x', 'y']
        solution = AlgebraUtils.solve_system(system, variables)
        
        x, y = sp.symbols('x y')
        assert solution[x] == 2
        assert solution[y] == 1
    
    def test_partial_fractions(self):
        """Test partial fraction decomposition."""
        # (2x + 3)/(x^2 - 1) = A/(x-1) + B/(x+1)
        result = AlgebraUtils.partial_fractions('(2*x + 3)/(x**2 - 1)', 'x')
        x = sp.Symbol('x')
        
        # The result should be a sum of terms with denominators (x-1) and (x+1)
        assert isinstance(result, sp.Expr)
        # Check that it's equivalent to the original when simplified
        original = (2*x + 3)/(x**2 - 1)
        assert sp.simplify(result - original) == 0
    
    def test_simplify_trig(self):
        """Test trigonometric simplification."""
        # sin²(x) + cos²(x) = 1
        simplified = AlgebraUtils.simplify_trig('sin(x)**2 + cos(x)**2')
        assert simplified == 1


class TestConstants:
    """Test mathematical constants."""
    
    def test_constants_available(self):
        """Test that constants are properly defined."""
        assert 'pi' in CONSTANTS
        assert 'e' in CONSTANTS
        assert 'i' in CONSTANTS
        
        # Test that they have correct values
        pi_val = complex(CONSTANTS['pi'].evalf())
        assert abs(pi_val.real - 3.14159265) < 1e-5
        
        e_val = complex(CONSTANTS['e'].evalf())
        assert abs(e_val.real - 2.71828182) < 1e-5


class TestFunctions:
    """Test mathematical functions."""
    
    def test_functions_available(self):
        """Test that common functions are available."""
        required_functions = ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']
        for func_name in required_functions:
            assert func_name in FUNCTIONS
            
        # Test function evaluation
        x = sp.Symbol('x')
        sin_func = FUNCTIONS['sin']
        result = sin_func(sp.pi/2)
        assert result == 1


class TestIntegration:
    """Test integration of symbolic math with the rest of the system."""
    
    def test_integration_with_number_theory(self):
        """Test that symbolic math can work with number theory concepts."""
        # Generate prime polynomials or work with prime-related expressions
        x = SymbolicMath.create_symbol('x')
        
        # Example: polynomial that generates many primes
        # f(x) = x^2 - x + 41 (Euler's prime-generating polynomial)
        poly = SymbolicMath.parse_expression('x**2 - x + 41')
        
        # Test evaluation at small integers
        for n in range(1, 5):
            value = SymbolicMath.evaluate_expression(poly, {'x': n})
            assert isinstance(value, (int, float))
            assert value > 0


if __name__ == "__main__":
    pytest.main([__file__])
