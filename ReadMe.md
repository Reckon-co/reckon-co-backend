# Reckon Dashboard API

Reckon Dashboard API is a backend service for a continuous fuzzing dashboard. It collects fuzzing run results, tracks crashes, and monitors code coverage trends across your projects. It provides a RESTful API for CI/CD pipelines to report fuzzing outcomes and for frontend clients to visualize the data.

## Features

- **Fuzz Run Tracking:** Record iterations, start/finish times, and coverage percentage for fuzz runs.
- **Crash Management:** Collect, deduplicate, and track crashes found during fuzzing.
- **Coverage Trends:** Track coverage progression over different commits.
- **Project Badges:** Automatically generate SVG badges indicating project fuzzing status.
- **Authentication:** Secure endpoint access with API tokens per project repository.

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** PostgreSQL with [SQLAlchemy](https://www.sqlalchemy.org/) ORM and [Alembic](https://alembic.sqlalchemy.org/) for migrations
- **Data Validation:** Pydantic
- **Containerization:** Docker & Docker Compose

## Getting Started

### Prerequisites

- Python 3.8+
- Docker & Docker Compose

### Local Development Setup

1. **Start the Database**
   The project uses PostgreSQL. Start it using Docker Compose:
   ```bash
   cd dashboard/api
   docker-compose up -d
   ```

2. **Create a Virtual Environment & Install Dependencies**
   ```bash
   cd dashboard/api
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run Database Migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start the API Server**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://127.0.0.1:8000`. You can access the interactive Swagger API documentation at `http://127.0.0.1:8000/docs`.

## Key API Endpoints

- `POST /api/v1/runs` - Create a new fuzz run and report crashes (Requires Bearer token authentication).
- `GET /api/v1/projects/{owner}/{repo}/runs` - Get a list of fuzz runs for a repository.
- `GET /api/v1/projects/{owner}/{repo}/crashes` - Get all crashes for a repository.
- `GET /api/v1/projects/{owner}/{repo}/coverage-trend` - Get the coverage trend.
- `GET /api/v1/projects/{owner}/{repo}/badge` - Get an SVG badge for the repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
