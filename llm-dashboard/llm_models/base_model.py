from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class BaseModel:
    id: Optional[str] = field(default=None)
    created_at: Optional[datetime] = field(default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self) -> dict:
        raise NotImplementedError(
            "Every model must implement to_dict()"
        )

    def _base_dict(self) -> dict:
        return {
            "created_at": self.created_at.isoformat()
        }