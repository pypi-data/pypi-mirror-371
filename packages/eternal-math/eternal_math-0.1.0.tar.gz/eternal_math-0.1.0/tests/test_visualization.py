"""
Test cases for visualization module.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from eternal_math.visualization import MathVisualizer, create_output_directory


class TestMathVisualizer(unittest.TestCase):
    """Test cases for MathVisualizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = MathVisualizer()
        
    def test_visualizer_initialization(self):
        """Test visualizer initialization."""
        self.assertIsInstance(self.visualizer, MathVisualizer)
        self.assertEqual(self.visualizer.figure_size, (10, 6))
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.close')
    def test_plot_function_simple(self, mock_close, mock_show):
        """Test plotting a simple function."""
        result = self.visualizer.plot_function("x**2")
        self.assertTrue(result)
        mock_show.assert_called_once()
        mock_close.assert_called_once()
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.close')
    def test_plot_function_trigonometric(self, mock_close, mock_show):
        """Test plotting trigonometric function."""
        result = self.visualizer.plot_function("sin(x)")
        self.assertTrue(result)
        mock_show.assert_called_once()
        mock_close.assert_called_once()
    
    def test_plot_function_invalid_expression(self):
        """Test plotting with invalid expression."""
        result = self.visualizer.plot_function("invalid_func(x)")
        self.assertFalse(result)
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.close')
    def test_plot_sequence(self, mock_close, mock_show):
        """Test plotting a sequence."""
        sequence = [1.0, 1.0, 2.0, 3.0, 5.0, 8.0]
        result = self.visualizer.plot_sequence(sequence, title="Test Sequence")
        self.assertTrue(result)
        mock_show.assert_called_once()
        mock_close.assert_called_once()
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.close')
    def test_plot_prime_distribution(self, mock_close, mock_show):
        """Test plotting prime distribution."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        result = self.visualizer.plot_prime_distribution(primes, 30)
        self.assertTrue(result)
        mock_show.assert_called_once()
        mock_close.assert_called_once()
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.close')
    def test_plot_collatz_trajectory(self, mock_close, mock_show):
        """Test plotting Collatz trajectories."""
        sequences = [[3, 10, 5, 16, 8, 4, 2, 1], [7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]]
        starting_values = [3, 7]
        result = self.visualizer.plot_collatz_trajectory(sequences, starting_values)
        self.assertTrue(result)
        mock_show.assert_called_once()
        mock_close.assert_called_once()
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.close')
    def test_plot_comparative_sequences(self, mock_close, mock_show):
        """Test plotting comparative sequences."""
        sequences = {
            "Fibonacci": [1.0, 1.0, 2.0, 3.0, 5.0],
            "Primes": [2.0, 3.0, 5.0, 7.0, 11.0]
        }
        result = self.visualizer.plot_comparative_sequences(sequences, title="Test Comparison")
        self.assertTrue(result)
        mock_show.assert_called_once()
        mock_close.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_function_save_to_file(self, mock_close, mock_savefig):
        """Test saving plot to file."""
        result = self.visualizer.plot_function("x**2", save_path="test_plot.png")
        self.assertTrue(result)
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()
    
    def test_create_output_directory(self):
        """Test output directory creation."""
        # Test with mock to avoid creating actual directory
        with patch('os.path.exists') as mock_exists, \
             patch('os.makedirs') as mock_makedirs:
            
            mock_exists.return_value = False
            result = create_output_directory()
            
            self.assertEqual(result, "math_plots")
            mock_makedirs.assert_called_once_with("math_plots")


class TestVisualizationIntegration(unittest.TestCase):
    """Integration tests for visualization with number theory functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = MathVisualizer()
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.close')
    def test_fibonacci_sequence_visualization(self, mock_close, mock_show):
        """Test visualizing Fibonacci sequence."""
        from eternal_math import fibonacci_sequence
        
        fib_seq = fibonacci_sequence(10)
        fib_floats = [float(x) for x in fib_seq]
        
        result = self.visualizer.plot_sequence(fib_floats, title="Fibonacci Sequence")
        self.assertTrue(result)
        mock_show.assert_called_once()
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.close')
    def test_prime_generation_visualization(self, mock_close, mock_show):
        """Test visualizing prime numbers."""
        from eternal_math import sieve_of_eratosthenes
        
        primes = sieve_of_eratosthenes(50)
        result = self.visualizer.plot_prime_distribution(primes, 50)
        self.assertTrue(result)
        mock_show.assert_called_once()


if __name__ == '__main__':
    # Run with reduced output to avoid matplotlib backend issues in testing
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    
    unittest.main()
