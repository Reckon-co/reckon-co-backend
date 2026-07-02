from pydantic import BaseModel, Field
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

class FuzzRunDetail(BaseModel):
    id: UUID
    project_id: UUID
    commit_sha: str
    started_at: datetime
    finished_at: datetime
    iterations: int
    coverage_pct: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FuzzRunsPaginated(BaseModel):
    items: List[FuzzRunDetail]
    next_cursor: Optional[int] = None

class CoverageTrendItem(BaseModel):
    commit_sha: str
    date: datetime
    coverage_pct: Optional[float] = None

class CrashDetail(BaseModel):
    id: UUID
    fuzz_run_id: UUID
    target_fn: str
    severity: str
    dedup_hash: str
    status: str
    reproducer_path: Optional[str] = None
    first_seen_at: datetime

    class Config:
        from_attributes = True
