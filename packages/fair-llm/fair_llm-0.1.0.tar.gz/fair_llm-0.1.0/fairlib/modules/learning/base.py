from abc import ABC, abstractmethod
from typing import Any, List


class AbstractModelManager(ABC):
    """
    Interface for managing fine-tuned model configurations or custom models.
    """

    @abstractmethod
    def get_model(self, model_id: str) -> Any:
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        pass

# MODULE GOAL: Enable the agentic system to adapt, improve performance, and
#   incorporate new knowledge or behaviors over time. eg. integrating fine-tuned
#   models and potentially supporting agent-level learning mechanisms through feedback/experience

# TODO::DESIGN::
#   interface for model management: clear interface, interacting with MAL
#       load/manage/select fine tuned models or model adapters
#   Feedback collection system: standardized way to capture:
#       explicit usr feedback, implicit signals, or evaluation outputs
#   Pluggable learning strategies: interfaces for incorporating different RL algos, or
#       other self-improvement techniques

# TODO::COMPONENTS::
#   feedback collection and storage interface
#   Model Adapter/loader [via MAL]
#   Data Logging: for retraining/Fine-tuning
#       collect interation data in a format suitable for exporting to model training pipelines
#   Online learning/preference alignment based on ongoing interactions
