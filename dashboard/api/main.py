from fastapi import FastAPI, Depends, HTTPException, status, Query, Header, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import models
import schemas
from database import engine, get_db, Base
import hashlib
from datetime import datetime, timezone

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reckon Dashboard API")

def verify_token(db: Session, repo: str, token: str) -> models.Project:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    project = db.query(models.Project).filter(models.Project.github_repo == repo).first()
    if not project or project.api_token_hash != token_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token"
        )
    return project

@app.post("/api/v1/runs", status_code=status.HTTP_201_CREATED, response_model=schemas.FuzzRunResponse)
def create_run(run: schemas.FuzzRunCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ")[1]
    
    project = verify_token(db, run.project_repo, token)
    
    db_run = models.FuzzRun(
        project_id=project.id,
        commit_sha=run.commit_sha,
        started_at=run.started_at,
        finished_at=run.finished_at,
        iterations=run.iterations,
        coverage_pct=run.coverage_pct,
    )
    db.add(db_run)
    db.flush()
    
    for crash in run.crashes:
        existing_crash = db.query(models.Crash).filter(
            models.Crash.dedup_hash == crash.dedup_hash,
            models.Crash.fuzz_run_id == db_run.id
        ).first()
        
        if not existing_crash:
            db_crash = models.Crash(
                fuzz_run_id=db_run.id,
                target_fn=crash.target_fn,
                severity=crash.severity,
                dedup_hash=crash.dedup_hash,
                reproducer_path=crash.reproducer_path,
                first_seen_at=datetime.now(timezone.utc)
            )
            db.add(db_crash)
            
    db.commit()
    db.refresh(db_run)
    return schemas.FuzzRunResponse(run_id=db_run.id)

@app.get("/api/v1/projects/{owner}/{repo}/runs", response_model=List[schemas.FuzzRunRecord])
def get_runs(owner: str, repo: str, limit: int = Query(20, le=100), cursor: Optional[str] = None, db: Session = Depends(get_db)):
    full_repo = f"{owner}/{repo}"
    project = db.query(models.Project).filter(models.Project.github_repo == full_repo).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    query = db.query(models.FuzzRun).filter(models.FuzzRun.project_id == project.id).order_by(desc(models.FuzzRun.created_at))
    runs = query.limit(limit).all()
    return runs

@app.get("/api/v1/projects/{owner}/{repo}/coverage-trend", response_model=List[schemas.CoverageTrend])
def get_coverage_trend(owner: str, repo: str, db: Session = Depends(get_db)):
    full_repo = f"{owner}/{repo}"
    project = db.query(models.Project).filter(models.Project.github_repo == full_repo).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    runs = db.query(models.FuzzRun).filter(
        models.FuzzRun.project_id == project.id,
        models.FuzzRun.coverage_pct.isnot(None)
    ).order_by(models.FuzzRun.created_at).all()
    
    return [schemas.CoverageTrend(commit_sha=r.commit_sha, date=r.created_at, coverage_pct=r.coverage_pct) for r in runs]

@app.get("/api/v1/projects/{owner}/{repo}/badge")
def get_badge(owner: str, repo: str, db: Session = Depends(get_db)):
    full_repo = f"{owner}/{repo}"
    project = db.query(models.Project).filter(models.Project.github_repo == full_repo).first()
    
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="a">
    <rect width="120" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#a)">
    <path fill="#555" d="M0 0h50v20H0z"/>
    <path fill="#4c1" d="M50 0h70v20H50z"/>
    <path fill="url(#b)" d="M0 0h120v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="25" y="15" fill="#010101" fill-opacity=".3">fuzz</text>
    <text x="25" y="14">fuzz</text>
    <text x="84" y="15" fill="#010101" fill-opacity=".3">passing</text>
    <text x="84" y="14">passing</text>
  </g>
</svg>'''
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/v1/projects/{owner}/{repo}/crashes", response_model=List[schemas.CrashRecord])
def get_crashes(owner: str, repo: str, status: Optional[str] = None, db: Session = Depends(get_db)):
    full_repo = f"{owner}/{repo}"
    project = db.query(models.Project).filter(models.Project.github_repo == full_repo).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    query = db.query(models.Crash).join(models.FuzzRun).filter(models.FuzzRun.project_id == project.id)
    if status:
        query = query.filter(models.Crash.status == status)
        
    crashes = query.all()
    return crashes
