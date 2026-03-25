from dataclasses import dataclass
from typing import Optional
from datetime import date
from llm_models.base_model import BaseModel

@dataclass
class DailyUsageModel(BaseModel):
    project_id: Optional[str] = None
    api_key_id: Optional[str] = None
    provider: str = ""
    model: str = ""
    usage_date: Optional[date] = None
    total_calls: int = 0
    total_sessions: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    avg_latency_ms: int = 0
    avg_cost_per_session: float = 0.0
    critic_rate: float = 0.0
    hallucinations_caught: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.usage_date is None:
            self.usage_date = date.today()

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "project_id": self.project_id,
            "api_key_id": self.api_key_id,
            "provider": self.provider,
            "model": self.model,
            "usage_date": self.usage_date.isoformat(),
            "total_calls": self.total_calls,
            "total_sessions": self.total_sessions,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "avg_latency_ms": self.avg_latency_ms,
            "avg_cost_per_session": self.avg_cost_per_session,
            "critic_rate": self.critic_rate,
            "hallucinations_caught": self.hallucinations_caught
        }