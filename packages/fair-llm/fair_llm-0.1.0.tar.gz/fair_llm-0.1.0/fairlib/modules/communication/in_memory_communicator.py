from typing import Optional, List, Dict
from collections import defaultdict
from fairlib.core.interfaces.communicator import AbstractCommunicator
from fairlib.core.message import Message

class InMemoryCommunicator(AbstractCommunicator):
    """
    An in-memory implementation of the AbstractCommunicator for single-process,
    multi-agent communication.

    This communicator uses a simple dictionary of lists to act as a message
    bus. Each agent has a dedicated message queue (a list) identified by its ID.
    When a message is sent to an agent, it is appended to that agent's list.
    When an agent checks for messages, it retrieves them from its list.

    This implementation is ideal for testing and for applications where all
    agents are running within the same Python process.
    """
    def __init__(self):
        # A dictionary where each value is a list (message queue) for an agent.
        self._message_queues: Dict[str, List[Message]] = defaultdict(list)
        self._registered_agents: List[str] = []

    def register_agent(self, agent_id: str):
        """Registers an agent with the communication system."""
        if agent_id not in self._registered_agents:
            self._registered_agents.append(agent_id)

    def send_message(self, recipient_agent_id: str, message: Message):
        """Appends a message to the recipient's queue."""
        print(f"COMMUNICATOR: Queuing message from {message.sender_id} to {recipient_agent_id}")
        self._message_queues[recipient_agent_id].append(message)

    async def asend_message(self, recipient_agent_id: str, message: Message):
        """Asynchronously appends a message to the recipient's queue."""
        self.send_message(recipient_agent_id, message)

    def receive_message(self, agent_id: str) -> Optional[Message]:
        """Retrieves and removes the oldest message from the agent's queue."""
        if self._message_queues[agent_id]:
            message = self._message_queues[agent_id].pop(0)
            print(f"COMMUNICATOR: Agent {agent_id} received message from {message.sender_id}")
            return message
        return None

    async def areceive_message(self, agent_id: str) -> Optional[Message]:
        """Asynchronously retrieves the oldest message from the agent's queue."""
        return self.receive_message(agent_id)
        
    def broadcast(self, message: Message):
        """Sends a message to all registered agents except the sender."""
        print(f"COMMUNICATOR: Broadcasting message from {message.sender_id} to all agents.")
        for agent_id in self._registered_agents:
            if agent_id != message.sender_id:
                self.send_message(agent_id, message)