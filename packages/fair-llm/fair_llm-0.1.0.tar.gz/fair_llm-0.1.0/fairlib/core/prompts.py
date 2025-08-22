# fairlib.core.prompts.py
"""
================================================================================
                    Core Prompt Engineering Infrastructure
================================================================================

**Purpose:**
This module provides a structured, object-oriented system for building complex
prompts for language models. It moves beyond static f-string templates to a
composable and maintainable approach, treating prompt engineering as a fairlib.core.part
of the application's architecture.

**Key Components:**
- **PromptItem:** An abstract base class for any granular part of a prompt.
  Subclasses can be sorted and manipulated in lists.

- **PromptBuilder:** A flexible container for assembling PromptItem objects
  into a final prompt string. Its component lists (e.g., `tool_instructions`)
  are public attributes, allowing for direct access and manipulation.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import copy
import re
from datetime import datetime
from dataclasses import dataclass

from fairlib.core.base_agent import BaseAgent
from fairlib.core.message import Message
from fairlib.core.interfaces.tools import AbstractTool, AbstractToolRegistry

# --- Foundational PromptItem Class ---

class PromptItem(ABC):
    """An abstract base class for any component of a system prompt."""
    @abstractmethod
    def render(self) -> str:
        """Renders the component's content into a string."""
        pass

# --- Granular Item Implementations ---

class RoleDefinition(PromptItem):
    """Defines the agent's role, goal, and overall purpose."""
    def __init__(self, text: str):
        self.text = text
    def render(self) -> str:
        return self.text

class ToolInstruction(PromptItem):
    """Describes a single available tool."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    def render(self) -> str:
        return f"- {self.name}: {self.description}"

class WorkerInstruction(PromptItem):
    """Describes a single available worker agent."""
    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description
    def render(self) -> str:
        return f"- {self.name}: {self.role_description}"

class FormatInstruction(PromptItem):
    """Provides a single, specific instruction on how the LLM should format its response."""
    def __init__(self, text: str):
        self.text = text
    def render(self) -> str:
        return self.text

class Example(PromptItem):
    """Provides a single few-shot example to guide the LLM's behavior."""
    def __init__(self, text: str):
        self.text = text
    def render(self) -> str:
        return self.text
    
class DateContextMixin:
    """Mixin to add date context to any component"""
    
    @staticmethod
    def get_current_date_context() -> Dict[str, str]:
        """Get comprehensive date context"""
        now = datetime.now()
        return {
            "current_date": now.strftime("%Y-%m-%d"),
            "current_year": str(now.year),
            "current_month": now.strftime("%B"),
            "current_day": str(now.day),
            "date_context": f"Today is {now.strftime('%A, %B %d, %Y')}",
            "timestamp": now.isoformat()
        }
    
    def enhance_with_date(self, text: str) -> str:
        """Add date context to any text"""
        date_info = self.get_current_date_context()
        
        # Create a string with the current date information
        date_context = f" (Current date: {date_info['current_month']} {date_info['current_day']}, {date_info['current_year']})"
        
        # Append the date context to the original text
        enhanced = text + date_context
        return enhanced
    
@dataclass
class AgentCapability:
    """Structured description of what an agent can do"""
    name: str
    primary_function: str
    capabilities: List[str]
    limitations: List[str]
    input_format: str
    output_format: str
    example_tasks: List[str]
    delegation_keywords: List[str]  # Keywords that should trigger this agent
    tools: List[str]  # Names of tools this agent has access to

