"""Tests for the mdformat-vuepress plugin."""

import pytest
import mdformat


class TestVuePressPlugin:
    """Test VuePress container preservation."""

    def test_vuepress_tip_container(self):
        """Test that tip containers are preserved."""
        markdown = """::: tip
This is a tip container
:::"""
        
        formatted = mdformat.text(markdown)
        assert "::: tip" in formatted
        assert "This is a tip container" in formatted
        assert ":::" in formatted

    def test_vuepress_warning_container(self):
        """Test that warning containers are preserved."""
        markdown = """::: warning
This is a warning
:::"""
        
        formatted = mdformat.text(markdown)
        assert "::: warning" in formatted
        assert "This is a warning" in formatted

    def test_vuepress_danger_container(self):
        """Test that danger containers are preserved."""
        markdown = """::: danger
This is dangerous
:::"""
        
        formatted = mdformat.text(markdown)
        assert "::: danger" in formatted
        assert "This is dangerous" in formatted

    def test_multiple_containers(self):
        """Test multiple containers in same document."""
        markdown = """::: tip
First container
:::

::: warning
Second container
:::"""
        
        formatted = mdformat.text(markdown)
        assert "::: tip" in formatted
        assert "::: warning" in formatted
        assert "First container" in formatted
        assert "Second container" in formatted

    def test_nested_markdown_in_container(self):
        """Test that markdown inside containers is preserved."""
        markdown = """::: tip
# Heading in container

- List item 1
- List item 2

**Bold text**
:::"""
        
        formatted = mdformat.text(markdown)
        assert "::: tip" in formatted
        assert "# Heading in container" in formatted
        assert "- List item 1" in formatted
        assert "**Bold text**" in formatted

    def test_custom_container_types(self):
        """Test custom container types are preserved."""
        markdown = """::: details Custom Title
Custom content here
:::"""
        
        formatted = mdformat.text(markdown)
        assert "::: details Custom Title" in formatted
        assert "Custom content here" in formatted


class TestPluginInstallation:
    """Test plugin installation and loading."""

    def test_plugin_loads(self):
        """Test that the plugin loads without errors."""
        # This will fail if the plugin has import errors
        import mdformat_vuepress.plugin
        assert hasattr(mdformat_vuepress.plugin, 'update_mdit')

    def test_plugin_entry_points(self):
        """Test that entry points are correctly configured."""
        # Test that mdformat can format with our plugin
        markdown = "::: tip\nTest\n:::"
        try:
            result = mdformat.text(markdown)
            # Should not raise an exception
            assert isinstance(result, str)
        except Exception as e:
            pytest.fail(f"Plugin failed to process markdown: {e}")

    def test_plugin_preserves_standard_markdown(self):
        """Test that standard markdown still works."""
        markdown = """# Heading

This is a paragraph with **bold** text.

- List item
- Another item"""
        
        formatted = mdformat.text(markdown)
        assert "# Heading" in formatted
        assert "**bold**" in formatted
        assert "- List item" in formatted