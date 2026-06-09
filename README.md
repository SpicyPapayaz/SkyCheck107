# SkyCheck 107 — UAV Mission Planning & Pre-Flight Analysis Tool

SkyCheck 107 is a Dockerized Python web app for pre-flight UAV mission checks.

**Drone Mission Pre-Flight Tool: Always Check to Prevent the Wreck!**

It evaluates UAV mission inputs against configurable FAA Part 107 advisory rules and generates a risk score, structured findings, operator checklist, and go/no-go guidance.

> Advisory only. This tool does not provide FAA authorization, legal advice, aviation weather briefing, or a substitute for Remote PIC judgment.

## Resume Alignment

**Tools:** Python, Docker, Git, Jira-style planning docs, JSON  


## Features

- Interactive mission form for altitude, visibility, cloud clearance, airspace, lighting, location risk, Remote ID, and operational flags. The form starts blank and the risk score stays `0` until the user submits a complete mission.
- JSON-driven rule pack in `rules/part107_rules.json`.
- Flask API endpoint at `/api/evaluate`.
- Operator-facing decision: `GO`, `CONDITIONAL GO`, or `NO-GO`.
- Risk scoring and mitigation checklist.
- Docker and Docker Compose support.
- Jira-style delivery artifact in `docs/jira_delivery_plan.md`.

## Project Structure

```txt
uav-mission-planner/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── rules/
│   └── part107_rules.json
├── data/
│   └── risk_profiles.json
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── styles.css
├── tests/
│   └── test_engine.py
└── docs/
    ├── jira_delivery_plan.md
    └── sample_missions.json
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

```txt
http://localhost:8000
```

## Run with Docker

```bash
docker build -t skycheck107 .
docker run -p 8000:8000 skycheck107
```

or:

```bash
docker compose up --build
```

## Production Notes

- The app exposes `/health` for deployment checks.
- The rule engine reads `rules/part107_rules.json`, keeping aviation constraints separate from application logic.
- The app is advisory only and does not replace FAA authorization, official weather briefing, or Remote PIC judgment.
