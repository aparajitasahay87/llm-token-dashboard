from dataclasses import dataclass
from typing import Optional
from llm_models.base_model import BaseModel

@dataclass
class ProjectModel(BaseModel):
    name: str = ""
    description: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "name": self.name,
            "description": self.description
        }