from dataclasses import dataclass
from typing import Optional
from llm_models.base_model import BaseModel

@dataclass
class BudgetModel(BaseModel):
    project_id: Optional[str] = None
    api_key_id: Optional[str] = None
    provider: str = ""
    monthly_limit: float = 0.0
    alert_at_pct: int = 80

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "project_id": self.project_id,
            "api_key_id": self.api_key_id,
            "provider": self.provider,
            "monthly_limit": self.monthly_limit,
            "alert_at_pct": self.alert_at_pct
        }