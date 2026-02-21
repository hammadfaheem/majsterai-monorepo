"""Agent domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Agent:
    """Agent domain entity - pure business logic."""

    id: int
    org_id: str
    name: str
    prompt: str
    extra_prompt: str | None
    is_custom_prompt: bool
    llm_model: str
    stt_model: str
    tts_model: dict[str, Any] | None
    settings: dict[str, Any] | None
    status: str
    created_at: int
    updated_at: int
    deleted_at: int | None
    variables: dict[str, Any] | None = None

    def __post_init__(self):
        """Validate agent entity."""
        if not self.org_id:
            raise ValueError("Agent must belong to an organization")
        if not self.name or len(self.name.strip()) < 1:
            raise ValueError("Agent name cannot be empty")
        if self.settings is None:
            self.settings = {}
        if self.tts_model is None:
            self.tts_model = {}

    def is_deleted(self) -> bool:
        """Check if agent is soft deleted."""
        return self.deleted_at is not None

    def is_ready(self) -> bool:
        """Check if agent is ready to use."""
        return self.status == "ready" and not self.is_deleted()

    def get_full_prompt(self) -> str:
        """Get full prompt including extra_prompt if available."""
        if self.extra_prompt:
            return f"{self.prompt}\n\n{self.extra_prompt}"
        return self.prompt
