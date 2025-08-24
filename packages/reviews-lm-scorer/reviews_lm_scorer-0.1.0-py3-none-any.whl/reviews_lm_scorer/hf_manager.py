from huggingface_hub import login, HfApi
from huggingface_hub.utils import RepositoryNotFoundError
from reviews_lm_scorer.utils import ConfigManager  
from typing import Optional, Union, List
from datasets import Dataset, load_dataset
import pandas as pd
from reviews_lm_scorer.utils import framework_check
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class HuggingFaceManager:
    def __init__(self, token: str, username: Optional[str] = None):
        
        self._config = ConfigManager.get_instance()
        self._config.set_huggingface_credentials(token=token, username=username)
        self._token = self._config.huggingface_token
        self._api = HfApi()
        
        if self._token:
            self._login()
            if username is None:
                username_found = self._api.whoami()['name']
                self._config.set_huggingface_credentials(token=token, username=username_found)

        self._username = self._config.huggingface_username

    def link_check(self):
        if not self._config.huggingface_linked:
            raise RuntimeError("Not logged in to HuggingFace. Please initialise again with a valid token")

    def _login(self) -> None:
        try:
            login(token=self._token)
            self._config.set_huggingface_link_flag(True)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to HuggingFace: {str(e)}")
        
    def store_dataset(self, dataset: Union[pd.DataFrame, Dataset], repo_id: str, **kwargs) -> None:
        self.link_check()

        if isinstance(dataset, pd.DataFrame):
            data = Dataset.from_pandas(dataset)
        elif isinstance(dataset, Dataset):
            data = dataset
        else:
            raise RuntimeError("Dataset is in an invalid format. Please convert to either a Pandas Dataframe or a Hugging Face Dataset.")
        
        try:
            data.push_to_hub(repo_id, **kwargs)
            print(f"Dataset successfully uploaded onto hugging face at {repo_id}")
        except Exception as e:
            print(f"Dataset failed to upload to {repo_id}: {e}")

    
    def list_models(self, account_username: Optional[str] = None) -> List:
        self.link_check()
        if account_username is None:
            account_username = self._username

        try:
            models = self._api.list_models(author=account_username)
        except Exception as e:
            raise RuntimeError(f"Failed to access models owned by {account_username}: {e}")
        
        model_list = [model.id for model in models] if models else []

        return model_list
    
    def list_datasets(self, account_username: Optional[str] = None) -> List:
        self.link_check()
        if account_username is None:
            account_username = self._username

        try:
            datasets = self._api.list_datasets(author=account_username)
        except Exception as e:
            raise RuntimeError(f"Failed to access datasets owned by {account_username}: {e}")
        
        datasets_list = [dataset.id for dataset in datasets] if datasets else []

        return datasets_list
    
    @staticmethod
    def _repo_type(api: HfApi, repo_id: str) -> Optional[str]:

        valid_repo_types = ["model", "dataset","space","library"]
        
        for valid_repo_type in valid_repo_types:
            try:
                api.repo_info(repo_id, repo_type=valid_repo_type)
                return valid_repo_type
            except RepositoryNotFoundError:
                pass

        return None

        
    def download_dataset(self, repo_id: str, **kwargs) -> Dataset:
        self.link_check()

        repo_type = self._repo_type(self._api,repo_id)
        if repo_type is None:
            raise RuntimeError(f"{repo_id} does not exists")
        elif repo_type != "dataset":
            raise RuntimeError(f"{repo_id} is not of a dataset repo type")
        
        try:
            loaded_dataset = load_dataset(repo_id,**kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to load dataset from {repo_id}: {e}")

        return loaded_dataset


    def store_model(self, model, repo_id: str, tokenizer=None, framework:str = "torch", **kwargs) -> None:
        self.link_check()
        framework_check(framework)
        try:
            self._api.create_repo(repo_id, exist_ok=True)
            model.push_to_hub(repo_id, **kwargs)
            if tokenizer:
                tokenizer.push_to_hub(repo_id, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to upload model to {repo_id}: {e}")
        
    def store_lm_scorer(self, model, repo_id: str, tokenizer=None, framework:str = "torch", **kwargs) -> None:
        self.store_model(model=model, repo_id=repo_id, tokenizer=tokenizer, framework=framework,tags=["lm_scorer"], **kwargs)
        
    def download_model(self, repo_id: str, model_type=None, framework:str = "torch", **kwargs) -> None:
        self.link_check()
        framework_check(framework)

        if model_type is None:
            model_type = AutoModelForSequenceClassification

        repo_type = self._repo_type(self._api,repo_id)
        if repo_type is None:
            raise RuntimeError(f"{repo_id} does not exists")
        elif repo_type != "model":
            raise RuntimeError(f"{repo_id} is not of a model repo type")
        
        try:
            if framework == "torch":
                model = model_type.from_pretrained(repo_id, **kwargs)
                tokenizer = AutoTokenizer.from_pretrained(repo_id, **kwargs)
                return model, tokenizer
            else:
                raise ValueError(f"{framework} is an unsupported framework")
        except Exception as e:
            raise RuntimeError(f"Model download from {repo_id} failed: {str(e)}")
                               

    @property
    def is_logged_in(self) -> bool:
        return self._config.huggingface_linked



