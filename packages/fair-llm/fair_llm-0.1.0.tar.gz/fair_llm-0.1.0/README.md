
# **FAIR-LLM: A Flexible, Agnostic, and Interoperable Reasoning Framework**

FAIR-LLM is a Python framework designed to accelerate the development of powerful, consistent, and modular agentic applications. It provides a structured, interface-driven architecture that allows developers to easily build and customize agents with sophisticated reasoning capabilities, long-term memory, and collaborative multi-agent systems. Crafted to help engineers build powerful AI systems—without vendor lock-in.

## **Core Principles**

The FAIR framework is built on four core principles that guide its architecture and empower developers:

  * **Flexible**: The framework is highly modular. Every core component is built upon an abstract interface, allowing developers to easily swap implementations (e.g., swapping a simple memory system for a summarizing one) without altering the agent's core logic.
  * **Agnostic**: You are not locked into a single LLM provider. The Model Abstraction Layer (MAL) enables seamless switching between different models—from OpenAI and Anthropic to local models via HuggingFace or Ollama—ensuring you can always use the best tool for the job.
  * **Interoperable**: Components are designed to work together seamlessly. A standardized set of data structures, like the `Message` and `Document` types, ensures that data flows consistently between the agent's memory, planner, and tools.
  * **Reasoning**: At its heart, the framework is built to support sophisticated reasoning patterns. The default `ReActPlanner` allows agents to "think" step-by-step to solve complex problems, and the architecture is extensible enough to support more advanced paradigms like "Plan-and-Execute".

## **Key Features**

  * ** Advanced Agent Patterns**: Built-in support for the powerful **ReAct (Reason+Act)** cognitive cycle, allowing agents to reason about a problem, select a tool, and use the observation from that tool to inform their next step.
  * ** Multi-Agent Collaboration**: Orchestrate teams of specialized agents with a hierarchical manager-worker architecture. The `HierarchicalAgentRunner` and `ManagerPlanner` allow a lead agent to delegate sub-tasks to workers, enabling the system to tackle complex, multi-faceted problems.
  * ** Retrieval-Augmented Generation (RAG)**: Easily ground agents in your own documents and data. The framework includes all necessary components for a robust RAG pipeline, including document loaders, text splitters, embedders (`SentenceTransformerEmbedder`), and a queryable vector store (`ChromaDBVectorStore`) made available to the agent through the `KnowledgeBaseQueryTool`.
  * ** Pluggable Model Support**: The **Model Abstraction Layer (MAL)** features concrete adapters for **OpenAI**, **Anthropic**, **HuggingFace Transformers**, and **Ollama**, allowing for unparalleled flexibility in model selection.
  * ** Modular & Extensible by Design**: Every core component (LLM, Memory, Tools, Planner) is defined by an `Abstract` base class in the `core/interfaces` directory. This interface-driven design makes the framework easy to extend and customize.
  * ** Secure by Design**: The framework includes foundational components for security, such as the `BasicSecurityManager` for input validation and explicit warnings and placeholders for sandboxed tool execution to mitigate risks.
  * ** Reliable Structured Output**: Comes with patterns and demos (see `demo_structured_output.py`) for compelling LLMs to return clean, Pydantic-validated JSON, which is essential for reliable data extraction and tool integration.

## **Getting Started: Your First Agent (5-Minute Quickstart)**

Follow these steps to get your first agent running.

### 1\. Prerequisites

  * Python 3.12+
  * Git

### 2\. Installation

Clone the repository and install the required dependencies. It is highly recommended to use a virtual environment.

```bash
pip install fair-llm
```


### 3\. Configuration

The framework uses a centralized configuration file for API keys and model settings.

1.  Navigate to the `config/` directory.
2.  Create a copy of `settings.yml.template` and name it `settings.yml`.
3.  Open your new `settings.yml` file and add your API keys (e.g., for OpenAI).

### 4\. Run Your First Agent

The following code assembles and runs a simple agent that can use a calculator. Save it as `main.py` in the root of the project directory.

