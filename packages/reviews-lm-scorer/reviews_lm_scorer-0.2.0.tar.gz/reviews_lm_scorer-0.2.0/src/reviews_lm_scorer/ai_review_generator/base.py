from abc import ABC, abstractmethod
from typing import Optional

class BaseAIReviewsGenerator(ABC):
    
    @abstractmethod
    def __init__(self,api_key: Optional[str] = None):
        pass

    @abstractmethod
    def generate_review(self,prompt: str, **kwargs) -> str:
        pass

    def _stitch_prompt(self,prompt: str, **kwargs) -> str:
        if not isinstance(prompt, str):
            raise TypeError(f"Prompt must be string. Input was of {type(prompt)}")
        
        try:
            return prompt.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing the required variables: {e}")
        except Exception as e:
            raise RuntimeError(f"Error combining prompt with variables: {e}")
        