from typing import Optional

"""
Singleton class for managing configuration settings across the framework.
Handles API keys and environment settings.
"""

class ConfigManager:

    _instance = None 
    _allow_init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._allow_init:
            raise RuntimeError("This is a Singleton Class, please invoke the get_instance() method instead")
    
        # Store Api Keys
        self._huggingface_token: Optional[str] = None
        self._openai_api_key: Optional[str] = None
        
        # HuggingFace Settings
        self._huggingface_username: Optional[str] = None
        self._huggingface_linked: bool = False
        

    # Get or create singleton instance of ConfigManager
    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        if cls._instance == None:
            cls._allow_init = True 
            cls._instance = cls()
            cls._allow_init = False
        return cls._instance
    
    # API Key Management
    def set_huggingface_credentials(self, token: str, username: Optional[str] = None) -> None:
        self._huggingface_token = token
        self._huggingface_username = username
    
    def set_openai_key(self, key: str) -> None:
        self._openai_api_key = key
    
    
    #hugging face link flag
    def set_huggingface_link_flag(self,flag: bool) -> None:
        self._huggingface_linked = flag

    # Getters
    @property
    def huggingface_token(self) -> Optional[str]:
        return self._huggingface_token

    @property
    def openai_api_key(self) -> Optional[str]:
        return self._openai_api_key

    @property
    def huggingface_username(self) -> Optional[str]:
        return self._huggingface_username

    @property
    def huggingface_linked(self) -> bool:
        return self._huggingface_linked




