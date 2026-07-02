from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import hashlib

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reckon Dashboard API", version="1.0.0")

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_project_by_token(api_key_header: str = Security(api_key_header), db: Session = Depends(get_db)):
    if not api_key_header:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = api_key_header.replace("Bearer ", "") if api_key_header.startswith("Bearer ") else api_key_header
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    project = db.query(models.Project).filter(models.Project.api_token_hash == token_hash).first()
    if not project:
        raise HTTPException(status_code=401, detail="Invalid token")
    return project

@app.post("/api/v1/runs", response_model=schemas.FuzzRunResponse, status_code=status.HTTP_201_CREATED)
def create_run(run: schemas.FuzzRunCreate, project: models.Project = Depends(get_project_by_token), db: Session = Depends(get_db)):
    if project.github_repo != run.project_repo:
        raise HTTPException(status_code=401, detail="Token does not match project repo")
    
    db_run = models.FuzzRun(
        project_id=project.id,
        commit_sha=run.commit_sha,
        started_at=run.started_at,
        finished_at=run.finished_at,
        iterations=run.iterations,
        coverage_pct=run.coverage_pct
    )
    db.add(db_run)
    db.flush() # To get db_run.id
    
    for crash in run.crashes:
        db_crash = models.Crash(
            fuzz_run_id=db_run.id,
            target_fn=crash.target_fn,
            severity=crash.severity,
            dedup_hash=crash.dedup_hash,
            reproducer_path=crash.reproducer_path
        )
        db.add(db_crash)
        
    db.commit()
    db.refresh(db_run)
    return {"run_id": db_run.id}

@app.get("/api/v1/projects/{repo:path}/runs", response_model=schemas.FuzzRunsPaginated)
def get_runs(repo: str, limit: int = 20, cursor: Optional[int] = None, db: Session = Depends(get_db)):
    limit = min(limit, 100)
    project = db.query(models.Project).filter(models.Project.github_repo == repo).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    query = db.query(models.FuzzRun).filter(models.FuzzRun.project_id == project.id).order_by(desc(models.FuzzRun.created_at))
    if cursor is not None:
        query = query.offset(cursor)
        
    runs = query.limit(limit).all()
    next_cursor = cursor + limit if cursor is not None else limit
    
    if len(runs) < limit:
        next_cursor = None
        
    return {"items": runs, "next_cursor": next_cursor}

@app.get("/api/v1/projects/{repo:path}/coverage-trend", response_model=List[schemas.CoverageTrendItem])
def get_coverage_trend(repo: str, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.github_repo == repo).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    runs = db.query(models.FuzzRun).filter(
        models.FuzzRun.project_id == project.id,
        models.FuzzRun.coverage_pct.isnot(None)
    ).order_by(models.FuzzRun.created_at).all()
    
    return [
        {"commit_sha": run.commit_sha, "date": run.created_at, "coverage_pct": run.coverage_pct}
        for run in runs
    ]

@app.get("/api/v1/projects/{repo:path}/badge")
def get_badge(repo: str, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.github_repo == repo).first()
    if not project:
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="20"><text x="10" y="15">Not Found</text></svg>'
        return Response(content=svg, media_type="image/svg+xml")
        
    latest_run = db.query(models.FuzzRun).filter(models.FuzzRun.project_id == project.id).order_by(desc(models.FuzzRun.created_at)).first()
    
    if not latest_run:
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="20"><text x="10" y="15">No Runs</text></svg>'
        return Response(content=svg, media_type="image/svg+xml")
        
    has_crashes = db.query(models.Crash).filter(models.Crash.fuzz_run_id == latest_run.id).first() is not None
    status_text = "failing" if has_crashes else "passing"
    color = "red" if has_crashes else "green"
    cov_text = f" | {latest_run.coverage_pct}%" if latest_run.coverage_pct else ""
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="20">
    <rect width="160" height="20" fill="{color}"/>
    <text x="10" y="14" fill="white" font-family="sans-serif" font-size="11">Reckon {status_text}{cov_text}</text>
    </svg>'''
    
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/v1/projects/{repo:path}/crashes", response_model=List[schemas.CrashDetail])
def get_crashes(repo: str, status: Optional[str] = "open", db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.github_repo == repo).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    query = db.query(models.Crash).join(models.FuzzRun).filter(models.FuzzRun.project_id == project.id)
    
    if status:
        query = query.filter(models.Crash.status == status)
        
    crashes = query.order_by(desc(models.Crash.first_seen_at)).all()
    return crashes
