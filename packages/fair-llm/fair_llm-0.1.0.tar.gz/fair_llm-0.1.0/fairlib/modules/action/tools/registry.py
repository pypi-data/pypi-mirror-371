# action/tools/registry.py

from typing import Dict, Optional
from fairlib.core.interfaces.tools import AbstractTool, AbstractToolRegistry

"""
This module provides a concrete implementation of the AbstractToolRegistry.
"""

class ToolRegistry(AbstractToolRegistry):
    """
    A concrete implementation of a tool registry that holds and manages a
    collection of tools for an agent.

    This implementation allows for tools to be dynamically registered, making it
    flexible for creating agents with different capabilities.
    """
    def __init__(self):
        """Initializes the ToolRegistry with an empty dictionary to store tools."""
        self._tools: Dict[str, AbstractTool] = {}

    def register_tool(self, tool: AbstractTool):
        """
        Adds a tool instance to the registry, making it available for use.

        The tool is stored using its `name` attribute as the key.

        Args:
            tool: An instance of a class that inherits from AbstractTool.
        """
        if not tool.name:
            raise ValueError("Tool must have a name attribute.")
        print(f"Registering tool: {tool.name}")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[AbstractTool]:
        """
        Retrieves a single tool from the registry by its name.

        Args:
            name: The name of the tool to retrieve.

        Returns:
            The tool instance if found, otherwise None.
        """
        return self._tools.get(name)

    def get_all_tools(self) -> Dict[str, AbstractTool]:
        """
        Returns a dictionary of all tools currently in the registry.

        Returns:
            A dictionary where keys are tool names and values are the
            tool instances.
        """
        return self._tools

