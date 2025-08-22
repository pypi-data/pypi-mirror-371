# fairlib.modules.planning/react_planner.py
"""
================================================================================
                        ReAct Planner Module
================================================================================

**Purpose:**
This module provides the "brain" for an agent, containing the logic for how it
reasons and decides what to do next. It implements the ReAct (Reason + Act)
design pattern, which is a powerful technique for enabling language models to
solve complex problems by thinking step-by-step and using tools.

**Two Planners for Different Needs:**
This module contains two distinct planner classes to accommodate the wide range
of language models available:

1.  **`ReActPlanner` (for powerful models):**
    -   Uses a sophisticated prompt that requires the LLM to output its
        decision as a structured JSON object.
    -   Best For: High-end models like GPT-4, Claude 3 Opus, or other large,
        instruction-following models that reliably adhere to complex formatting
        rules.

2.  **`SimpleReActPlanner` (for smaller/local models):**
    -   Uses a simplified prompt that asks the LLM for a basic key-value
        pair format instead of strict JSON.
    -   Best For: Smaller, open-source models that may struggle with generating
        perfect JSON.

**Architectural Note:**
This version uses the native chat message format (a list of Message
objects) for interacting with LLMs. This is a more robust and modern approach
than compiling the entire context into a single system prompt string.
"""
import asyncio
import json
import re
import logging
from typing import Union, List, Tuple

# --- Core Framework Imports ---
from fairlib.core.interfaces.llm import AbstractChatModel
from fairlib.core.interfaces.planner import AbstractPlanner
from fairlib.core.interfaces.tools import AbstractToolRegistry
from fairlib.core.message import Message, Thought, Action, FinalAnswer

# --- Prompt Engineering Imports ---
from fairlib.core.prompts import (
    PromptBuilder,
    RoleDefinition,
    FormatInstruction,
    ToolInstruction,
    Example,
)

logger = logging.getLogger(__name__)


# --- Helper functions to create default prompt builders ---

def _create_default_json_builder() -> PromptBuilder:
    """
    Creates a robust, high-quality prompt builder for powerful, JSON-based models.

    This prompt is engineered for maximum consistency between the instructions
    and the agent's real-world behavior, preventing common ReAct failures. It
    explicitly tells the model that tool observations will arrive in 'system'
    messages, aligning it with the SimpleAgent's implementation.
    """
    builder = PromptBuilder()

    # --- 1. Define the Core Role and Goal ---
    builder.role_definition = RoleDefinition(
        "You are a precise, reasoning agent. Your purpose is to solve a user's request by breaking it down into a sequence of logical steps. At each step, you must reason about your goal and then act by selecting an appropriate tool."
    )

    # --- 2. Define the Strict JSON Output Structure ---
    # This section provides an unambiguous schema for the model's response.
    builder.format_instructions.extend([
        FormatInstruction(
            "# --- RESPONSE FORMAT (MANDATORY JSON) ---\n"
            "Your entire response MUST be a single, valid JSON object.\n"
            "This JSON object MUST have exactly two top-level keys: 'thought' and 'action'.\n\n"
            "1.  `thought`: A string explaining your reasoning for the current step.\n"
            "2.  `action`: An object containing the tool you will use, with two keys:\n"
            "    -   `tool_name`: The string name of the tool to use (e.g., 'safe_calculator' or 'final_answer').\n"
            "    -   `tool_input`: The string input for that tool."
        ),
        FormatInstruction(
            "# --- JSON RULES ---\n"
            "- ALWAYS use double quotes for all keys and string values.\n"
            "- Do NOT include any text or markdown formatting (like ```json) outside of the main JSON object."
        ),
            FormatInstruction(
        "# --- ABSOLUTE RULE ---\n"
        "Under NO circumstances should you ever respond with anything other than the JSON object described above. Your adherence to this format is non-negotiable."
    )
    ])

    # --- 3. Define the Explicit Reasoning Process ---
    # This resolves the original contradiction by correctly explaining how observations are received.
    builder.format_instructions.append(
        FormatInstruction(
            "# --- REASONING WORKFLOW ---\n"
            "1.  Analyze the user's request and the conversation history.\n"
            "2.  After using a tool, its result will appear as a 'system' message prefixed with 'Observation:'.\n"
            "3.  You MUST carefully analyze this observation to plan your next step.\n"
            "4.  If the observation provides the final answer, your ONLY next action is to use the 'final_answer' tool.\n"
            "5.  NEVER respond conversationally. Your ONLY output is the JSON object with your thought and action."
        )
    )

    # --- 4. Provide Clear, Consistent Examples ---
    # These examples perfectly match the rules and agent behavior, creating a reliable pattern.
    builder.examples.append(
        Example(
            '# --- Example 1: Simple, Single-Step Task ---\n'
            'user: "What is (100 + 50) / 25?"\n\n'
            'system: Observation: The result of \'(100 + 50) / 25\' is 6.0\n\n'
            'assistant: {\n'
            '    "thought": "I have received the result from the calculator, which is 6.0. This fully answers the user\'s request, so I can now provide the final answer.",\n'
            '    "action": {\n'
            '        "tool_name": "final_answer",\n'
            '        "tool_input": "The result of (100 + 50) / 25 is 6.0."\n'
            '    }\n'
            '}'
        )
    )
    builder.examples.append(
        Example(
            '# --- Example 2: Complex, Multi-Step Task ---\n'
            'user: "What is the weather in Paris, and what is the derivative of x**3?"\n\n'
            'system: Observation: The weather in Paris is 22°C and sunny.\n\n'
            'assistant: {\n'
            '    "thought": "I have successfully retrieved the weather in Paris. Now I need to address the second part of the request, which is to find the derivative of x**3. I will use the advanced_calculus_tool for this.",\n'
            '    "action": {\n'
            '        "tool_name": "advanced_calculus_tool",\n'
            '        "tool_input": "derivative(x**3, x)"\n'
            '    }\n'
            '}'
        )
    )
    return builder

