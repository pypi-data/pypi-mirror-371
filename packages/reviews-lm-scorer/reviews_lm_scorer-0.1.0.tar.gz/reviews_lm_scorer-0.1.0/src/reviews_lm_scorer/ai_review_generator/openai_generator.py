from openai import OpenAI, AuthenticationError
from typing import Dict
from reviews_lm_scorer.utils import ConfigManager  
from reviews_lm_scorer.ai_review_generator import BaseAIReviewsGenerator
import inspect



class OpenAIReviewGenerator(BaseAIReviewsGenerator):
    
    def __init__(self,api_key: str):
        if not isinstance(api_key, str):
            raise TypeError(f"API key must be string format. Input was of {type(api_key)}")

        self._config = ConfigManager.get_instance()
        self._config.set_openai_key(api_key)
        self._api_key = self._config.openai_api_key

        self._client = OpenAI(api_key=self._api_key)
        self._validate_api_key()

        self._valid_setting_params = set(inspect.signature(self._client.responses.create).parameters.keys())
        '''
        Valid params as of 21/08/25:
        {'max_output_tokens', 'parallel_tool_calls', 'truncation', 'stream_options', 'tool_choice', 
        'tools', 'model', 'top_logprobs', 'extra_headers', 'max_tool_calls', 'include', 'extra_query', 
        'metadata', 'prompt_cache_key', 'extra_body', 'reasoning', 'top_p', 'safety_identifier', 'stream', 
        'input', 'text', 'previous_response_id', 'instructions', 'user', 'timeout', 'prompt', 'background',
        'store', 'temperature', 'service_tier'}
        '''
        self._settings = {
            'model': "gpt-4o-mini",
            'temperature': 0.7
        }

    def _validate_api_key(self) -> None:
        try:
            self._client.models.list()
        except AuthenticationError:
            raise ValueError("Authentication Failed: Invalid OpenAI key")
        except Exception as e:
            raise RuntimeError(f"Authentication Error: {str(e)}")
        
    def config_settings(self, **kwargs) -> None:
        for param, val in kwargs.items():
            if param in self._valid_setting_params:
                self._settings[param] = val
            else:
                raise ValueError(f"Invalid parameter: {param}. Valid parameters are: {self._valid_setting_params}")
            

    def generate_review(self, prompt: str, **kwargs) -> str:
        stitched_prompt = self._stitch_prompt(prompt, ** kwargs)

        try:
            response = self._client.responses.create(input=stitched_prompt, **self.settings)
            
        except Exception as e:
            raise RuntimeError(f"Review generation failed: {str(e)}")
        
        return response.output_text


    @property
    def settings(self) -> Dict:
        return self._settings.copy()

        

      