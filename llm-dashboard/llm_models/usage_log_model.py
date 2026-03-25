from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from llm_models.base_model import BaseModel

@dataclass
class UsageLogModel(BaseModel):
    project_id: Optional[str] = None
    api_key_id: Optional[str] = None
    session_id: Optional[str] = None
    provider: str = ""
    model: str = ""
    tier: str = "paid"
    call_type: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    status: str = "success"
    critic_triggered: bool = False
    strength_tier: Optional[str] = None
    corrections_made: int = 0
    hallucinations_caught: int = 0
    candidates_found: int = 0
    examples_used: int = 0
    temperature: Optional[float] = None
    max_tokens_set: Optional[int] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        super().__post_init__()
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "project_id": self.project_id,
            "api_key_id": self.api_key_id,
            "session_id": self.session_id,
            "provider": self.provider,
            "model": self.model,
            "tier": self.tier,
            "call_type": self.call_type,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "status": self.status,
            "critic_triggered": self.critic_triggered,
            "strength_tier": self.strength_tier,
            "corrections_made": self.corrections_made,
            "hallucinations_caught": self.hallucinations_caught,
            "candidates_found": self.candidates_found,
            "examples_used": self.examples_used,
            "temperature": self.temperature,
            "max_tokens_set": self.max_tokens_set,
            "timestamp": self.timestamp.isoformat()
        }