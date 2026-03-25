from dataclasses import dataclass
from typing import Optional
from llm_models.base_model import BaseModel

@dataclass
class ApiKeyModel(BaseModel):
    project_id: str = ""
    provider: str = ""
    alias: str = ""
    tier: str = "paid"

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "project_id": self.project_id,
            "provider": self.provider,
            "alias": self.alias,
            "tier": self.tier
        }