# fairlib.py
"""
================================================================================
                    FAIR-LLM Framework Central API
================================================================================

Purpose:
This module serves as the primary, user-facing API for the FAIR-LLM framework.
Its goal is to simplify development by providing a single, convenient location
to import all essential classes, tools, and components needed to build
sophisticated agentic applications.

Instead of navigating the entire module structure, developers can get started
quickly by importing directly from this 'fairlib' module.

For example:
    from fairlib import (
        settings,
        SimpleAgent,
        ReActPlanner,
        OpenAIAdapter,
        SafeCalculatorTool
    )

--------------------------------------------------------------------------------

Architecture: Lazy Loading with Static Typing Support

This module uses an advanced design pattern to provide both high performance at
runtime and a great developer experience in modern IDEs.

1.  On-Demand (Lazy) Loading:
    At runtime, this module uses Python's '__getattr__' function to load
    components only when they are first requested. This results in faster
    application startup and lower memory usage, as only the necessary parts of
    the framework are loaded into memory.

2.  Static Analysis & IDE Support:
    To ensure that developer tools like linters, type checkers (e.g., MyPy),
    and IDE features (e.g., "Go to Definition", autocompletion) work correctly,
    this module uses a 'if typing.TYPE_CHECKING:' block. This block is ONLY
    processed by static analysis tools and is ignored at runtime. It contains
    standard imports for all components, allowing your IDE to understand the
    full structure of the 'fairlib' API.

This hybrid approach gives you the best of both worlds: a fast, efficient
framework at runtime and a fully-featured, discoverable API during development.
================================================================================
"""
import importlib
from typing import TYPE_CHECKING

# --- Eagerly Loaded Components ---
# These are the absolute fairlib.core. lightweight data structures that are fundamental
# to nearly every agentic process and have no heavy dependencies. They are
# imported directly at startup for immediate availability.
from fairlib.core.config import settings
from fairlib.core.types import Document
from fairlib.core.message import Message, Thought, Action, Observation, FinalAnswer

