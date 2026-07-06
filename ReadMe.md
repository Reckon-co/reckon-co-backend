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

## Contributing

We welcome contributions from the open-source community! Whether you want to fix a bug, add a feature, or improve documentation, your help is appreciated.

### How to Contribute

1. **Fork the Repository:** Start by forking this repository to your GitHub account using the "Fork" button.
2. **Clone Locally:** Clone your forked repository to your local machine.
   ```bash
   git clone https://github.com/your-username/reckon-co-backend.git
   ```
3. **Create a Branch:** Create a new branch for your feature or bug fix. Please use descriptive branch names.
   ```bash
   git checkout -b feature/my-awesome-feature
   # or
   git checkout -b fix/issue-123
   ```
4. **Make Your Changes:** Implement your feature or bug fix. Ensure your code follows the existing style conventions.
5. **Test Your Code:** Verify that your changes do not break existing functionality. Run the local development server and ensure everything works smoothly.
6. **Commit Your Changes:** Write clear, concise commit messages.
   ```bash
   git commit -m "Add feature X"
   ```
7. **Push to Your Fork:**
   ```bash
   git push origin feature/my-awesome-feature
   ```
8. **Submit a Pull Request:** Open a pull request against the `master` branch of the original repository. Describe your changes in detail and link any related issues.

### Reporting Bugs

If you find a bug, please open an issue in the issue tracker. Include the following information:
- A clear and descriptive title.
- Steps to reproduce the bug.
- Expected vs. actual behavior.
- Relevant logs, screenshots, or code snippets.
- Your environment (e.g., OS, Python version).

### Suggesting Enhancements

Got an idea for a new feature? We'd love to hear it! Open an issue to discuss your proposal before starting development to ensure it aligns with the project's goals.

### Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please treat all maintainers and contributors with respect, maintain a welcoming environment for everyone, and engage constructively in discussions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
