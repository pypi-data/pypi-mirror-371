"""Integration tests for package installation and CLI functionality."""

import subprocess
import tempfile
import os
from pathlib import Path
import pytest


class TestPackageInstallation:
    """Test package installation and CLI integration."""

    def test_plugin_imports(self):
        """Test that the plugin can be imported without errors."""
        import mdformat_vuepress.plugin
        assert hasattr(mdformat_vuepress.plugin, 'update_mdit')

    def test_mdformat_cli_basic(self):
        """Test basic mdformat CLI functionality with VuePress containers."""
        test_content = """::: tip
Test container content
:::

Regular **markdown** text."""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Run mdformat on the file
            result = subprocess.run(['mdformat', temp_file], 
                                  capture_output=True, text=True, check=True)
            
            # Read the formatted content
            with open(temp_file, 'r') as f:
                formatted_content = f.read()
            
            # Verify VuePress containers are preserved
            assert "::: tip" in formatted_content
            assert "Test container content" in formatted_content
            assert ":::" in formatted_content
            
            # Verify regular markdown is present
            assert "**markdown**" in formatted_content
            
        finally:
            os.unlink(temp_file)

    def test_mdformat_cli_multiple_containers(self):
        """Test mdformat CLI with multiple VuePress containers."""
        test_content = """::: tip
First container
:::

# Regular heading

::: danger
Second container with **markdown**
:::"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Run mdformat
            subprocess.run(['mdformat', temp_file], check=True)
            
            # Read formatted content
            with open(temp_file, 'r') as f:
                formatted_content = f.read()
            
            # Count container markers (should be 4: 2 starts + 2 ends)
            container_count = formatted_content.count(":::")
            assert container_count == 4, f"Expected 4 container markers, got {container_count}"
            
            # Verify specific containers
            assert "::: tip" in formatted_content
            assert "::: danger" in formatted_content
            assert "First container" in formatted_content
            assert "Second container with **markdown**" in formatted_content
            
            # Verify regular markdown formatting
            assert "# Regular heading" in formatted_content
            
        finally:
            os.unlink(temp_file)

    def test_mdformat_cli_check_flag(self):
        """Test mdformat --check flag functionality."""
        test_content = """::: warning
Test container
:::"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # First format the file
            subprocess.run(['mdformat', temp_file], check=True)
            
            # Then check if it needs formatting (should not)
            result = subprocess.run(['mdformat', '--check', temp_file], 
                                  capture_output=True, text=True)
            
            # Should exit with code 0 (no changes needed)
            assert result.returncode == 0, "Formatted file should pass --check"
            
        finally:
            os.unlink(temp_file)

    def test_mdformat_stdin_pipe(self):
        """Test mdformat with stdin/stdout piping."""
        test_content = """::: info
Piped content
:::"""
        
        # Test piping through mdformat
        result = subprocess.run(['mdformat', '-'], 
                              input=test_content, 
                              capture_output=True, text=True, check=True)
        
        output = result.stdout
        assert "::: info" in output
        assert "Piped content" in output
        assert output.count(":::") == 2