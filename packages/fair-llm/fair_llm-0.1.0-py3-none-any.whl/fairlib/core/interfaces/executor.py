# fairlib.core.interfaces/executor.py

from abc import ABC, abstractmethod
from typing import Any
from fairlib.core.interfaces.tools import AbstractToolRegistry

"""
This module defines the abstract interface for a tool-executing component.
"""

class AbstractToolExecutor(ABC):
    """
    An abstract interface for a class that is responsible for executing tools.

    This decouples the agent's decision-making logic from the actual
    implementation of how a tool is run, allowing for different execution
    strategies (e.g., local, sandboxed, remote).
    """

    @abstractmethod
    def execute(self, tool_name: str, tool_input: str) -> str:
        """
        Synchronously executes a tool with the given input.

        Args:
            tool_name: The name of the tool to execute.
            tool_input: The input string for the tool.

        Returns:
            The result of the tool execution as a string.
        """
        pass

    async def aexecute(self, tool_name: str, tool_input: str) -> str:
        """
        Asynchronously executes a tool. By default, this runs the synchronous
        method, but can be overridden for true async execution.

        Args:
            tool_name: The name of the tool to execute.
            tool_input: The input string for the tool.

        Returns:
            The result of the tool execution as a string.
        """
        return self.execute(tool_name, tool_input)


