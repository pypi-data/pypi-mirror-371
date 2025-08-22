import abc
from typing import Optional, List, Dict
from collections import defaultdict
from fairlib.core.message import Message  # Assuming Message is a defined type

class AbstractCommunicator(abc.ABC):
    """
    An abstract interface for message passing between agents.

    This class defines the essential contract for a communication system in a
    multi-agent framework. It ensures that agents can interact in a decoupled
    manner, allowing for different communication backbones (e.g., in-memory,
    networked, pub/sub) to be swapped in without changing the agents' fairlib.core.logic.
    """

    @abc.abstractmethod
    def send_message(self, recipient_agent_id: str, message: Message):
        """Sends a message to a specific agent."""
        ...

    @abc.abstractmethod
    async def asend_message(self, recipient_agent_id: str, message: Message):
        """Asynchronously sends a message to a specific agent."""
        ...

    @abc.abstractmethod
    def receive_message(self, agent_id: str) -> Optional[Message]:
        """Receives the next available message for a specific agent."""
        ...

    @abc.abstractmethod
    async def areceive_message(self, agent_id: str) -> Optional[Message]:
        """Asynchronously receives the next available message for a specific agent."""
        ...

    @abc.abstractmethod
    def broadcast(self, message: Message):
        """Sends a message to all agents in the system."""
        ...