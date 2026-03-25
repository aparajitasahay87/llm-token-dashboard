from dataclasses import dataclass
from typing import Optional
from llm_models.base_model import BaseModel

@dataclass
class InsightModel(BaseModel):
    project_id: Optional[str] = None
    insight_text: str = ""
    insight_type: str = ""

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "project_id": self.project_id,
            "insight_text": self.insight_text,
            "insight_type": self.insight_type
        }