# Contributing to TicketFlow OSS

Thanks for your interest in contributing.

## Good first issues

- add seed data command
- add Dockerfile
- add pagination to list endpoints
- add request cancellation flow
- add webhook notification adapter
- improve docs examples

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

## Contribution guidelines

- open an issue before large changes
- keep PRs focused and small
- include tests for new behavior
- update docs when endpoints or workflow rules change