# --- Lazy Loading Configuration ---
# This dictionary maps the string names of components to the module paths where
# they are defined. The '__getattr__' function below uses this map to import
# components on-demand the first time they are accessed.
_LAZY_LOAD_MAP = {
    # Core Data Types (less common or more specialized)
    "FinalGrade": "fairlib.core.types",
    "GradingCriterion": "fairlib.core.types",

    # Prompt Engineering Infrastructure
    "PromptBuilder": "fairlib.core.prompts",
    "PromptItem": "fairlib.core.prompts",
    "RoleDefinition": "fairlib.core.prompts",
    "ToolInstruction": "fairlib.core.prompts",
    "WorkerInstruction": "fairlib.core.prompts",
    "FormatInstruction": "fairlib.core.prompts",
    "Example": "fairlib.core.prompts",
    "History": "fairlib.core.prompts",
    "UserRequest": "fairlib.core.prompts",
    "AgentCapability": "fairlib.core.prompts",

    # Core Interfaces (for type hinting and custom implementations)
    "AbstractChatModel": "fairlib.core.interfaces.llm",
    "AbstractPlanner": "fairlib.core.interfaces.planner",
    "AbstractTool": "fairlib.core.interfaces.tools",
    "AbstractToolRegistry": "fairlib.core.interfaces.tools",
    "AbstractMemory": "fairlib.core.interfaces.memory",
    "AbstractVectorStore": "fairlib.core.interfaces.memory",
    "AbstractRetriever": "fairlib.core.interfaces.memory",
    "AbstractEmbedder": "fairlib.core.interfaces.embedder",
    "AbstractPerception": "fairlib.core.interfaces.perception",
    "AbstractSecurityManager": "fairlib.core.interfaces.security",

    # Agent Primitives & Orchestrators
    "BaseAgent": "fairlib.core.base_agent",
    "SimpleAgent": "fairlib.modules.agent.simple_agent",
    "HierarchicalAgentRunner": "fairlib.modules.agent.multi_agent_runner",

    # Planners
    "ReActPlanner": "fairlib.modules.planning.react_planner",
    "SimpleReActPlanner": "fairlib.modules.planning.react_planner",
    "ManagerPlanner": "fairlib.modules.agent.multi_agent_runner",

    # Memory & RAG Components
    "WorkingMemory": "fairlib.modules.memory.base",
    "LongTermMemory": "fairlib.modules.memory.base",
    "SummarizingMemory": "fairlib.modules.memory.summarization",
    "ChromaDBVectorStore": "fairlib.modules.memory.vector_store",
    "InMemoryVectorStore": "fairlib.modules.memory.vector_store",
    "SentenceTransformerEmbedder": "fairlib.modules.memory.embedder",
    "DummyEmbedder": "fairlib.modules.memory.embedder",
    "SimpleRetriever": "fairlib.modules.memory.retriever",

    # Model Adapters (MAL)
    "OpenAIAdapter": "fairlib.modules.mal.openai_adapter",
    "AnthropicAdapter": "fairlib.modules.mal.anthropic_adapter",
    "OllamaAdapter": "fairlib.modules.mal.local_llama_adapter",
    "HuggingFaceAdapter": "fairlib.modules.mal.huggingface_adapter",

    # Tool Components
    "ToolRegistry": "fairlib.modules.action.tools.registry",
    "ToolExecutor": "fairlib.modules.action.executor",

    # Built-in Tools
    "SafeCalculatorTool": "fairlib.modules.action.tools.builtin_tools.safe_calculator",
    "AdvancedCalculusTool": "fairlib.modules.action.tools.advanced_calculus_tool",
    "WebSearcherTool": "fairlib.modules.action.tools.builtin_tools.web_searcher",
    "WeatherTool": "fairlib.modules.action.tools.builtin_tools.weather",
    "GraphingTool": "fairlib.modules.action.tools.graphing_tool",
    "WebDataExtractor": "fairlib.modules.action.tools.builtin_tools.data_extractor",

    # Autograder Tools
    "KnowledgeBaseQueryTool": "fairlib.modules.action.tools.knowledge_tool",
    "GradeEssayFromRubricTool": "fairlib.modules.action.tools.grading_tool",
    "GradeCodeFromRubricTool": "fairlib.modules.action.tools.grading_tool",
    "CodeExecutionTool": "fairlib.modules.action.tools.code_execution_tool",

    # Perception & Security
    "TextParser": "fairlib.modules.perception.text_parser",
    "EchoPreprocessor": "fairlib.modules.perception.echo_preprocessor",
    "BasicSecurityManager": "fairlib.modules.security.basic_security_manager",
}

# The public API exposed by this module. This list is used by features like
# tab-completion in IDEs and to define what `from fairlib import *` imports.
__all__ = [
    # Eagerly loaded components
    "settings",
    "Document",
    "Message",
    "Thought",
    "Action",
    "Observation",
    "FinalAnswer",
    # Lazily loaded components (all keys from the map)
    *_LAZY_LOAD_MAP.keys(),
]


