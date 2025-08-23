"""
Tests for the CLI module.
"""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner

from stfu.cli import main, show_welcome
from stfu.config import Config


class TestCLI:
    """Test cases for CLI functionality."""
    
    def test_show_welcome(self, capsys):
        """Test welcome message display."""
        show_welcome()
        captured = capsys.readouterr()
        assert "STFU" in captured.out
        assert "Terraform" in captured.out
    
    @patch('stfu.cli.TerraformWrapper')
    @patch('stfu.cli.UIRenderer')
    def test_main_with_args(self, mock_renderer, mock_terraform):
        """Test main function with terraform arguments."""
        runner = CliRunner()
        
        # Mock terraform execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_terraform.return_value.execute.return_value = mock_result
        
        result = runner.invoke(main, ['plan'])
        
        # Should not exit with error
        assert result.exit_code == 0
        mock_terraform.return_value.execute.assert_called_once_with(['plan'])
        mock_renderer.return_value.render.assert_called_once()
    
    def test_main_without_args(self):
        """Test main function without arguments shows welcome."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        
        assert result.exit_code == 0
        assert "STFU" in result.output
