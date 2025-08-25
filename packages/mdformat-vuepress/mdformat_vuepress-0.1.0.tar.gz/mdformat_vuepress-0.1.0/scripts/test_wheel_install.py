#!/usr/bin/env python3
"""Test script for plugin integration via pyproject.toml configuration."""

import subprocess
import sys
import tempfile
import os
import textwrap
from pathlib import Path


def test_pyproject_integration():
    """Test that the plugin can be added via pyproject.toml and works with mdformat."""
    
    # Find the wheel file
    dist_dir = Path("dist")
    wheel_files = list(dist_dir.glob("*.whl"))
    
    if not wheel_files:
        print("❌ No wheel file found in dist/")
        return False
    
    wheel_file = wheel_files[0].resolve()
    print(f"🔍 Testing plugin integration with wheel: {wheel_file}")
    
    # Create temporary project directory
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()
        
        print("✅ Created test project directory")
        
        # Create venv and install project
        venv_path = project_path / ".venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # Get paths for the virtual environment
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:  # Unix-like
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        try:
            # First install our plugin wheel directly
            subprocess.run([str(pip_exe), "install", str(wheel_file)], check=True)
            print("✅ Plugin wheel installed")
            
            # Then install just mdformat (plugin is already installed)
            subprocess.run([str(pip_exe), "install", "mdformat"], check=True)
            print("✅ mdformat installed")
            
            # Verify plugin is discoverable by mdformat
            check_plugin = subprocess.run([
                str(python_exe), "-c", 
                """
import pkg_resources
import mdformat_vuepress.plugin

# Check if entry point is registered
eps = list(pkg_resources.iter_entry_points('mdformat.parser_extension', 'vuepress'))
if not eps:
    eps = list(pkg_resources.iter_entry_points('mdformat.plugins', 'vuepress'))

if eps:
    print(f'Plugin entry point found: {eps[0]}')
else:
    print('No plugin entry point found')
    exit(1)

# Test that plugin module loads
assert hasattr(mdformat_vuepress.plugin, 'update_mdit')
print('Plugin module loads correctly')
                """
            ], capture_output=True, text=True, check=True)
            print("✅ Plugin is properly registered and discoverable")
            
            # Test actual mdformat functionality
            test_content = """::: tip Custom Title
Test container content with **markdown**
:::

# Regular Heading

Regular paragraph."""
            
            test_file = project_path / "test.md"
            test_file.write_text(test_content)
            
            # Run mdformat (plugin should be auto-discovered)
            subprocess.run([str(python_exe), "-m", "mdformat", str(test_file)], 
                         check=True)
            
            # Verify content
            formatted_content = test_file.read_text()
            
            # Check that VuePress containers are preserved
            if ("::: tip Custom Title" in formatted_content and 
                "Test container content with **markdown**" in formatted_content and
                "# Regular Heading" in formatted_content):
                print("✅ Plugin functionality works via pyproject.toml integration")
                return True
            else:
                print("❌ Plugin test failed - content not preserved correctly")
                print(f"Formatted content:\n{formatted_content}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Integration test failed: {e}")
            if e.stdout:
                print(f"stdout: {e.stdout}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            return False


if __name__ == "__main__":
    success = test_pyproject_integration()
    sys.exit(0 if success else 1)