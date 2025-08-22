# fairlib.core.message.py
"""
================================================================================
                        Core Data Structures Module
================================================================================

**Purpose:**
This module contains the fundamental data structures that represent the flow of
information and the internal state of an agent within the FAIR-LLM framework.
These classes are used consistently across all fairlib.modules.to ensure a common,
predictable language for communication and reasoning.

**Key Components:**

1.  **`Message` Dataclass:**
    -   This is the primary data structure for all conversational turns. It is
        used for communication between the user and the agent, between the agent
        and the language model, and between the agent and its tools.
    -   It standardizes the concept of a "turn" in a conversation, with clearly
        defined roles (user, assistant, system, tool).

2.  **ReAct Loop Dataclasses (`Thought`, `Action`, `Observation`, `FinalAnswer`):**
    -   These classes represent the distinct stages of the "Reason-Act" cognitive
        cycle.
    -   They are internal data structures primarily created and used by the
        `Planner` and `SimpleAgent` fairlib.modules.to manage the agent's step-by-step
        reasoning process. They provide a structured way to handle the agent's
        internal monologue and decisions before a final `Message` is produced.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional

# Defines the possible roles in a conversation, aligning with standards from
# major language model providers like OpenAI and Anthropic.
Role = Literal["user", "assistant", "system", "tool"]

@dataclass
class Message:
    """
    Represents a single message in a conversation. This is the fairlib.core.data object
    for all interactions that are stored in an agent's memory.
    """
   
    role: Role
    """
    The role of the entity that produced the message.
    - 'system': Sets up the context or instructions for the assistant.
    - 'user': Represents a message from the end-user.
    - 'assistant': A response or action from the language model.
    - 'tool': The result of a tool execution.
    """

    content: str
    """
    The textual content of the message. For a 'tool' role, this holds the
    output or observation from the tool execution.
    """
    
    tool_calls: Optional[List[Dict[str, Any]]] = None
    """
    Add the tool_calls attribute to support modern function/tool calling APIs.
    This field will hold the list of tools the model wants to call.
    """


    name: Optional[str] = None
    """
    Optional: The name of the tool that was called. This field should be populated only
    when the 'role' is 'tool', to identify which tool produced the 'content'.
    """
    
    tool_call_id: Optional[str] = None
    """
    Optional: A unique identifier for a tool call. When an assistant decides
    to use a tool, it can generate a `tool_call_id`. The subsequent 'tool'
    role message containing the result should use the same ID to link the
    request and the result. This is crucial for handling multiple tool calls
    in a single turn.
    """

    metadata: Dict[str, Any] = field(default_factory=dict)
    """
    An optional dictionary for any extra data or metadata associated with the
    message, such as timestamps, sources, or security logs. The `default_factory`
    ensures that a new empty dict is created for each instance if not provided.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the Message object into a dictionary.

        This is a crucial utility method used by prompt builders and other
        components that need a plain Python dictionary representation of the
        message, for example, to format it into a prompt string.
        """
        # asdict recursively converts dataclass instances to dicts.
        return asdict(self)

# --- ReAct Loop Data Structures ---
# The following classes provide a structured way to represent the internal
# state and decisions of an agent during a ReAct (Reason + Act) loop.
# These classes are not typically stored in memory directly but are used as
# transient objects within the agent's reasoning loop to pass structured
# information between the planner and the executor.

@dataclass
class Thought:
    """
    Represents the agent's internal reasoning or thought process. This is the
    "Reason" part of the "Reason-Act" cycle. It's the agent's "inner monologue"
    explaining why it's about to take a certain action.
    """
    text: str

@dataclass
class Action:
    """
    Represents the agent's decision to execute a specific tool. This is the
    "Act" part of the "Reason-Act" cycle.
    """
    # The name of the tool to be executed, which must match a name in the ToolRegistry.
    tool_name: str
    
    # The input to be passed to the tool. This can be a simple string or a
    # more complex object (like a dictionary), depending on what the tool expects.
    tool_input: Any

@dataclass
class Observation:
    """
    Represents the result or output obtained from executing a tool. This is the
    feedback the agent receives from its environment after taking an action.
    """
    # The name of the tool that was executed.
    tool_name: str

    # The string representation of the output from the tool.
    tool_output: str

@dataclass
class FinalAnswer:
    """
    Represents the agent's conclusive response to the user's request, signaling
    the end of a reasoning cycle.
    """
    # The final, synthesized answer to be presented to the user.
    text: str