class History:
    """
    Renders the conversation history for inclusion in a prompt.

    This class plays a critical role in the ReAct loop by translating the
    agent's internal memory (a list of `Message` objects) into the specific
    textual format that the planner's Language Model is expecting to see.
    It deliberately formats certain message roles to match the patterns
    established in the planner's few-shot examples.
    """
    def __init__(self, history: List[Message]):
        """
        Initializes the History item.

        Args:
            history: A list of `Message` objects representing the conversation
                     and reasoning steps so far.
        """
        self.history = history

    def render(self) -> str:
        """
        Renders the list of messages into a single string.

        This method intelligently formats messages to align with the ReAct
        prompting style:
        - Messages with `role="user"` are prefixed with "User Request:".
        - Messages with `role="assistant"` are prefixed with "Thought:", as they
          represent the agent's internal reasoning.
        - Messages with `role="tool"` are prefixed with "Observation:", as they
          represent the result of an action.

        This explicit mapping is a deliberate design choice that is critical
        for ensuring the LLM can correctly parse the history and follow the
        Thought -> Action -> Observation pattern.

        Returns:
            A formatted string representing the conversation history, with each
            message on a new line, or a default string if the history is empty.
        """
        if not self.history:
            return "No history yet."

        rendered_parts = []
        for msg in self.history:
            if not hasattr(msg, 'role') or not hasattr(msg, 'content'):
                continue

            prefix = ""
            content = str(msg.content)

            # --- Remove the special case for role="tool" ---
            # The "Observation:" prefix is now added directly in the SimpleAgent.
            # We still map 'assistant' to 'Thought' for the SimpleReActPlanner's benefit.
            if msg.role == "user":
                prefix = "User Request:"
            elif msg.role == "assistant":
                # The assistant's messages contain either its thought or an observation.
                # We will now just use the raw content.
                rendered_parts.append(content)
                continue # Skip the generic prefix: content formatting
            
            if content.strip():
                 rendered_parts.append(f"{prefix} {content}")

        return "\n\n".join(rendered_parts)

# --- Refactored PromptBuilder ---

class PromptBuilder:
    """
    Assembles a system prompt and combines it with conversation history
    to create a structured list of messages for a chat model.
    """
    def __init__(self):
        self.role_definition: Optional[RoleDefinition] = None
        self.tool_instructions: List[ToolInstruction] = []
        self.worker_instructions: List[WorkerInstruction] = []
        self.format_instructions: List[FormatInstruction] = []
        self.examples: List[Example] = []
        self.date_context: DateContextMixin = DateContextMixin()

    def clone(self) -> 'PromptBuilder':
        """Creates a deep copy of this builder instance."""
        return copy.deepcopy(self)

    def add_tool_registry(self, tool_registry: AbstractToolRegistry):
        """Helper to populate tool instructions from a registry."""
        for name, tool in tool_registry.get_all_tools().items():
            self.tool_instructions.append(ToolInstruction(name, tool.description))

    def add_worker_dict(self, workers: Dict[str, BaseAgent]):
        """Helper to populate worker instructions from a dictionary."""
        for name, worker in workers.items():
            self.worker_instructions.append(WorkerInstruction(name, worker.role_description))
            
    def build_system_prompt_string(self) -> str:
        """
        Builds the static system prompt string from all configured items.
        This string contains the fairlib.core.instructions for the agent.
        """
        prompt_parts = []
        if self.role_definition:
            prompt_parts.append(f"# --- Role and Goal ---\n{self.role_definition.render()}")
        if self.tool_instructions:
            rendered_tools = "\n".join([item.render() for item in self.tool_instructions])
            prompt_parts.append(f"# --- Available Tools ---\n{rendered_tools}")
        if self.worker_instructions:
            rendered_workers = "\n".join([item.render() for item in self.worker_instructions])
            prompt_parts.append(f"# --- Available Workers ---\n{rendered_workers}")
        if self.format_instructions:
            rendered_formats = "\n".join([item.render() for item in self.format_instructions])
            prompt_parts.append(f"# --- Output Format ---\n{rendered_formats}")
        if self.examples:
            rendered_examples = "\n\n".join([f"--- Example {i+1} ---\n{item.render()}" for i, item in enumerate(self.examples)])
            prompt_parts.append(f"# --- Example Workflows ---\n{rendered_examples}")
        if self.date_context:
            prompt_parts.append(f"# --- Current Date Information ---\n{self.date_context.get_current_date_context()}")
            
        return "\n\n".join(prompt_parts)

    def build_message_list(self, history: List[Message], user_input: str) -> List[Message]:
        """
        Constructs the final list of messages to be sent to the LLM using the
        native chat format.
        """
        messages = []
        system_prompt_content = self.build_system_prompt_string()
        
        if system_prompt_content:
            messages.append(Message(role="system", content=system_prompt_content))
        
        messages.extend(history)
        
        if user_input:
            messages.append(Message(role="user", content=user_input))
            
        return messages


