from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class CrashCreate(BaseModel):
    target_fn: str
    severity: str
    dedup_hash: str
    reproducer_path: Optional[str] = None

class FuzzRunCreate(BaseModel):
    project_repo: str
    commit_sha: str
    started_at: datetime
    finished_at: datetime
    iterations: int
    coverage_pct: Optional[float] = None
    crashes: List[CrashCreate] = []

class FuzzRunResponse(BaseModel):
    run_id: UUID

class FuzzRunRecord(BaseModel):
    id: UUID
    project_id: UUID
    commit_sha: str
    started_at: datetime
    finished_at: datetime
    iterations: int
    coverage_pct: Optional[float]
    model_config = ConfigDict(from_attributes=True)

class CoverageTrend(BaseModel):
    commit_sha: str
    date: datetime
    coverage_pct: Optional[float]

class CrashRecord(BaseModel):
    id: UUID
    target_fn: str
    severity: str
    dedup_hash: str
    status: str
    reproducer_path: Optional[str]
    first_seen_at: datetime
    model_config = ConfigDict(from_attributes=True)
