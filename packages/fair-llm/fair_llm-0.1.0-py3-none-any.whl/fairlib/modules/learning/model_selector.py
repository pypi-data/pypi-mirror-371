from fairlib.modules.learning.base import AbstractModelManager
from typing import Optional


class ModelSelector:
    """
    Utility class to select a model from a model manager based on input criteria.
    """

    def __init__(self, model_manager: AbstractModelManager):
        self.model_manager = model_manager

    def select_model(self, task_type: str = "general", user_id: Optional[str] = None) -> str:
        """
        Select a model ID based on task type, user, or other context.

        For now, this uses simple heuristics. This can later be expanded
        to support ML-based selection, embeddings, usage logs, etc.
        """
        available_models = self.model_manager.list_models()

        # just return a matching one by prefix
        for model_id in available_models:
            if task_type in model_id:
                return model_id

        return available_models[0] if available_models else None
