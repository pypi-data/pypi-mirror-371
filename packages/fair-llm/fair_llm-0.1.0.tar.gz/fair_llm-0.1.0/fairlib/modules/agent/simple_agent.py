# fairlib.modules.agent/simple_agent.py

"""
================================================================================
                        The Simple Agent Module
================================================================================

**Purpose:**
This module contains the `SimpleAgent`, the primary concrete implementation of a
reasoning agent in the FAIR-LLM framework. It is the fairlib.core.workhorse that powers
most single-agent and worker-agent systems.

**How it Works:**
The `SimpleAgent` orchestrates the fundamental "cognitive cycle" of an AI agent.
It connects the "brain" (the Planner), the "hands" (the Tool Executor), and the
"memory" into a cohesive loop, allowing the agent to perform multi-step reasoning
to solve problems. This loop is commonly known as the ReAct (Reason + Act) pattern.
"""

import json
from typing import List, Optional

from fairlib.core.base_agent import BaseAgent
from fairlib.core.interfaces.executor import AbstractToolExecutor
from fairlib.core.interfaces.llm import AbstractChatModel
from fairlib.core.interfaces.memory import AbstractMemory
from fairlib.core.interfaces.planner import AbstractPlanner
from fairlib.core.message import Action, FinalAnswer, Message, Thought
from fairlib.core.prompts import AgentCapability

# this kinda violates a pure, abstract design - I'll need to fix this later.
from fairlib.modules.planning.react_planner import ReActPlanner, SimpleReActPlanner 


class SimpleAgent(BaseAgent):
    """
    An agent that uses a planner to reason and act in a loop. It can be
    configured to be stateful (for conversations) or stateless (for
    single-task execution as a worker).
    """
    def __init__(
        self,
        llm: AbstractChatModel,
        planner: AbstractPlanner,
        tool_executor: AbstractToolExecutor,
        memory: AbstractMemory,
        max_steps: int = 10,
        stateless: bool = False,
        capability: Optional['AgentCapability'] = None,
        role_description: Optional[str] = None
    ):
        """
        Initializes the SimpleAgent.

        Args:
            llm: The language model that powers the agent's planner.
            planner: The planning component that decides the next action.
            tool_executor: The component that executes tool actions.
            memory: The memory system for storing conversation history.
            max_steps: The maximum number of reasoning steps to prevent loops.
            stateless: If True, the agent clears its memory before each run,
                       making it suitable as a worker agent. Defaults to False.
        """
        self.llm = llm
        self.planner = planner
        self.tool_executor = tool_executor
        self.memory = memory
        self.max_steps = max_steps
        self.stateless = stateless
        self.capability = capability
        self.role_description: str = "A helpful AI assistant."

    async def arun(self, user_input: str) -> str:
            """
            Runs the agent's main reasoning loop (the ReAct cycle).

            This method orchestrates the agent's entire process by repeatedly
            calling the planner and the tool executor. It is designed to be robust
            and handle both conversational (stateful) and worker (stateless) roles.

            The ReAct (Reason-Act-Observe) Cycle implemented here is as follows:
            1.  PLAN: The planner is called to generate a `Thought` and an `Action`
                based on the current history.
            2.  ACT: The `Action` (a tool call) is executed by the `ToolExecutor`.
            3.  OBSERVE: The result from the tool is formatted as an "Observation"
                and added back to memory to inform the next planning step.

            This cycle continues until the planner returns a `FinalAnswer` or the
            maximum number of steps is reached.

            Args:
                user_input: The input or query from the user that kicks off the task.

            Returns:
                The agent's final response as a string.
            """
            # For stateless worker agents, clear memory at the start of each task.
            if self.stateless:
                self.memory.clear()

            turn_messages: List[Message] = [Message(role="user", content=user_input)]
            current_request = user_input
            
            for step in range(self.max_steps):
                print(f"--- Step {step + 1}/{self.max_steps} ---")
                
                history = self.memory.get_history()
                
                # The planner generates a plan based on the history.
                plan_result = await self.planner.aplan(history, current_request)

                if isinstance(plan_result, FinalAnswer):
                    final_answer_text = plan_result.text
                    print(f"Thought: {final_answer_text}")
                    print("Action: Final Answer")
                    turn_messages.append(Message(role="assistant", content=final_answer_text))
                    for msg in turn_messages:
                        self.memory.add_message(msg)
                    return final_answer_text

                try:
                    thought, action = plan_result
                    print(f"Thought: {thought.text}")
                    print(f"Action: Using tool '{action.tool_name}' with input '{action.tool_input}'")
                except (ValueError, TypeError):
                    error_message = "Error: The planner returned a malformed response. Ending task."
                    print(error_message)
                    return error_message
                
                assistant_response_content = ""
                
                # --- Create a history message that matches the specific  planner's format ---

                # NOTE: This is a sort of fudge for now, need a better way of handling
                #       specific planner needs or requirements - the agent should not have to care.       
                if isinstance(self.planner, SimpleReActPlanner):
                    # Simple planner expects a plain text key-value format in history.             
                    assistant_response_content = (
                        f"Thought: {thought.text}\n"
                        f"Action:\n"
                        f"tool_name: {action.tool_name}\n"
                        f"tool_input: {action.tool_input}"
                    )
                else: # Default to the JSON format for the standard ReActPlanner
                    assistant_response_content = json.dumps(
                        {
                            "thought": thought.text,
                            "action": {
                                "tool_name": action.tool_name,
                                "tool_input": action.tool_input,
                            },
                        },
                        indent=4
                    )
                
                # Append the full, (correcly formatted) content to the history for this turn.
                turn_messages.append(Message(role="assistant", content=assistant_response_content))

                try:
                    observation_output = self.tool_executor.execute(action.tool_name, action.tool_input)
                    print(f"Observation: {observation_output}")
                except Exception as e:
                    observation_output = f"Error: {e}"
                    print(observation_output)

                # This creates the 'Observation' message for the LLM to react to in the next step.
                observation_message = Message(
                    role="system",
                    content=f"Observation: {str(observation_output)}"
                )
                turn_messages.append(observation_message)
                
                # Add all messages from this turn to the main memory.
                for msg in turn_messages:
                    self.memory.add_message(msg)

                turn_messages = []
                
                # Clear the user request after the first turn.
                current_request = ""

            final_response = "Agent stopped after reaching max steps."
            self.memory.add_message(Message(role="assistant", content=final_response))
            return final_response