# --- Static Typing and IDE Support Block ---
# This block is only processed by static analysis tools (like MyPy or the one
# in your IDE). It is completely ignored at runtime because 'typing.TYPE_CHECKING'
# is 'False' during normal execution. This allows us to have the performance
# benefits of lazy loading while keeping the developer experience benefits of
# static analysis and autocompletion.
if TYPE_CHECKING:
    # Eagerly re-import all components for the type checker.
    # This list should be kept in sync with the _LAZY_LOAD_MAP.

    # Core Data Types
    from fairlib.core.types import Document, FinalGrade, GradingCriterion
    
    # Prompt Engineering
    from fairlib.core.prompts import (
        PromptBuilder, PromptItem, RoleDefinition, ToolInstruction,
        WorkerInstruction, FormatInstruction, Example, History, UserRequest, AgentCapability
    )

    # Core Interfaces
    from fairlib.core.interfaces.llm import AbstractChatModel
    from fairlib.core.interfaces.planner import AbstractPlanner
    from fairlib.core.interfaces.tools import AbstractTool, AbstractToolRegistry
    from fairlib.core.interfaces.memory import (
        AbstractMemory, AbstractVectorStore, AbstractRetriever
    )
    from fairlib.core.interfaces.embedder import AbstractEmbedder
    from fairlib.core.interfaces.perception import AbstractPerception
    from fairlib.core.interfaces.security import AbstractSecurityManager
    
    # Agent Primitives & Orchestrators
    from fairlib.core.base_agent import BaseAgent
    from fairlib.modules.agent.simple_agent import SimpleAgent
    from fairlib.modules.agent.multi_agent_runner import HierarchicalAgentRunner
    
    # Planners
    from fairlib.modules.agent.multi_agent_runner import ManagerPlanner
    from fairlib.modules.planning.react_planner import ReActPlanner, SimpleReActPlanner
    
    # Memory & RAG Components
    from fairlib.modules.memory.base import LongTermMemory, WorkingMemory
    from fairlib.modules.memory.summarization import SummarizingMemory
    from fairlib.modules.memory.embedder import DummyEmbedder, SentenceTransformerEmbedder
    from fairlib.modules.memory.retriever import SimpleRetriever
    from fairlib.modules.memory.vector_store import ChromaDBVectorStore, InMemoryVectorStore
    
    # Model Adapters (MAL)
    from fairlib.modules.mal.anthropic_adapter import AnthropicAdapter
    from fairlib.modules.mal.huggingface_adapter import HuggingFaceAdapter
    from fairlib.modules.mal.local_llama_adapter import OllamaAdapter
    from fairlib.modules.mal.openai_adapter import OpenAIAdapter
    
    # Tool Components
    from fairlib.modules.action.executor import ToolExecutor
    from fairlib.modules.action.tools.registry import ToolRegistry
    
    # Built-in & Custom Tools
    from fairlib.modules.action.tools.builtin_tools.safe_calculator import SafeCalculatorTool
    from fairlib.modules.action.tools.advanced_calculus_tool import AdvancedCalculusTool
    from fairlib.modules.action.tools.builtin_tools.weather import WeatherTool
    from fairlib.modules.action.tools.builtin_tools.web_searcher import WebSearcherTool
    from fairlib.modules.action.tools.code_execution_tool import CodeExecutionTool
    from fairlib.modules.action.tools.grading_tool import (GradeCodeFromRubricTool,
                                                    GradeEssayFromRubricTool)
    from fairlib.modules.action.tools.knowledge_tool import KnowledgeBaseQueryTool
    from fairlib.modules.action.tools.graphing_tool import GraphingTool
    from fairlib.modules.action.tools.builtin_tools.data_extractor import WebDataExtractor
    
    # Perception & Security
    from fairlib.modules.perception.text_parser import TextParser
    from fairlib.modules.perception.echo_preprocessor import EchoPreprocessor
    from fairlib.modules.security.basic_security_manager import BasicSecurityManager

# --- Runtime Lazy Loading Mechanism ---

def __getattr__(name: str):
    """
    Module-level 'getattr' function (PEP 562).

    This function is called by the Python interpreter only when an attribute
    (e.g., a class or function name) is accessed from this module but is not
    found in the module's globals. It allows us to intercept the import and
    load the requested component on-demand from the _LAZY_LOAD_MAP.
    """
    if name in _LAZY_LOAD_MAP:
        module_path = _LAZY_LOAD_MAP[name]
        try:
            # Import the module where the requested component is defined.
            module = importlib.import_module(module_path)
            # Get the component (attribute) from the imported module.
            attribute = getattr(module, name)
            # Cache the loaded attribute in this module's globals. The next
            # time this attribute is accessed, it will be found directly, and
            # this function will not be called again for it.
            globals()[name] = attribute
            return attribute
        except ImportError as e:
            # Provide a helpful error message if the module path is incorrect.
            raise ImportError(f"Could not import {name} from {module_path}. Please check the path in fairlib/__init__.py.") from e
        except AttributeError:
            # Provide a helpful error message if the component name is not in the module.
             raise AttributeError(f"Could not find {name} in module {module_path}. Please check the class/function name.")

    # If the name is not in our map, raise the standard AttributeError.
    raise AttributeError(f"module '{__name__!r}' has no attribute '{name!r}'")


def __dir__():
    """
    Module-level '__dir__' function.

    This is used by features like 'dir()' and IDE autocompletion to know what
    names are available in this module. We return the '__all__' list to ensure
    that all lazily-loaded components are discoverable by developer tools.
    """
    return __all__