def _create_default_simple_kv_builder() -> PromptBuilder:
    """
    Creates a direct and robust prompt builder for smaller or less instruction-
    compliant models.

    This prompt is engineered for maximum clarity and consistency to prevent
    common failure modes. It explicitly aligns the instructions and examples
    with the agent's actual behavior (i.e., receiving tool results in a
    'system' message).
    """
    builder = PromptBuilder()

    # --- 1. Define the Core Role ---
    # A simple, direct statement of the agent's purpose.
    builder.role_definition = RoleDefinition(
        "You are a helpful assistant that solves problems by reasoning and using tools in a step-by-step manner. You must strictly follow all formatting rules."
    )

    # --- 2. Define the Strict Output Format ---
    # This section dictates the exact key-value structure the model must output.
    # It is non-negotiable for the planner to parse the response correctly.
    builder.format_instructions.append(
        FormatInstruction(
            "# --- YOUR RESPONSE FORMAT (MANDATORY) ---\n"
            "On every turn, you MUST provide your reasoning in a 'Thought' and your action in an 'Action' block.\n"
            "Your response must use this exact key-value format:\n\n"
            "Thought: [Your analysis and step-by-step reasoning for what to do next.]\n"
            "Action:\n"
            "tool_name: [The name of the ONE tool to use, or 'final_answer']\n"
            "tool_input: [The input for that tool, or the complete final answer for the user.]\n\n"
            "==> IMPORTANT: Your response MUST end immediately after the 'tool_input:' line."
        )
    )

    # --- 3. Define the Explicit Decision-Making Process ---
    # This tells the model HOW to think. It resolves the fairlib.core.contradiction by
    # correctly stating that observations come from a 'system' message.
    builder.format_instructions.append(
        FormatInstruction(
            "# --- YOUR REASONING PROCESS ---\n"
            "1.  First, look at the user's request to understand their ultimate goal.\n"
            "2.  Next, look at the most recent 'system' message in the history. This is the 'Observation' from your last action.\n"
            "3.  If this Observation contains the complete answer to the user's goal, your action MUST be to use the 'final_answer' tool.\n"
            "4.  If the Observation is not enough, you MUST choose another tool to get closer to the solution."
        )
    )

    # --- 4. Provide Clear, Consistent Examples ---
    # These examples perfectly match the rules defined above, creating a
    # consistent and easy-to-follow pattern for the model.

    # A single-step example demonstrating the basic loop.
    builder.examples.append(
        Example(
            "# --- Example 1: Single-Step Calculation ---\n"
            "user: What is 50 multiplied by 3?\n"
            "assistant: "
            "Thought: The user wants to multiply 50 by 3. I will use the safe_calculator tool for this.\n"
            "Action:\n"
            "tool_name: safe_calculator\n"
            "tool_input: 50 * 3\n"
            "\n"
            "system: Observation: The result of '50 * 3' is 150.\n"
            "assistant: "
            "Thought: I have the result from the calculator, which is 150. This fully answers the user's request, so I will use the final_answer tool.\n"
            "Action:\n"
            "tool_name: final_answer\n"
            "tool_input: The result of 50 multiplied by 3 is 150."
        )
    )

    # A multi-step example to demonstrate sequential tool use.
    builder.examples.append(
        Example(
            "# --- Example 2: Multi-Step Calculation ---\n"
            "user: What is the derivative of x**2, and then what is the integral of that result?\n"
            "assistant: "
            "Thought: The user has a two-part request. First, I need to find the derivative of x**2. I will use the advanced_calculus_tool for this first step.\n"
            "Action:\n"
            "tool_name: advanced_calculus_tool\n"
            "tool_input: derivative(x**2, x)\n"
            "\n"
            "system: Observation: The derivative of x**2 with respect to x is: 2*x\n"
            "assistant: "
            "Thought: I have the result of the first step, which is 2*x. Now I need to perform the second step, which is to find the integral of 2*x. I will use the advanced_calculus_tool again.\n"
            "Action:\n"
            "tool_name: advanced_calculus_tool\n"
            "tool_input: integral(2*x, x)\n"
            "\n"
            "system: Observation: The indefinite integral of 2*x with respect to x is: x**2\n"
            "assistant: "
            "Thought: I have the result of the second step. I have now completed all parts of the user's request. I can provide the final answer.\n"
            "Action:\n"
            "tool_name: final_answer\n"
            "tool_input: The derivative of x**2 is 2*x. The integral of that result is x**2."
        ))
    
    return builder

