# fairlib.core.base_agent.py

from abc import ABC, abstractmethod

"""
This module defines the abstract base class for all agents in the FAIR-LLM
framework. It establishes the fundamental contract that all concrete agent
implementations must follow.
"""

class BaseAgent(ABC):
    """
    The abstract blueprint for an agent.

    This class is not meant to be instantiated directly. Instead, it should be
    inherited by concrete agent classes (e.g., `SimpleAgent`). Its purpose is to
    ensure that any agent created within the framework has a consistent,
    predictable structure and entry point.

    By defining an abstract `arun` method, we guarantee that every agent has a
    primary method for execution, which will contain its fairlib.core.reasoning loop
    (like a ReAct cycle, a plan-and-execute strategy, etc.).
    """

    # The `role_description` is a helpful attribute that can be used in
    # multi-agent systems to help a manager agent understand the capabilities
    # of its workers. It's good practice to set this on concrete agent instances.
    role_description: str = "An AI agent."

    @abstractmethod
    async def arun(self, user_input: str) -> str:
        """
        The primary asynchronous entry point for running the agent's logic.

        This method must be implemented by any concrete subclass. It should
        contain the agent's fairlib.core.reasoning and action loop.

        Args:
            user_input: The initial prompt or query from the user that kicks
                        off the agent's task.

        Returns:
            A string containing the final response from the agent after it has
            completed its task.
        """
        pass

