#!/usr/bin/env python3
"""
Test script to verify core plugin loading functionality.
"""

import sys
import os
import importlib.util
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

from janito.plugin_system.base import Plugin, PluginMetadata


class CorePlugin(Plugin):
    """Simple core plugin implementation."""

    def __init__(self, name: str, description: str, tools: list):
        super().__init__()
        self.plugin_name = name
        self.plugin_description = description
        self.plugin_tools = tools
        self.tool_classes = []

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.plugin_name,
            version="1.0.0",
            description=self.plugin_description,
            author="Janito",
            license="MIT",
        )

    def get_tools(self) -> list:
        return self.tool_classes

    def initialize(self):
        """Initialize by creating tool classes."""
        from janito.tools.function_adapter import create_function_tool

        self.tool_classes = []
        for tool_func in self.plugin_tools:
            if callable(tool_func):
                tool_class = create_function_tool(tool_func)
                self.tool_classes.append(tool_class)


def load_core_plugin_fixed(plugin_name: str):
    """Fixed version of core plugin loader"""
    try:
        # Parse plugin name
        if "." not in plugin_name:
            return None

        parts = plugin_name.split(".")
        if len(parts) != 2:
            return None

        package_name, submodule_name = parts

        # Build path to plugin using absolute path
        base_dir = Path(__file__).parent  # Go to project root
        plugin_path = (
            base_dir / "janito" / "plugins" / "core" / submodule_name / "__init__.py"
        )

        if not plugin_path.exists():
            print(f"Plugin file not found: {plugin_path}")
            return None

        # Load the module
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec is None or spec.loader is None:
            print(f"Failed to create spec for: {plugin_name}")
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get plugin info
        name = getattr(module, "__plugin_name__", plugin_name)
        description = getattr(
            module, "__plugin_description__", f"Core plugin: {plugin_name}"
        )
        tools = getattr(module, "__plugin_tools__", [])

        if not tools:
            print(f"No tools found in: {plugin_name}")
            return None

        # Create plugin
        plugin = CorePlugin(name, description, tools)
        plugin.initialize()
        return plugin

    except Exception as e:
        print(f"Error loading core plugin {plugin_name}: {e}")
        return None


def main():
    """Test loading core plugins"""
    print("Testing core plugin loading...")

    # Test loading core plugins
    core_plugins = [
        "core.filemanager",
        "core.codeanalyzer",
        "core.system",
        "core.imagedisplay",
    ]

    loaded_plugins = []
    for plugin_name in core_plugins:
        print(f"\nLoading {plugin_name}...")
        plugin = load_core_plugin_fixed(plugin_name)
        if plugin:
            print(f"✓ Successfully loaded: {plugin.get_metadata().name}")
            print(f"  Tools: {len(plugin.get_tools())}")
            loaded_plugins.append(plugin_name)
        else:
            print(f"✗ Failed to load: {plugin_name}")

    print(f"\nTotal loaded: {len(loaded_plugins)} plugins")
    return loaded_plugins


if __name__ == "__main__":
    loaded = main()