class ReActPlanner(AbstractPlanner):
    """
    The standard ReAct planner, designed for powerful, JSON-compliant models.
    It uses the native chat format to communicate with the LLM.
    """
    def __init__(self, llm: AbstractChatModel, 
                 tool_registry: AbstractToolRegistry, 
                 prompt_builder: PromptBuilder = None):
        
        """Initializes the ReActPlanner."""
        self.llm = llm
        self.tool_registry = tool_registry
        self.prompt_builder = prompt_builder or _create_default_json_builder()

    def _prepare_and_build_messages(self, history: List[Message], user_input: str) -> List[Message]:
        """
        A helper method to contain the logic for preparing and building the
        list of messages for the LLM. This avoids code duplication between
        plan and aplan.
        """
        local_builder = self.prompt_builder.clone()
        local_builder.add_tool_registry(self.tool_registry)
        local_builder.tool_instructions.append(
            ToolInstruction("final_answer", "Use this tool to provide the final answer when the task is complete.")
        )
        return local_builder.build_message_list(history, user_input)

    def plan(self, history: List[Message], user_input: str) -> Union[FinalAnswer, Tuple[Thought, Action]]:
        """
        Synchronously generates the next reasoning step. This is a wrapper
        around the async 'aplan' method for use in synchronous contexts.
        """
        return asyncio.run(self.aplan(history, user_input))

    async def aplan(self, history: List[Message], user_input: str) -> Union[FinalAnswer, Tuple[Thought, Action]]:
        """
        Asynchronously generates the next plan for the agent by building the
        prompt and calling the async LLM method.
        """
        # 1. Prepare the messages using the shared helper method.
        messages = self._prepare_and_build_messages(history, user_input)
        
        # 2. Call the asynchronous LLM method.
        response_message = await self.llm.ainvoke(messages)
        
        # 3. Parse the response.
        return self._parse_json_response(response_message.content)


    def _parse_json_response(self, response_text: str) -> Union[FinalAnswer, Tuple[Thought, Action]]:
            """
            Parses the raw response from the LLM, with intelligent fallback for
            conversational final answers.
            """
            try:
                # --- Primary Path: Handle a perfect JSON response ---
                response_data = json.loads(response_text.strip())
                thought_text = response_data.get("thought")
                action_data = response_data.get("action")

                if not thought_text or not action_data:
                    raise KeyError("The JSON response is missing 'thought' or 'action' keys.")

                tool_name = action_data.get("tool_name")
                tool_input = action_data.get("tool_input")

                if not tool_name or tool_input is None:
                    raise KeyError("The 'action' object is missing 'tool_name' or 'tool_input' keys.")

                thought = Thought(text=str(thought_text))

                if tool_name == "final_answer":
                    return FinalAnswer(text=str(tool_input))
                
                return thought, Action(tool_name=str(tool_name), tool_input=tool_input)

            except json.JSONDecodeError:
                # --- Fallback Path: Handle a conversational final answer ---
                # This is a common case where the LLM, especially after a successful
                # tool use, responds with a plain sentence instead of the required JSON.
                # We treat this as an implicit 'FinalAnswer'.
                logger.info(
                    "Response was not valid JSON. Assuming a conversational Final Answer. Response: '%s'",
                    response_text
                )
                return FinalAnswer(text=response_text)

            except (KeyError, TypeError) as e:
                # --- Fallback Path for malformed but valid JSON ---
                logger.warning(
                    "Could not parse ReAct JSON due to missing keys '%s'. Treating as Final Answer. Response: '%s'",
                    e,
                    response_text
                )
                return FinalAnswer(text=response_text)


