# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Superset Showtime is a Python CLI tool for managing Apache Superset ephemeral environments using **circus tent emoji labels** as a state management system on GitHub PRs. The system replaces complex GitHub Actions scripts with a simple CLI that uses GitHub labels for ACID-like state transactions.

## Development Commands

### Essential Commands
```bash
# Development setup
uv pip install -e ".[dev]"     # Install with dev dependencies
make pre-commit                 # Setup pre-commit hooks
make test                       # Run tests
make lint                       # Run ruff + mypy

# Testing circus tent functionality
python -m showtime --help               # Shows complete workflow tutorial
python -m showtime labels               # Complete label reference
python -m showtime list                 # List all environments (requires GITHUB_TOKEN)
python -m showtime test-lifecycle 1234  # Full workflow simulation

# Test with real GitHub PRs safely
export GITHUB_TOKEN=xxx
showtime start 34809 --dry-run-aws --aws-sleep 5    # Mock AWS, real GitHub labels
showtime status 34809                                # Check environment status
showtime stop 34809 --force                         # Clean up test labels
```

### Testing Single Components
```bash
pytest tests/unit/test_circus.py                    # Test label parsing
pytest tests/unit/test_circus.py::test_show_properties -v   # Single test
python -c "from showtime.core.circus import Show; show = Show(pr_number=1234, sha='abc123f', status='running'); print(show.to_circus_labels())"   # Quick circus label test
```

## Architecture Overview

### Core State Management Pattern
The system uses **GitHub labels as a distributed state machine**:
- **Trigger labels** (`🎪 trigger-start`) - Commands added by users, processed and removed by CLI
- **State labels** (`🎪 🚦 abc123f running`) - Per-SHA status managed by CLI
- **No external database** - All state reconstructed from GitHub labels

### Key Classes and Responsibilities

#### `Show` (showtime/core/circus.py:16)
Represents a single ephemeral environment with per-SHA state:
- **Properties**: `aws_service_name`, `aws_image_tag` for deterministic AWS naming
- **Methods**: `to_circus_labels()` creates per-SHA format labels
- **Parsing**: `from_circus_labels()` reconstructs from GitHub labels

#### `PullRequest` (showtime/core/circus.py:121)
Container parsing all shows from a PR's labels:
- **Properties**: `current_show`, `building_show`, `circus_labels`
- **State reconstruction**: Parses all environments from labels
- **Factory method**: `from_id()` loads real GitHub data

#### `GitHubInterface` (showtime/core/github.py:23)
GitHub API operations with emoji label support:
- **Authentication**: Auto-detects `GITHUB_TOKEN` or `gh auth token`
- **Label operations**: Handles emoji encoding for GitHub API
- **Discovery**: `find_prs_with_shows()` searches for circus tent labels

#### `AWSInterface` (showtime/core/aws.py:35)
Replicates current GitHub Actions AWS logic:
- **Naming**: Uses same deterministic patterns as current GHA
- **Operations**: `create_environment()`, `delete_environment()` mirror existing workflows
- **Network config**: Same subnets/security groups as production

### Label Format Design

#### Per-SHA State Labels
```bash
🎪 🚦 {sha} {status}        # 🎪 🚦 abc123f running
🎪 🌐 {sha} {ip-dashes}     # 🎪 🌐 abc123f 52-1-2-3
🎪 📅 {sha} {timestamp}     # 🎪 📅 abc123f 2024-01-15T14-30
🎪 ⌛ {sha} {ttl}           # 🎪 ⌛ abc123f 24h
🎪 🤡 {sha} {username}      # 🎪 🤡 abc123f maxime
🎪 ⚙️ {sha} {config}        # 🎪 ⚙️ abc123f alerts,debug
```

#### Pointer Labels (No Value)
```bash
🎪 🎯 {sha}                 # Active environment pointer
🎪 🏗️ {sha}                 # Building environment pointer
```

### GitHub Actions Integration

#### Current Integration Points
- **`.github/workflows/circus.yml`** - Main workflow replacing `ephemeral-env.yml`
- **`.github/workflows/circus-cleanup.yml`** - Scheduled cleanup replacing manual processes
- **Security model**: `pull_request_target` + PyPI install (no PR code execution)

#### CLI Commands Called by GHA
- `showtime handle-trigger {pr-number}` - Process trigger labels
- `showtime handle-sync {pr-number}` - Handle new commits
- `showtime cleanup --older-than 48h` - Scheduled cleanup

## Important Implementation Details

### Authentication Pattern
```python
# Priority order for credentials:
github = GitHubInterface()  # Auto-detects GITHUB_TOKEN or gh CLI
# No config files - environment variables only
```

### Dry-Run Testing Strategy
The CLI has comprehensive dry-run support for safe testing:
```bash
--dry-run-aws        # Skip AWS operations, use mock data
--dry-run-github     # Skip GitHub operations, show what would happen
--aws-sleep N        # Sleep N seconds to simulate AWS timing
```

### AWS Resource Naming
Must maintain compatibility with existing Superset infrastructure:
- **ECS Service**: `pr-{pr_number}-{sha}` (e.g., `pr-1234-abc123f`)
- **ECR Image**: `pr-{pr_number}-{sha}-ci`
- **Network**: Same subnets/security groups as current production setup

### State Recovery Pattern
Since the CLI is stateless, it always reconstructs state from GitHub labels:
```python
pr = PullRequest.from_id(pr_number, github)  # Reads all labels
show = pr.current_show                       # Finds active environment
# All state comes from parsing circus tent emoji labels
```

## Critical Development Notes

### Label Operations Must Be Atomic
GitHub label operations are the "database transactions" - handle carefully:
```python
# Remove trigger immediately after processing
github.remove_label(pr_number, trigger_label)
# Update state labels atomically
github.remove_circus_labels(pr_number)
for label in new_labels:
    github.add_label(pr_number, label)
```

### Per-SHA Format Required
All new state labels must include SHA for multi-environment support:
```python
# Correct: Per-SHA format
f"🎪 🚦 {sha} running"      # Status per environment
f"🎪 🌐 {sha} {ip}"         # IP per environment

# Incorrect: Global format (legacy)
"🎪 🚦 running"             # Which environment??
```

### Testing Against Real PRs
The CLI can safely test against real Superset PRs:
```bash
# Test label management without AWS costs
showtime start 34809 --dry-run-aws
# Removes test labels when done
showtime stop 34809 --force
```

## Current Implementation Status

### ✅ Working (Tested)
- GitHub API integration with apache/superset
- Circus tent emoji label parsing and creation
- CLI commands: `list`, `status`, `start/stop` (with dry-run)
- Beautiful help system that teaches label workflow
- Comprehensive dry-run testing framework

### 🚧 Partially Implemented
- AWS operations (class exists, logic written, needs testing)
- Per-SHA label parsing (designed, needs full implementation)
- Trigger processing (framework exists, needs completion)

### 📋 Not Implemented
- Rolling update logic for zero-downtime
- Real AWS integration testing
- Feature flag configuration via labels
- GitHub Actions workflow deployment
