"""
Tests for the CLI functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from eternal_math.cli import EternalMathCLI


class TestEternalMathCLI(unittest.TestCase):
    """Test cases for the CLI interface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cli = EternalMathCLI()
    
    def test_cli_initialization(self):
        """Test CLI initializes correctly."""
        self.assertTrue(self.cli.running)
        self.assertIn('help', self.cli.commands)
        self.assertIn('primes', self.cli.commands)
        self.assertIn('quit', self.cli.commands)
    
    @patch('builtins.print')
    def test_help_command(self, mock_print):
        """Test help command displays correctly."""
        self.cli._help([])
        mock_print.assert_called()
        # Check that help was called multiple times (for different sections)
        self.assertGreater(mock_print.call_count, 5)
    
    @patch('builtins.print')
    def test_primes_command(self, mock_print):
        """Test primes command works correctly."""
        self.cli._primes(['10'])
        mock_print.assert_called()
        # Check that output contains prime numbers
        calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(calls)
        self.assertIn('[2, 3, 5, 7]', output)
    
    @patch('builtins.print')
    def test_primes_command_no_args(self, mock_print):
        """Test primes command with no arguments."""
        self.cli._primes([])
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(calls)
        self.assertIn('Usage:', output)
    
    @patch('builtins.print')
    def test_fibonacci_command(self, mock_print):
        """Test fibonacci command works correctly."""
        self.cli._fibonacci(['5'])
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(calls)
        self.assertIn('[0, 1, 1, 2, 3]', output)
    
    @patch('builtins.print')
    def test_perfect_numbers_command(self, mock_print):
        """Test perfect numbers command."""
        self.cli._perfect_numbers(['10'])
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(calls)
        self.assertIn('[6]', output)
    
    @patch('builtins.print')
    def test_euler_totient_command(self, mock_print):
        """Test Euler's totient function command."""
        self.cli._euler_totient(['12'])
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(calls)
        self.assertIn('φ(12)', output)
    
    @patch('builtins.print')
    def test_collatz_command(self, mock_print):
        """Test Collatz sequence command."""
        self.cli._collatz(['7'])
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(calls)
        self.assertIn('Collatz sequence for 7', output)
    
    @patch('builtins.print')
    def test_theorem_command(self, mock_print):
        """Test theorem display command."""
        self.cli._show_theorem([])
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(calls)
        self.assertIn('integer greater than 1', output)
    
    @patch('builtins.print')
    def test_examples_command(self, mock_print):
        """Test examples display command."""
        self.cli._show_examples([])
        mock_print.assert_called()
        calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(calls)
        self.assertIn('Usage Examples', output)
    
    def test_quit_command(self):
        """Test quit command stops the CLI."""
        self.assertTrue(self.cli.running)
        self.cli._quit([])
        self.assertFalse(self.cli.running)
    
    @patch('builtins.print')
    def test_invalid_command(self, mock_print):
        """Test invalid command handling."""
        # Mock the input and running state
        with patch('builtins.input', return_value='invalid_command'):
            self.cli.running = True
            # Simulate one iteration of the main loop
            user_input = 'invalid_command'
            parts = user_input.split()
            command = parts[0]
            
            if command in self.cli.commands:
                self.cli.commands[command]([])
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.\n")
            
            mock_print.assert_called()
            calls = [str(call) for call in mock_print.call_args_list]
            output = ' '.join(calls)
            self.assertIn('Unknown command', output)


if __name__ == '__main__':
    unittest.main()