class SimpleReActPlanner(AbstractPlanner):
    """A simplified ReAct planner for smaller models, using the native chat format."""
    def __init__(self, llm: AbstractChatModel, 
                 tool_registry: AbstractToolRegistry, 
                 prompt_builder: PromptBuilder = None):
        
        """Initializes the SimpleReActPlanner."""
        self.llm = llm
        self.tool_registry = tool_registry
        self.prompt_builder = prompt_builder or _create_default_simple_kv_builder()

    def _prepare_and_build_messages(self, history: List[Message], 
                                    user_input: str) -> List[Message]:
        """
        A helper method to prepare and build messages for the SimpleReActPlanner.
        """
        local_builder = self.prompt_builder.clone()
        local_builder.add_tool_registry(self.tool_registry)
        local_builder.tool_instructions.append(
            ToolInstruction("final_answer", "Use this to provide the final answer when all steps are complete.")
        )
        
        effective_input = user_input

        if not user_input and history:

            # This prompt defaults to finishing but allows for multi-step tasks.
            # It explicitly asks the LLM to check the original request for remaining steps.
            effective_input = (
                "The last step was successful. Review the original user request in the history. "
                "If all parts of the original request have been fully addressed by the observations, "
                "your ONLY action is to use the 'final_answer' tool to summarize the final result. "
                "If there are still remaining steps in the original request, perform the very next one."
            )
        
        return local_builder.build_message_list(history, effective_input)

    def plan(self, history: List[Message], 
             user_input: str) -> Union[FinalAnswer, Tuple[Thought, Action]]:
        
        """
        Synchronously generates the next reasoning step by wrapping the async version.
        """
        return asyncio.run(self.aplan(history, user_input))

    async def aplan(self, history: List[Message], 
                    user_input: str) -> Union[FinalAnswer, Tuple[Thought, Action]]:
        """
        Asynchronously generates the next plan for the agent.
        """
        # 1. Prepare messages using the shared helper.
        messages = self._prepare_and_build_messages(history, user_input)
        
        # 2. Call the async LLM method.
        response_message = await self.llm.ainvoke(messages)
        
        # 3. Parse the response.
        return self._parse_simplified_response(response_message.content)
    

    def _parse_simplified_response(self, 
                                   response_text: str) -> Union[FinalAnswer, Tuple[Thought, Action]]:
        """
        Parses the simplified key-value format, specifically looking for the
        first valid thought/action block to prevent runaway generation loops.
        """
        try:
            # --- Change the final (.*) to ([^\n]*) ---
            # This makes the tool_input non-greedy and forces it to stop at the
            # end of the line, preventing it from consuming a hallucinated response.
            pattern = r"Thought:(.*?)(?=Action:|$).*?Action:\s*tool_name:\s*(.*?)\s*tool_input:\s*([^\n]*)"
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)

            if not match:
                # Fallback for JSON or conversational responses
                # (Existing fallback logic remains here...)
                try:
                    response_data = json.loads(response_text.strip())
                    thought_text = response_data.get("thought")
                    action_data = response_data.get("action")
                    tool_name = action_data.get("tool_name")
                    tool_input = action_data.get("tool_input")
                    if not all([thought_text, action_data, tool_name, tool_input is not None]):
                        raise ValueError("JSON response is missing required keys.")
                except (json.JSONDecodeError, ValueError, AttributeError):
                     raise ValueError("Response is not a valid KV block or a parsable JSON object.")
            else:
                thought_text, tool_name, tool_input = match.groups()

            # Process the extracted data
            thought_text = thought_text.strip()
            tool_name = tool_name.strip()
            tool_input = tool_input.strip()
            
            if not tool_name: # tool_input can be empty for some tools
                raise ValueError("Empty tool_name found in parsed action.")
            
            thought = Thought(text=thought_text)
            
            if tool_name.lower() == "final_answer":
                return FinalAnswer(text=tool_input)
            else:
                return thought, Action(tool_name=tool_name, tool_input=tool_input)
                
        except ValueError as e:
            logger.warning(
                "Could not parse simplified ReAct response due to '%s'. Treating as Final Answer. Response: '%s'",
                e,
                response_text
            )
            return FinalAnswer(text=response_text)