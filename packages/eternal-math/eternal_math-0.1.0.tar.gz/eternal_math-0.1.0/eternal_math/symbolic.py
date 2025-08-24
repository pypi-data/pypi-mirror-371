"""
Symbolic mathematics and algebraic computation using SymPy.
"""

import sympy as sp
from typing import List, Tuple, Union, Dict, Any
from sympy import symbols, sympify, latex, simplify, expand, factor, solve, diff, integrate
from sympy import sin, cos, tan, exp, log, sqrt, pi, E, oo, I
from sympy.parsing.sympy_parser import parse_expr


class SymbolicMath:
    """Main class for symbolic mathematical operations."""
    
    @staticmethod
    def create_symbol(name: str, **assumptions) -> sp.Symbol:
        """Create a symbolic variable with optional assumptions."""
        return symbols(name, **assumptions)
    
    @staticmethod
    def create_symbols(names: str, **assumptions) -> Tuple[sp.Symbol, ...]:
        """Create multiple symbolic variables."""
        return symbols(names, **assumptions)
    
    @staticmethod
    def parse_expression(expr_str: str) -> sp.Expr:
        """Parse a string expression into a SymPy expression."""
        try:
            # Replace ^ with ** for Python exponentiation syntax
            expr_str = expr_str.replace('^', '**')
            return parse_expr(expr_str)
        except Exception as e:
            raise ValueError(f"Could not parse expression '{expr_str}': {e}")
    
    @staticmethod
    def simplify_expression(expr: Union[str, sp.Expr]) -> sp.Expr:
        """Simplify a mathematical expression."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        return simplify(expr)
    
    @staticmethod
    def expand_expression(expr: Union[str, sp.Expr]) -> sp.Expr:
        """Expand a mathematical expression."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        return expand(expr)
    
    @staticmethod
    def factor_expression(expr: Union[str, sp.Expr]) -> sp.Expr:
        """Factor a mathematical expression."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        return factor(expr)
    
    @staticmethod
    def solve_equation(equation: Union[str, sp.Expr], variable: Union[str, sp.Symbol] = None) -> List[sp.Expr]:
        """Solve an equation for a variable."""
        if isinstance(equation, str):
            # Replace ^ with ** for Python exponentiation syntax
            equation = equation.replace('^', '**')
            # Handle equation format "expr=0" or just "expr" 
            if '=' in equation:
                left, right = equation.split('=', 1)
                equation = SymbolicMath.parse_expression(f"({left}) - ({right})")
            else:
                equation = SymbolicMath.parse_expression(equation)
        
        if variable is None:
            # Auto-detect the variable if not specified
            free_symbols = equation.free_symbols
            if len(free_symbols) == 1:
                variable = list(free_symbols)[0]
            else:
                raise ValueError("Multiple variables found, please specify which variable to solve for")
        elif isinstance(variable, str):
            variable = symbols(variable)
        
        return solve(equation, variable)
    
    @staticmethod
    def differentiate(expr: Union[str, sp.Expr], variable: Union[str, sp.Symbol], order: int = 1) -> sp.Expr:
        """Compute the derivative of an expression."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        if isinstance(variable, str):
            variable = symbols(variable)
        
        return diff(expr, variable, order)
    
    @staticmethod
    def integrate(expr: Union[str, sp.Expr], variable: Union[str, sp.Symbol], 
                  limits: Tuple[Any, Any] = None) -> sp.Expr:
        """Compute the integral of an expression."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        if isinstance(variable, str):
            variable = symbols(variable)
        
        if limits:
            return integrate(expr, (variable, limits[0], limits[1]))
        else:
            return integrate(expr, variable)
    
    @staticmethod
    def substitute(expr: Union[str, sp.Expr], substitutions: Dict[str, Any]) -> sp.Expr:
        """Substitute values into an expression."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        
        # Convert string keys to symbols if needed
        subs_dict = {}
        for key, value in substitutions.items():
            if isinstance(key, str):
                key = symbols(key)
            subs_dict[key] = value
        
        return expr.subs(subs_dict)
    
    @staticmethod
    def to_latex(expr: Union[str, sp.Expr]) -> str:
        """Convert expression to LaTeX format."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        return latex(expr)
    
    @staticmethod
    def evaluate_expression(expr: Union[str, sp.Expr], substitutions: Dict[str, float] = None) -> Union[float, complex]:
        """Evaluate an expression numerically."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        
        if substitutions:
            expr = SymbolicMath.substitute(expr, substitutions)
        
        try:
            result = complex(expr.evalf())
            # Return real number if imaginary part is negligible
            if abs(result.imag) < 1e-10:
                return result.real
            return result
        except Exception as e:
            raise ValueError(f"Could not evaluate expression numerically: {e}")