# --- Standalone Demonstration ---
if __name__ == "__main__":
    # --- 1. Mock Objects for Demonstration ---
    # This allows us to run this script by itself to test the PromptBuilder.
    class MockTool(AbstractTool):

        def __init__(self, 
                     name: str = "Echo tool", 
                     description: str = "Just echos back user query"):
            self.name=name
            self.description=description

        def use(self, query: str) -> str:
            """
                echos back original query
            """

            # This is a hardcoded response for simulation purposes.
            # A real implementation would make an API call to a weather service here.
            return f"The mockup tool: {query}."

    class MockToolRegistry(AbstractToolRegistry):
        def __init__(self, name, description):
            self.name = name
            self.description = description

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

    # --- 2. Setup the Builder and Mock Data ---
    print("--- 🛠️ DEMONSTRATING PROMPT BUILDER 🛠️ ---")

    # Create a mock tool registry
    mock_registry = MockToolRegistry()
    mock_registry.register_tool(MockTool())
    mock_registry.register_tool(MockTool("weather_tool", "Gets the current weather for a city."))

    # Instantiate the builder
    builder = PromptBuilder()

    # --- 3. Manipulating the Prompt Items ---

    # Set the role directly
    builder.role_definition = RoleDefinition("You are a helpful AI assistant.")

    # Use the helper to add tools from the registry
    builder.add_tool_registry(mock_registry)

    # **MANUALLY ADD a tool instruction** (your requested feature)
    # This is for the "final_answer" pseudo-tool which isn't in the registry.
    final_answer_tool = ToolInstruction(
        name="final_answer",
        description="Use this tool to provide the final, complete answer to the user and end the task."
    )
    builder.tool_instructions.append(final_answer_tool)
    print("\n✅ Manually added 'final_answer' to tool instructions.")

    # **ACCESS and ENUMERATE a list**
    print("\nIterating over current tool instructions:")
    for tool in builder.tool_instructions:
        print(f"  - Found tool: {tool.name}")

    # **REMOVE an item from a list**
    # Let's remove the weather tool.
    tool_to_remove = next((t for t in builder.tool_instructions if t.name == "weather_tool"), None)
    if tool_to_remove:
        builder.tool_instructions.remove(tool_to_remove)
        print(f"\n✅ Removed '{tool_to_remove.name}' from tool instructions.")

    # **MANUALLY ADD to other lists**
    builder.format_instructions.append(
        FormatInstruction("Your response must contain a 'Thought' and an 'Action' part.")
    )
    builder.format_instructions.append(
        FormatInstruction("The 'Action' part must be a single, valid JSON object.")
    )
    print("\n✅ Manually added two format instructions.")

    # Add other items
    builder.examples.append(Example("User: What is 2+2?\nThought: I should use the calculator.\nAction: {\"tool_name\": \"safe_calculator\", \"tool_input\": \"2+2\"}"))
    builder.history = History([Message("user", "Hello there!"), Message("assistant", "Hi! How can I help?"), Message("user", "What is the capital of France?")])

    # --- 4. Build and Print the Final Prompt ---
    final_prompt = builder.build_system_prompt_string()

    print("\n\n" + "="*50)
    print("      FINAL RENDERED PROMPT")
    print("="*50 + "\n")
    print(final_prompt)