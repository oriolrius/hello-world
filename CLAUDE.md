# Claude Code Instructions

## Project Overview

**hello-world** is an educational DevOps demonstration project showcasing production-grade deployment practices. The application is a minimal HTTP server returning "hello-world" — the focus is on infrastructure, CI/CD, and deployment patterns rather than application logic.

**Current Version**: v4.x (ECR + ECS Fargate)

## Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.13 |
| Package Manager | [uv](https://docs.astral.sh/uv/) |
| Build Backend | Hatchling |
| Linter/Formatter | Ruff |
| Testing | pytest |
| Containerization | Docker (multi-stage) |
| Container Registry | Amazon ECR |
| Orchestration | AWS ECS Fargate |
| Infrastructure | AWS CloudFormation |
| CI/CD | GitHub Actions |
| Versioning | Commitizen (Conventional Commits) |

## Directory Structure

```
hello-world/
├── src/hello_world/           # Application source
│   └── __init__.py            # HTTP server (main entry point)
├── tests/                     # Test suite
│   └── test_server.py
├── docker/                    # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── infra/                     # AWS CloudFormation IaC
│   ├── cloudformation.yml
│   └── docs/                  # Architecture diagrams
├── .github/workflows/         # CI/CD pipelines
│   └── release.yml
├── pyproject.toml             # Project config (deps, tools, scripts)
├── Makefile                   # Build & deployment automation
├── uv.lock                    # Locked dependencies
└── .githooks/                 # Git hooks (commitizen validation)
```

## Development Setup

```bash
# Install dependencies (creates venv automatically)
uv sync

# Run the application
uv run hello-world --bind 0.0.0.0 --port 8080

# Or install globally
uv pip install -e .
hello-world -b 0.0.0.0 -p 8080
```

## Development Commands

```bash
# Linting and formatting
uv run ruff check src/ tests/       # Check for issues
uv run ruff check --fix src/ tests/ # Auto-fix issues
uv run ruff format src/ tests/      # Format code
uv run ruff format --check src/ tests/  # Check formatting

# Testing
uv run pytest -v                    # Run all tests

# Building
uv build                            # Build wheel and sdist to dist/
```

## Code Style

Ruff is configured in `pyproject.toml`:

```toml
[tool.ruff]
src = ["src"]
line-length = 100
select = ["E", "F", "I", "W"]  # Errors, Pyflakes, Imports, Warnings
```

Run `uv run ruff check --fix` and `uv run ruff format` before committing.

## Testing

Tests are in `tests/` using pytest. The test suite spins up a temporary HTTP server and validates responses.

```bash
uv run pytest -v           # Verbose output
uv run pytest -x           # Stop on first failure
uv run pytest --tb=short   # Shorter tracebacks
```

## Docker

```bash
# Build locally
docker build -f docker/Dockerfile -t hello-world .

# Run locally
docker run -p 8080:49000 hello-world

# Using docker-compose
docker compose -f docker/docker-compose.yml up
```

The Dockerfile uses multi-stage builds with `python:3.13-slim` and installs via `uv`.

## AWS Infrastructure

Infrastructure is defined in `infra/cloudformation.yml`. Key resources:

| Resource | Purpose |
|----------|---------|
| ECR Repository | Container image storage |
| ECS Cluster | Fargate container orchestration |
| ECS Task Definition | 0.25 vCPU, 512MB memory |
| ECS Service | Runs 1 task with public IP |
| VPC + Subnet | Networking (10.0.0.0/16) |
| Security Group | Allows inbound port 49000 |
| CloudWatch Logs | 7-day retention |

## Makefile Targets

```bash
make help       # Show all targets
make deploy     # Deploy CloudFormation stack
make delete     # Delete stack
make ecr-login  # Authenticate to ECR
make ecr-push   # Build and push Docker image
make redeploy   # Force new ECS deployment
make status     # Show service status and public IP
make logs       # Tail CloudWatch logs
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/release.yml`) runs on:
- Push tags matching `v*-ecr-ecs-fargate`
- Manual `workflow_dispatch`

**Pipeline stages:**
1. **lint** — Ruff check and format validation
2. **test** — pytest execution
3. **build** — Build wheel/sdist, upload artifacts
4. **release** — Create GitHub release
5. **docker** — Build and push to ECR

**Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN` (optional, for SSO)

## Commit Message Format

This project uses **Conventional Commits** via [commitizen](https://commitizen-tools.github.io/commitizen/).

### Format

```
type(scope)?: description

[optional body]

[optional footer(s)]
```

### Types and Version Bumps

| Type | Description | Version Bump |
|------|-------------|--------------|
| `feat` | A new feature | MINOR |
| `fix` | A bug fix | PATCH |
| `docs` | Documentation only | - |
| `style` | Code style (formatting) | - |
| `refactor` | Neither fix nor feature | - |
| `perf` | Performance improvement | PATCH |
| `test` | Adding/correcting tests | - |
| `build` | Build system changes | - |
| `ci` | CI configuration | - |
| `chore` | Maintenance tasks | - |
| `revert` | Reverts a commit | - |

### Breaking Changes

Add `!` after type/scope or `BREAKING CHANGE:` in footer → MAJOR bump:

```
feat!: remove deprecated API
feat(api)!: change auth method

feat: new feature

BREAKING CHANGE: description of breaking change
```

### Examples

```
feat: add user login
fix(auth): resolve token bug
docs: update API docs
feat!: redesign API (breaking)
```

### Commitizen Commands

```bash
cz commit        # Interactive commit (optional)
cz check         # Validate last commit message
cz bump          # Bump version based on commits
cz bump --dry-run  # Preview version bump
```

### Co-Authored-By

Include when creating commits:

```
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Git Hooks

The project uses custom git hooks in `.githooks/`:
- **commit-msg**: Validates commit messages against Conventional Commits via `cz check`

To enable hooks after cloning:

```bash
git config core.hooksPath .githooks
```

## Tag Format

Tags follow the pattern: `v{version}-ecr-ecs-fargate`

Example: `v4.3.3-ecr-ecs-fargate`

This suffix identifies the deployment target/branch family.

## Troubleshooting

### Common Issues

**Linting fails:**
```bash
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/
```

**Commit rejected by hook:**
Ensure your commit message follows Conventional Commits format. Use `cz commit` for interactive help.

**Docker build fails:**
Check that you're building from the repo root with `-f docker/Dockerfile`.

**ECS deployment not updating:**
```bash
make redeploy  # Forces new deployment with latest image
```

**Can't connect to deployed service:**
```bash
make status    # Check if task is running and get public IP
make logs      # Check application logs
```

## Key Files

| File | Purpose |
|------|---------|
| `src/hello_world/__init__.py` | Main application (HTTP server) |
| `pyproject.toml` | Project config, dependencies, tool settings |
| `docker/Dockerfile` | Container build instructions |
| `infra/cloudformation.yml` | AWS infrastructure definition |
| `.github/workflows/release.yml` | CI/CD pipeline |
| `Makefile` | Build and deployment automation |
