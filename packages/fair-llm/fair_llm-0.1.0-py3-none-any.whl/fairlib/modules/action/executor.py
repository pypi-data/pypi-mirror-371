# action/executor.py

from typing import Optional
# The import path for the interfaces has been corrected to be relative.
from fairlib.core.interfaces.executor import AbstractToolExecutor
from fairlib.core.interfaces.security import AbstractSecurityManager
from fairlib.core.interfaces.tools import AbstractToolRegistry, AbstractTool

class ToolExecutor(AbstractToolExecutor):
    """
    A concrete implementation of the AbstractToolExecutor. This class is
    responsible for safely finding and running tools that an agent decides
    to use. It acts as the "hands" of the agent, translating the agent's
    intent into a real action.
    """
    def __init__(self, tool_registry: AbstractToolRegistry, security_manager: Optional[AbstractSecurityManager] = None):
        """
        Initializes the ToolExecutor.

        Args:
            tool_registry: An object that holds all the tools available to the
                           agent. This is how the executor finds the correct
                           tool to run.
            security_manager: An optional security component that can validate
                              inputs before they are passed to a tool, providing
                              a layer of protection.
        """
        self.tool_registry = tool_registry
        self.security_manager = security_manager

    def execute(self, tool_name: str, tool_input: str) -> str:
        """
        Finds the specified tool in the registry and executes it with the
        given input.

        This method encapsulates the fairlib.core.logic of an agent's action phase:
        1. Find the tool.
        2. Perform a security check.
        3. Run the tool.
        4. Handle any errors gracefully.

        Args:
            tool_name: The name of the tool to execute, as decided by the
                       agent's planner.
            tool_input: The input string for the tool, also from the planner.

        Returns:
            A string representing the result (the "observation") of the tool's
            execution, or an error message if something went wrong.
        """
        # Step 1: Find the tool in the registry.
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            # If the agent hallucinates a tool that doesn't exist, we return
            # a clear error message. This is crucial feedback for the agent's
            # next reasoning step.
            return f"Error: Tool '{tool_name}' not found."

        # Step 2: (Optional) Security Validation Step.
        # If a security manager is configured, use it to validate the input
        # that the LLM generated for the tool. This helps prevent prompt
        # injection attacks where the LLM might be tricked into generating
        # malicious input for a sensitive tool.
        if self.security_manager and not self.security_manager.validate_input(tool_input):
            return f"Error: Input validation failed for tool '{tool_name}'. Execution halted."
            
        try:
            # Step 3: Run the tool.
            # We call the 'use' method as defined in the AbstractTool interface.
            # This is where the tool's actual logic is executed.
            result = tool.use(tool_input)

        except Exception as e:
            # Step 4: Handle any exceptions that occur during tool execution
            # gracefully. This prevents the entire agent from crashing and
            # provides useful feedback.
            return f"Error executing tool '{tool_name}': {e}"

        # Ensure the final output is always a string.
        return str(result)
