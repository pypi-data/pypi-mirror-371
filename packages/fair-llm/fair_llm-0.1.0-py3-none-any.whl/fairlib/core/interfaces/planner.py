import abc
from typing import List, Union, Tuple
from fairlib.core.message import Message, Thought, Action, FinalAnswer

class AbstractPlanner(abc.ABC):
    """
    An abstract interface for an agent's planner component.

    The Planner is the "brain" of the agent. Its primary responsibility is to
    analyze the current conversation history and decide on the next step. It
    encapsulates the fairlib.core.reasoning logic of the agent.

    A planner's decision can result in one of two outcomes:
    1.  A `FinalAnswer`: If the planner believes the user's request has been
        fully addressed and no more actions are needed.
    2.  A `(Thought, Action)` pair: If more work is needed, the planner generates:
        - A Thought: The textual reasoning behind the chosen action.
        - An Action: The specific tool to call and the input for that tool.
    """

    @abc.abstractmethod
    def plan(
        self, messages: List[Message], **kwargs
    ) -> Union[Tuple[Thought, Action], FinalAnswer]:
        """
        Synchronously determines the next step for the agent.

        Args:
            messages: A list of Message objects representing the full
                      conversation history.
            **kwargs: Placeholder for additional implementation-specific arguments.

        Returns:
            Either a FinalAnswer if the task is complete, or a tuple containing
            the agent's Thought and the next Action to execute.
        """
        ...

    @abc.abstractmethod
    async def aplan(
        self, messages: List[Message], **kwargs
    ) -> Union[Tuple[Thought, Action], FinalAnswer]:
        """
        Asynchronously determines the next step for the agent.

        This is the asynchronous version of `plan` and should be preferred in
        asyncio applications to avoid blocking the event loop.

        Args:
            messages: A list of Message objects representing the full
                      conversation history.
            **kwargs: Placeholder for additional implementation-specific arguments.

        Returns:
            Either a FinalAnswer if the task is complete, or a tuple containing
            the agent's Thought and the next Action to execute.
        """
        ...