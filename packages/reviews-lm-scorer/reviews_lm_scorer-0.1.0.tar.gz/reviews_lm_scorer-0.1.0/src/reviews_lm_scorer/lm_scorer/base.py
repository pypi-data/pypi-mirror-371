# reviews_lm_scorer/lm_scorers/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from reviews_lm_scorer.utils import ConfigManager


class BaseLMScorer(ABC):

    def __init__(self, api_connector: Optional[Any] = None, model_params: Optional[Dict[str, Any]] = None):

        self._model_params = model_params or {}
        self._api_connector = api_connector
        self._config = ConfigManager.get_instance()


    @abstractmethod
    def evaluate(self, eval_data, labels) -> Dict[str, float]:
        pass

    @abstractmethod
    def predict(self, inputs) -> Any:
        pass

    
    @property
    def model_params(self) -> Dict[str, Any]:
        return self._model_params

