"""
Visualization module for Eternal Math

This module provides visualization capabilities for mathematical functions,
sequences, and concepts using matplotlib.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable, Optional
import sympy as sp
from sympy import lambdify
import os

class MathVisualizer:
    """Class for creating mathematical visualizations."""
    
    def __init__(self, style: str = 'default'):
        """Initialize the visualizer with a specific style."""
        plt.style.use(style)
        self.figure_size = (10, 6)
        
    def plot_function(self, expression: str, x_range: Tuple[float, float] = (-10, 10), 
                     title: Optional[str] = None, save_path: Optional[str] = None) -> bool:
        """
        Plot a mathematical function from string expression.
        
        Args:
            expression: Mathematical expression as string (e.g., 'x**2', 'sin(x)')
            x_range: Tuple of (min, max) for x-axis range
            title: Optional title for the plot
            save_path: Optional path to save the plot
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Parse the expression
            x = sp.Symbol('x')
            expr = sp.sympify(expression)
            
            # Convert to numerical function
            func = lambdify(x, expr, 'numpy')
            
            # Generate x values
            x_vals = np.linspace(x_range[0], x_range[1], 1000)
            y_vals = func(x_vals)
            
            # Create the plot
            plt.figure(figsize=self.figure_size)
            plt.plot(x_vals, y_vals, linewidth=2, color='blue')
            plt.grid(True, alpha=0.3)
            plt.xlabel('x', fontsize=12)
            plt.ylabel(f'f(x) = {expression}', fontsize=12)
            
            if title:
                plt.title(title, fontsize=14, fontweight='bold')
            else:
                plt.title(f'Plot of f(x) = {expression}', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"📊 Plot saved to: {save_path}")
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error plotting function: {e}")
            return False
    
    def plot_sequence(self, sequence: List[float], title: Optional[str] = None, 
                     x_labels: Optional[List[str]] = None, save_path: Optional[str] = None) -> bool:
        """
        Plot a mathematical sequence.
        
        Args:
            sequence: List of values to plot
            title: Optional title for the plot
            x_labels: Optional labels for x-axis
            save_path: Optional path to save the plot
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            plt.figure(figsize=self.figure_size)
            
            x_vals = x_labels if x_labels else list(range(len(sequence)))
            
            # Plot as both points and lines
            plt.plot(x_vals, sequence, 'ro-', linewidth=2, markersize=6, 
                    markerfacecolor='darkred')
            
            plt.grid(True, alpha=0.3)
            plt.xlabel('n', fontsize=12)
            plt.ylabel('Value', fontsize=12)
            
            if title:
                plt.title(title, fontsize=14, fontweight='bold')
            else:
                plt.title('Mathematical Sequence', fontsize=14, fontweight='bold')
            
            # Add value annotations for small sequences
            if len(sequence) <= 20:
                for i, val in enumerate(sequence):
                    plt.annotate(f'{val}', (x_vals[i], val), 
                               textcoords="offset points", xytext=(0,10), ha='center')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"📊 Plot saved to: {save_path}")
            else:
                plt.show()
                
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error plotting sequence: {e}")
            return False
    
    def plot_prime_distribution(self, primes: List[int], limit: int, 
                               save_path: Optional[str] = None) -> bool:
        """
        Plot the distribution of prime numbers.
        
        Args:
            primes: List of prime numbers
            limit: Upper limit for the range
            save_path: Optional path to save the plot
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            plt.figure(figsize=(12, 8))
            
            # Create subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Plot 1: Prime numbers as points
            ax1.scatter(primes, [1] * len(primes), alpha=0.6, s=20, color='blue')
            ax1.set_xlim(0, limit)
            ax1.set_ylim(0.5, 1.5)
            ax1.set_xlabel('Number', fontsize=12)
            ax1.set_title(f'Prime Numbers up to {limit}', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.set_yticks([])
            
            # Plot 2: Prime counting function π(x)
            x_vals = list(range(2, limit + 1))
            pi_x = []
            prime_count = 0
            prime_set = set(primes)
            
            for x in x_vals:
                if x in prime_set:
                    prime_count += 1
                pi_x.append(prime_count)
            
            ax2.plot(x_vals, pi_x, linewidth=2, color='red', label='π(x)')
            
            # Add approximation x/ln(x)
            x_approx = np.linspace(2, limit, 1000)
            approx = x_approx / np.log(x_approx)
            ax2.plot(x_approx, approx, '--', linewidth=2, color='green', 
                    label='x/ln(x) approximation')
            
            ax2.set_xlabel('x', fontsize=12)
            ax2.set_ylabel('π(x)', fontsize=12)
            ax2.set_title('Prime Counting Function π(x)', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"📊 Plot saved to: {save_path}")
            else:
                plt.show()
                
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error plotting prime distribution: {e}")
            return False
    
    def plot_collatz_trajectory(self, sequences: List[List[int]], 
                               starting_values: List[int], save_path: Optional[str] = None) -> bool:
        """
        Plot Collatz sequence trajectories.
        
        Args:
            sequences: List of Collatz sequences
            starting_values: List of starting values for each sequence
            save_path: Optional path to save the plot
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            plt.figure(figsize=(12, 8))
            
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink']
            
            for i, (seq, start_val) in enumerate(zip(sequences, starting_values)):
                color = colors[i % len(colors)]
                steps = list(range(len(seq)))
                plt.plot(steps, seq, 'o-', linewidth=2, markersize=4,
                        color=color, label=f'Start: {start_val}')
            
            plt.yscale('log')
            plt.xlabel('Step', fontsize=12)
            plt.ylabel('Value (log scale)', fontsize=12)
            plt.title('Collatz Sequences (3n+1 Problem)', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"📊 Plot saved to: {save_path}")
            else:
                plt.show()
                
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error plotting Collatz trajectories: {e}")
            return False
    
    def plot_comparative_sequences(self, sequences_dict: dict, title: Optional[str] = None,
                                  save_path: Optional[str] = None) -> bool:
        """
        Plot multiple sequences for comparison.
        
        Args:
            sequences_dict: Dictionary with sequence names as keys and lists as values
            title: Optional title for the plot
            save_path: Optional path to save the plot
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            plt.figure(figsize=(12, 8))
            
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
            
            for i, (name, sequence) in enumerate(sequences_dict.items()):
                color = colors[i % len(colors)]
                x_vals = list(range(len(sequence)))
                plt.plot(x_vals, sequence, 'o-', linewidth=2, markersize=4,
                        color=color, label=name)
            
            plt.xlabel('n', fontsize=12)
            plt.ylabel('Value', fontsize=12)
            
            if title:
                plt.title(title, fontsize=14, fontweight='bold')
            else:
                plt.title('Comparative Sequences', fontsize=14, fontweight='bold')
                
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"📊 Plot saved to: {save_path}")
            else:
                plt.show()
                
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error plotting comparative sequences: {e}")
            return False

def create_output_directory():
    """Create output directory for saving plots."""
    output_dir = "math_plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir
