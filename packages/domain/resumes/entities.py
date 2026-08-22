from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Resume:
    """Domain representation of a candidate resume."""

    id: UUID
    candidate_id: UUID
    filename: str
    content_type: str
    storage_key: str
    parsed_text: str | None = None
    is_canonical: bool = False
    created_at: datetime | None = None