```python
# main.py
import asyncio
from fairlib import (
    settings,
    OpenAIAdapter,
    ToolRegistry,
    SafeCalculatorTool,
    ToolExecutor,
    WorkingMemory,
    ReActPlanner,
    SimpleAgent
)

async def main():
    print("Initializing a single agent...")

    # 1. The "Brain": Initialize the LLM adapter from the settings file
    llm = OpenAIAdapter(
        api_key=settings.api_keys.openai_api_key,
        model_name=settings.models["openai_gpt4"].model_name
    )

    # 2. The "Toolbelt": Create a registry and add tools
    tool_registry = ToolRegistry()
    tool_registry.register_tool(SafeCalculatorTool())

    # 3. The "Hands": Create an executor that uses the toolbelt
    executor = ToolExecutor(tool_registry)

    # 4. The "Memory": Set up short-term memory for the conversation
    memory = WorkingMemory()

    # 5. The "Mind": Create the planner that uses the brain and tools
    planner = ReActPlanner(llm, tool_registry)

    # 6. Assemble the Agent: Combine all parts into a functional unit
    agent = SimpleAgent(
        llm=llm,
        planner=planner,
        tool_executor=executor,
        memory=memory
    )
    print("✅ Agent created. Ask a math question or type 'exit'.")

    # 7. Run the agent in a loop
    while True:
        try:
            user_input = input("\n👤 You: ")
            if user_input.lower() == "exit":
                break
            response = await agent.arun(user_input)
            print(f"🤖 Agent: {response}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    asyncio.run(main())
```

Run the agent from your terminal:

```bash
python main.py
```

## **🏛️ Framework Architecture**

(Note: Not all areas are listed and explained here.)

The FAIR Agentic Framework is organized into a modular architecture. Below is an overview of the most critical components:

  * `core/`: Contains the architectural DNA of the framework.
      * `interfaces/`: Abstract Base Classes that define the "contract" for every major component (e.g., `AbstractChatModel`, `AbstractPlanner`). This is the key to the framework's modularity.
      * `message.py`, `types.py`: Core data structures like `Message`, `Action`, and `Document` that flow between all components.
  * `modules/`: Contains the concrete implementations of the interfaces.
      * `mal/`: The **Model Abstraction Layer**, with adapters for different LLM providers.
      * `agent/`: Agent definitions (`SimpleAgent`) and multi-agent orchestrators (`HierarchicalAgentRunner`).
      * `planning/`: Reasoning engines like the `ReActPlanner`.
      * `action/`: The `ToolExecutor` and the library of `tools` an agent can use.
      * `memory/`: Short-term (`WorkingMemory`) and long-term (RAG components like `ChromaDBVectorStore`) memory systems.
      * `security/`: Security components like the `BasicSecurityManager`.
  * `config/`: Centralized YAML configuration files.
  * `utils/`: Misc. utility code that support various apps or modules.


## **📁 Folder Structure**

```
fair_llm/
├── fairlib/
│   ├── config/
│   │   └── settings.yml
│   ├── core/
│   │   ├── interfaces/
│   │   ├── base_agent.py
│   │   ├── config.py
│   │   ├── message.py
│   │   └── prompts.py
│   ├── modules/
│   │   ├── action/
│   │   │   └── tools/
│   │   ├── agent/
│   │   ├── communication/
│   │   ├── learning/
│   │   ├── mal/
│   │   ├── memory/
│   │   ├── perception/
│   │   ├── planning/
│   │   └── security/
│   └── utils/
├── demo/
│   ├── demo_advanced_calculator_calculus.py
│   ├── demo_committee_of_agents_coding_autograder.py
│   ├── demo_committee_of_agents_essay_autograder.py
│   ├── demo_model_comparison.py
│   ├── demo_multi_agent.py
│   ├── demo_rag_from_documents.py
│   ├── demo_single_agent_calculator.py
│   └── demo_structured_output.py
├── fairlib.py
└── README.md
```

