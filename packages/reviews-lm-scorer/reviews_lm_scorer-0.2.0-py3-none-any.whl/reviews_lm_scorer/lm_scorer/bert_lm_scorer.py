from typing import Optional, Dict, Any, List, Union
import pandas as pd
import numpy as np
from transformers import BertForSequenceClassification
from reviews_lm_scorer.lm_scorer import BaseLMScorer
from reviews_lm_scorer.hf_manager import HuggingFaceManager 
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score



class BERTLMScorer(BaseLMScorer):
    def __init__(self, hugging_face_manager: Optional[HuggingFaceManager] = None, model_params: Optional[Dict[str, Any]] = None):

        if hugging_face_manager is not None and not isinstance(hugging_face_manager, HuggingFaceManager):
            raise TypeError(f"hugging_face_manager must be a HuggingFaceManager instance.")

        self._framework = None
        self._valid_frameworks = ["torch"]

        super().__init__(api_connector=hugging_face_manager,model_params=model_params)
        if self._api_connector is not None:
            self.hf_connection = True
        else:
            self.hf_connection = False

    def _hf_connection_check(self) -> None:
        if self.hf_connection == False:
            raise ConnectionError(f"BERTLMScorer is not linked to Hugging Face Hub. Please link with the following method: '.hf_link(YOUR_HuggingFaceManager_OBJECT)'")
        
    def hf_link(self, hugging_face_manager: HuggingFaceManager) -> None:
        if not isinstance(hugging_face_manager, HuggingFaceManager):
            raise TypeError(f"hugging_face_manager must be a HuggingFaceManager instance.")
        self._api_connector = hugging_face_manager
        self.hf_connection = True

    def hf_download(self,repo_id: str, framework: str = "torch", **kwargs) -> None:
        self._hf_connection_check()

        if not isinstance(framework, str):
            raise ValueError(f"Framework must be a string.")
        elif framework not in self._valid_frameworks:
            raise ValueError(f"{framework} is not a valid framework. Only the following frameworks are valid: {self._valid_frameworks}")
        else:
            self._framework = framework

        tags = self._api_connector._api.model_info(repo_id).tags
        if "lm_scorer" not in tags:
            raise RuntimeError(f"{repo_id} is not an LM scorer model")
        model, tokenizer = self._api_connector.download_model(repo_id=repo_id, model_type=BertForSequenceClassification, framework=framework, **kwargs)

        if not isinstance(model, BertForSequenceClassification):
            raise TypeError("Downloaded model is not a BertForSequenceClassification")
        if model.config.num_labels != 2:
            raise ValueError("Downloaded model does not perform binary classification")
        
        self.model = model
        self.tokenizer = tokenizer

    def predict(self, inputs: Union[str, List[str], pd.Series, pd.DataFrame], **kwargs) -> List[int]:

        if isinstance(inputs,str):
            inputs = [inputs]
        elif isinstance(inputs,list):
            inputs = inputs
        elif isinstance(inputs,pd.Series):
            inputs = inputs.tolist()
        elif isinstance(inputs, pd.DataFrame):
            if len(inputs.columns) > 1:
                raise ValueError("The DataFrame provided has more than one column. Please ensure that Pandas DataFrames provided to this function only has one column.")
            inputs = inputs.iloc[:, 0].tolist()
        else:
            raise ValueError(f"Invalid input type: {type(inputs)}")
        
        if self._framework == "torch":
            try:
                encodings = self.tokenizer(inputs, padding=True, truncation=True, return_tensors="pt", **kwargs)
            except Exception as e:
                raise RuntimeError(f"Enconding Failure: {str(e)}")
            
            self.model.eval()
            import torch
            with torch.no_grad():
                outputs = self.model(**encodings)
                preds = torch.argmax(outputs.logits, dim=-1).tolist()
            return preds
        
    def evaluate(self, eval_data: Union[List[str], pd.Series, pd.DataFrame], labels: Union[List[int], np.ndarray], **kwargs) -> Dict[str, float]:
        if not (isinstance(labels,list) or isinstance(labels,np.ndarray)):
            raise ValueError("Labels must be a list or numpy array")
        
        if isinstance(labels, np.ndarray):
            labels = labels.tolist()
        
        if not set(labels).issubset({0, 1}):
            raise ValueError("Labels can only contain {0 ,1}")
        
        if len(eval_data) != len(labels):
            raise ValueError("eval_data and labels must have the same length")
        
        preds = self.predict(eval_data, **kwargs)
        
        metrics = {
            "accuracy": accuracy_score(labels, preds),
            "precision": precision_score(labels, preds, zero_division=0),
            "recall": recall_score(labels, preds, zero_division=0),
            "f1": f1_score(labels, preds, zero_division=0)
            }
        
        return metrics
    
    def lm_score(self, inputs: Union[str, List[str], pd.Series, pd.DataFrame], **kwargs) -> List[int]:

        if isinstance(inputs,str):
            inputs = [inputs]
        elif isinstance(inputs,list):
            inputs = inputs
        elif isinstance(inputs,pd.Series):
            inputs = inputs.tolist()
        elif isinstance(inputs, pd.DataFrame):
            if len(inputs.columns) > 1:
                raise ValueError("The DataFrame provided has more than one column. Please ensure that Pandas DataFrames provided to this function only has one column.")
            inputs = inputs.iloc[:, 0].tolist()
        else:
            raise ValueError(f"Invalid input type: {type(inputs)}")
        
        if self._framework == "torch":
            try:
                encodings = self.tokenizer(inputs, padding=True, truncation=True, return_tensors="pt", **kwargs)
            except Exception as e:
                raise RuntimeError(f"Enconding Failure: {str(e)}")
            
            self.model.eval()
            import torch
            import torch.nn.functional as F
            with torch.no_grad():
                outputs = self.model(**encodings)
                probs = F.softmax(outputs.logits, dim=-1)[:, 1].tolist()
            return probs

            





