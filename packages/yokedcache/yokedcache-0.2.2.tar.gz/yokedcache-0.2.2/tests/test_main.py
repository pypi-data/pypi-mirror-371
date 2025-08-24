"""
Tests for the __main__.py module entry point.
"""

import subprocess
import sys
from unittest.mock import patch

import pytest


class TestMainModule:
    """Test the __main__.py module entry point."""

    def test_main_module_import(self):
        """Test that the main module can be imported."""
        import yokedcache.__main__
        assert hasattr(yokedcache.__main__, 'main')

    def test_main_module_execution(self):
        """Test that the main module can be executed."""
        with patch('yokedcache.__main__.main') as mock_main:
            # Import and execute the module
            import yokedcache.__main__
            
            # Simulate running as main
            with patch('yokedcache.__main__.__name__', '__main__'):
                exec(compile(open('src/yokedcache/__main__.py').read(), 'src/yokedcache/__main__.py', 'exec'))
            
            # The main function should have been called
            mock_main.assert_called_once()

    def test_main_module_cli_integration(self):
        """Test that running python -m yokedcache works."""
        # Test that the module can be run (will fail due to no Redis, but should import correctly)
        result = subprocess.run(
            [sys.executable, '-m', 'yokedcache', '--help'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        # Should show help text and exit with code 0
        assert result.returncode == 0
        assert 'Usage:' in result.output or 'usage:' in result.output.lower()

    def test_main_module_sys_import(self):
        """Test that sys is properly imported."""
        import yokedcache.__main__
        assert hasattr(yokedcache.__main__, 'sys')

    def test_main_module_cli_import(self):
        """Test that CLI main function is properly imported."""
        import yokedcache.__main__
        from yokedcache.cli import main
        assert yokedcache.__main__.main == main
