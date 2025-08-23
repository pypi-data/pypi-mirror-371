"""
schemas/run_schema.py
Keeps client / server / SDK in sync with the new user_id column on runs.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from projectdavid_common.schemas.actions_schema import ActionRead
from projectdavid_common.schemas.tools_schema import Tool, ToolRead


# --------------------------------------------------------------------------- #
#  Status enum (unchanged)
# --------------------------------------------------------------------------- #
class RunStatus(str, Enum):
    queued = "queued"
    in_progress = "in_progress"
    pending_action = "action_required"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
    pending = "pending"
    processing = "processing"
    expired = "expired"
    retrying = "retrying"


# --------------------------------------------------------------------------- #
#  Base‑level model returned by most endpoints
# --------------------------------------------------------------------------- #
class Run(BaseModel):
    id: str
    user_id: Optional[str] = Field(
        default=None,
        description="Filled in by the server from the caller’s API‑key. "
        "Clients MAY omit or set to None.",
    )

    assistant_id: str
    cancelled_at: Optional[int]
    completed_at: Optional[int]
    created_at: int
    expires_at: int
    failed_at: Optional[int]
    incomplete_details: Optional[str]
    instructions: str
    last_error: Optional[str]
    max_completion_tokens: Optional[int]
    max_prompt_tokens: Optional[int]
    meta_data: Dict[str, Any]
    model: str
    object: str
    parallel_tool_calls: bool
    required_action: Optional[str]
    response_format: str
    started_at: Optional[int]
    status: RunStatus | str
    thread_id: str
    tool_choice: str
    tools: List[Tool]
    truncation_strategy: Dict[str, Any]
    usage: Optional[Any]
    temperature: float
    top_p: float
    tool_resources: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------- #
#  Payload used by SDK / tests when creating runs
#  user_id is optional ‑ server overwrites it from auth context
# --------------------------------------------------------------------------- #
class RunCreate(BaseModel):
    id: str
    assistant_id: str
    # ── NEW optional user_id (ignored by server if provided) ───────────── #
    user_id: Optional[str] = Field(
        default=None,
        json_schema_extra={"readOnly": True},  # treated as server‑generated
    )
    # ───────────────────────────────────────────────────────────────────── #
    cancelled_at: Optional[int] = None
    completed_at: Optional[int] = None
    created_at: int
    expires_at: int
    failed_at: Optional[int] = None
    incomplete_details: Optional[Dict[str, Any]] = None
    instructions: str
    last_error: Optional[str] = None
    max_completion_tokens: Optional[int] = 1000
    max_prompt_tokens: Optional[int] = 500
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    model: str = "gpt-4"
    object: str = "run"
    parallel_tool_calls: bool = False
    required_action: Optional[str] = None
    response_format: str = "text"
    started_at: Optional[int] = None
    status: RunStatus | str = RunStatus.pending
    thread_id: str
    tool_choice: str = "none"
    tools: List[Tool] = Field(default_factory=list)
    truncation_strategy: Dict[str, Any] = Field(default_factory=dict)
    usage: Optional[Any] = None
    temperature: float = 0.7
    top_p: float = 0.9
    tool_resources: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------- #
#  Rich read model with actions attached
# --------------------------------------------------------------------------- #
class RunReadDetailed(BaseModel):
    id: str
    user_id: str
    assistant_id: str
    cancelled_at: Optional[int] = None
    completed_at: Optional[int] = None
    created_at: int
    expires_at: Optional[int] = None
    failed_at: Optional[int] = None
    incomplete_details: Optional[str] = None
    instructions: str
    last_error: Optional[str] = None
    max_completion_tokens: Optional[int] = 1000
    max_prompt_tokens: Optional[int] = 500
    meta_data: Dict[str, Any]
    model: str
    object: str
    parallel_tool_calls: bool
    required_action: Optional[str] = None
    response_format: str
    started_at: Optional[int] = None
    status: RunStatus | str
    thread_id: str
    tool_choice: str
    tools: List[ToolRead]
    truncation_strategy: Dict[str, Any]
    usage: Optional[Any] = None
    temperature: float
    top_p: float
    tool_resources: Dict[str, Any]
    actions: List[ActionRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------- #
#  Small helper for the status‑only update endpoint
# --------------------------------------------------------------------------- #
class RunStatusUpdate(BaseModel):
    status: RunStatus


# --------------------------------------------------------------------------- #
#  Small helper for the status‑only update endpoint
# --------------------------------------------------------------------------- #
class RunListResponse(BaseModel):
    object: Literal["list"] = "list"
    data: List[Run]
    first_id: Optional[str] = None
    last_id: Optional[str] = None
    has_more: bool = False
