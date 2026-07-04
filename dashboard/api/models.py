import uuid
from sqlalchemy import Column, String, BigInteger, Numeric, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_repo = Column(String, nullable=False, unique=True)
    owner_github_id = Column(BigInteger, nullable=False)
    api_token_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    fuzz_runs = relationship("FuzzRun", back_populates="project", cascade="all, delete-orphan")


class FuzzRun(Base):
    __tablename__ = "fuzz_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    commit_sha = Column(String, nullable=False)
    started_at = Column(TIMESTAMP(timezone=True), nullable=False)
    finished_at = Column(TIMESTAMP(timezone=True), nullable=False)
    iterations = Column(BigInteger, nullable=False)
    coverage_pct = Column(Numeric(5, 2))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    project = relationship("Project", back_populates="fuzz_runs")
    crashes = relationship("Crash", back_populates="fuzz_run", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_fuzz_runs_project_id", "project_id"),
        Index("idx_fuzz_runs_commit_sha", "commit_sha"),
    )


class Crash(Base):
    __tablename__ = "crashes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fuzz_run_id = Column(UUID(as_uuid=True), ForeignKey("fuzz_runs.id", ondelete="CASCADE"), nullable=False)
    target_fn = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    dedup_hash = Column(String, nullable=False)
    status = Column(String, nullable=False, default="open")
    reproducer_path = Column(String)
    first_seen_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    fuzz_run = relationship("FuzzRun", back_populates="crashes")

    __table_args__ = (
        CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name="crashes_severity_check"),
        CheckConstraint("status IN ('open', 'acknowledged', 'fixed', 'wontfix')", name="crashes_status_check"),
        Index("idx_crashes_dedup", "fuzz_run_id", "dedup_hash", unique=True),
    )


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    soroban_type = Column(String, nullable=False)
    crate_version = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "crate_version", name="strategies_name_crate_version_key"),
    )