class CalculusUtils:
    """Utilities for calculus operations."""
    
    @staticmethod
    def find_critical_points(expr: Union[str, sp.Expr], variable: Union[str, sp.Symbol]) -> List[sp.Expr]:
        """Find critical points of a function."""
        derivative = SymbolicMath.differentiate(expr, variable)
        return SymbolicMath.solve_equation(derivative, variable)
    
    @staticmethod
    def find_inflection_points(expr: Union[str, sp.Expr], variable: Union[str, sp.Symbol]) -> List[sp.Expr]:
        """Find inflection points of a function."""
        second_derivative = SymbolicMath.differentiate(expr, variable, order=2)
        return SymbolicMath.solve_equation(second_derivative, variable)
    
    @staticmethod
    def taylor_series(expr: Union[str, sp.Expr], variable: Union[str, sp.Symbol], 
                     point: float = 0, order: int = 6) -> sp.Expr:
        """Compute Taylor series expansion."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        if isinstance(variable, str):
            variable = symbols(variable)
        
        return expr.series(variable, point, order).removeO()
    
    @staticmethod
    def limit(expr: Union[str, sp.Expr], variable: Union[str, sp.Symbol], 
             point: Union[float, str]) -> sp.Expr:
        """Compute limit of an expression."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        if isinstance(variable, str):
            variable = symbols(variable)
        if point == 'oo' or point == 'inf':
            point = oo
        
        return sp.limit(expr, variable, point)


class AlgebraUtils:
    """Utilities for algebraic operations."""
    
    @staticmethod
    def solve_system(equations: List[Union[str, sp.Expr]], variables: List[Union[str, sp.Symbol]]) -> Dict[sp.Symbol, sp.Expr]:
        """Solve a system of equations."""
        eqs = []
        for eq in equations:
            if isinstance(eq, str):
                eq = SymbolicMath.parse_expression(eq)
            eqs.append(eq)
        
        vars_list = []
        for var in variables:
            if isinstance(var, str):
                var = symbols(var)
            vars_list.append(var)
        
        return solve(eqs, vars_list)
    
    @staticmethod
    def partial_fractions(expr: Union[str, sp.Expr], variable: Union[str, sp.Symbol]) -> sp.Expr:
        """Compute partial fraction decomposition."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        if isinstance(variable, str):
            variable = symbols(variable)
        
        return sp.apart(expr, variable)
    
    @staticmethod
    def simplify_trig(expr: Union[str, sp.Expr]) -> sp.Expr:
        """Simplify trigonometric expressions."""
        if isinstance(expr, str):
            expr = SymbolicMath.parse_expression(expr)
        return sp.trigsimp(expr)


# Common mathematical constants and functions for easy access
CONSTANTS = {
    'pi': pi,
    'e': E,
    'i': I,
    'infinity': oo,
    'oo': oo
}

FUNCTIONS = {
    'sin': sin,
    'cos': cos, 
    'tan': tan,
    'exp': exp,
    'log': log,
    'sqrt': sqrt
}


__all__ = [
    'SymbolicMath', 'CalculusUtils', 'AlgebraUtils',
    'CONSTANTS', 'FUNCTIONS'
]
