# fairlib.core.interfaces/model_manager.py
"""
This module defines the abstract interface for a Model Manager.

The Model Manager acts as a central registry and factory for accessing various
language models available within the framework. It decouples the rest of the
application from the specific details of how different model adapters are
instantiated and configured.
"""

import abc
from typing import List, Union
from .llm import AbstractChatModel, AbstractLanguageModel

class AbstractModelManager(abc.ABC):
    """
    An abstract interface for a class that manages access to language models.

    A concrete implementation of this class would handle loading model-specific
    configurations (e.g., API keys, model names) and providing initialized
    instances of the appropriate model adapter (e.g., OpenAIAdapter,
    HuggingFaceAdapter) on demand.
    """
    @abc.abstractmethod
    def get_model(self, model_id: str, model_type: str = "chat") -> Union[AbstractChatModel, AbstractLanguageModel]:
        """
        Retrieves an initialized instance of a specified language model.

        This method acts as a factory, returning a ready-to-use model object
        that conforms to one of the standard model interfaces.

        Args:
            model_id: The unique identifier for the model to be retrieved,
                      e.g., "openai_gpt4", "local_mistral".
            model_type: The type of model interface to return. Defaults to "chat".
                        Can be "chat" for AbstractChatModel or "text" for
                        AbstractLanguageModel.

        Returns:
            An instance of a class that implements either AbstractChatModel or
            AbstractLanguageModel.
        """
        ...

    @abc.abstractmethod
    def list_models(self) -> List[str]:
        """
        Lists the unique identifiers of all available models.

        This method is useful for discovery, allowing other parts of the system
        to know which models are registered and available for use.

        Returns:
            A list of strings, where each string is a `model_id`.
        """
        ...