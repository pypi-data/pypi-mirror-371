# action/tools/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

"""
This module defines the abstract base classes for Tools and Tool Registries.
These interfaces ensure that any new tool or registry will integrate seamlessly
with the framework's agent and executor components.
"""

class AbstractTool(ABC):
    """
    The abstract base class for all tools.

    By inheriting from this class, you can create tools as self-contained
    classes with their own state and logic. This is more powerful than simple
    function-based tools.
    """
    name: str
    description: str

    @abstractmethod
    def use(self, tool_input: str) -> str:
        """
        The primary method for executing the tool's logic.

        Args:
            tool_input: The string input provided by the agent for the tool.

        Returns:
            A string representing the result or observation from the tool.
        """
        pass


class AbstractToolRegistry(ABC):
    """
    An abstract interface for a class that manages a collection of tools.
    """
    @abstractmethod
    def register_tool(self, tool: AbstractTool):
        """Adds a tool to the registry."""
        pass

    @abstractmethod
    def get_tool(self, name: str) -> Optional[AbstractTool]:
        """Retrieves a single tool by its name."""
        pass

    @abstractmethod
    def get_all_tools(self) -> Dict[str, AbstractTool]:
        """Returns a dictionary of all registered tools."""
        pass

