import json
from pathlib import Path
from typing import Dict, Optional
import importlib.resources as pkg_resources


class PromptTemplateManager():

    def __init__(self, template_storage_path: Optional[str] = None):
        if template_storage_path is None:
            with pkg_resources.path(__package__, "prompt_templates.json") as p:
                self.json_path = p
        else:
            self.json_path = Path(template_storage_path)

        self._json_path_validity(self.json_path)
        
        self.templates = self._load_templates(self.json_path)

    @staticmethod
    def _json_path_validity(json_path: Path) -> None:

        if not json_path.exists():
            raise FileNotFoundError(f"Template file does not exist: {json_path}")
        
        if json_path.suffix.lower() != ".json":
            raise ValueError(f"Template file must be a JSON file: {json_path}")
        
    @staticmethod
    def _load_templates(json_path: Path) -> Dict[str, str]:
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Template JSON must be a dictionary: {json_path}")
        
        for name, prompt in data.items():
            if not name.strip():
                raise ValueError(f"Names for prompt templates must be non-empty strings. Found Name: {name}")
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError(f"Prompt templates must be non-empty strings. Found Name and Prompt pair with '{name}': {prompt}")
            
        return data
    
    def get_template(self, name: str) -> str:
        if name not in self.templates:
            raise KeyError(f"Template '{name}' does not exist.")
        return self.templates[name]
    
    def _update_templates_json(self, modified_templates: Dict[str, str]) -> None:
  
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(modified_templates, f, indent=4, ensure_ascii=False)

    def add_template(self, name: str, prompt: str) -> None:
        if not isinstance(name, str) or not isinstance(prompt, str):
            raise ValueError("Both template name and prompt must be non_empty strings.")
        if name.strip() == "" or prompt.strip() == "":
            raise ValueError("Both template name and prompt must be non-empty strings.")
        if name in self.templates:
            raise ValueError("Name already in use. Pick another.")
        self.templates[name] = prompt
        self._update_templates_json(self.templates)

    
    def delete_template(self, name: str) -> None:
        if name not in self.templates:
            raise KeyError(f"Template '{name}' does not exist.")
        del self.templates[name]
        self._update_templates_json(self.templates)

    def update_template(self, name: str, new_prompt: str) -> None:
        if name not in self.templates:
            raise KeyError(f"Template '{name}' does not exist.")
        if not isinstance(new_prompt, str) or not new_prompt.strip():
            raise ValueError("Prompt must be a non-empty string.")
        
        self.templates[name] = new_prompt
        self._update_templates_json(self.templates)

    def list_templates(self) -> list[str]:
        return list(self.templates.keys())




