# TicketFlow OSS

TicketFlow OSS is a lightweight open-source IT request and approval workflow API built with FastAPI and SQLite.
It is designed for learning, demos, and small-team internal tooling. The project models common ITSM patterns such as:

- request intake for laptops, software, and VPN access
- manager approval and conditional security approval
- assignment-group task creation after approval
- audit-friendly event timelines
- status tracking and simple reporting endpoints

## Why this project is worth building publicly

This repo fits practical help desk / ServiceNow-style workflows while staying fully open-source and easy to run locally.
It can grow into a real community project by adding:

- pluggable approval rules
- PostgreSQL support
- email or Slack notifications
- dashboards and analytics
- Terraform or Docker deployment examples
- issue templates and beginner-friendly contributions

## Tech stack

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- pytest

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open docs at `http://127.0.0.1:8000/docs`.

## Sample workflow

1. Create a request for `laptop`, `software`, or `vpn`.
2. Manager approves the request.
3. VPN requests require an additional security approval.
4. After final approval, fulfillment tasks are generated for the proper assignment group.
5. When all tasks are completed, the request closes automatically.

## Roadmap

### v0.1
- [x] request intake API
- [x] manager approval
- [x] conditional security approval for VPN
- [x] auto-generated fulfillment tasks
- [x] event timeline
- [x] basic tests

### v0.2
- [ ] Docker support
- [ ] PostgreSQL support
- [ ] role-based auth
- [ ] email notification adapter
- [ ] metrics endpoint

### v0.3
- [ ] frontend dashboard
- [ ] webhook integrations
- [ ] plugin system for approval policies

## Contribution ideas

- add new request types
- improve validation rules
- add more tests
- create Docker Compose setup
- add seed/demo data
- improve docs and examples

## License

MIT
