# SkyCheck 107 — UAV Mission Planning & Pre-Flight Analysis Tool

SkyCheck 107 is a portfolio-grade, Dockerized Python web app for pre-flight UAV mission checks.

**Drone Mission Pre-Flight Tool: Always Check to Prevent the Wreck!**

It evaluates UAV mission inputs against configurable FAA Part 107 advisory rules and generates a risk score, structured findings, operator checklist, and go/no-go guidance.

> Advisory only. This tool does not provide FAA authorization, legal advice, aviation weather briefing, or a substitute for Remote PIC judgment.

## Resume Alignment

**Tools:** Python, Docker, Git, Jira-style planning docs, JSON  
**Demonstrates:** rule-engine design, API endpoints, responsive UI, config-driven software logic, automated tests, Microsoft Azure container deployment readiness.

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

## Test

```bash
pytest
```

Final UI smoke-test values:

Safe mission:
```txt
Mission name: Safe daylight mapping
Remote PIC: Portfolio Demo Pilot
Location: Pittsburgh, PA
Latitude: 40.4406
Longitude: -79.9959
Airport distance NM: 6
Altitude AGL ft: 250
Visibility SM: 8
Wind mph: 10
Cloud horizontal ft: 3000
Cloud vertical ft: 900
Airspace: G
Light condition: Day
Remote ID ready: checked
Expected: GO
```

Blocked mission:
```txt
Altitude AGL ft: 450
Visibility SM: 2.5
Cloud horizontal ft: 1000
Cloud vertical ft: 300
Airspace: D
LAANC/ATC authorization: unchecked
Light condition: Night
Anti-collision lights: unchecked
Emergency activity nearby: checked
Expected: NO-GO
```


## GitHub Upload

```bash
git init
git add .
git commit -m "Initial SkyCheck 107 UAV mission planner"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/uav-mission-planner.git
git push -u origin main
```

## Deploy to Microsoft Azure

Recommended path: **Azure Container Apps**. It is a managed container platform that can build from your Dockerfile and expose a public HTTPS URL.

Full instructions are in:

```txt
docs/azure_deployment_guide.md
```

Quick deploy after installing Azure CLI and Docker:

```bash
az login
az extension add --name containerapp --upgrade
az group create --name rg-skycheck107 --location eastus
az containerapp up \
  --name skycheck107 \
  --resource-group rg-skycheck107 \
  --location eastus \
  --source . \
  --ingress external \
  --target-port 8000
```

Get the public URL:

```bash
az containerapp show \
  --name skycheck107 \
  --resource-group rg-skycheck107 \
  --query properties.configuration.ingress.fqdn \
  -o tsv
```

## Production Notes

- The app exposes `/health` for deployment checks.
- The rule engine reads `rules/part107_rules.json`, keeping aviation constraints separate from application logic.
- The app is advisory only and does not replace FAA authorization, official weather briefing, or Remote PIC judgment.
