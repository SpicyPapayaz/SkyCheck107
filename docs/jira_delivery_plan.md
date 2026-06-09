# Jira-Style Delivery Plan

## Epic: UAV Mission Planning & Pre-Flight Analysis Tool

### SKY-101 — Project scaffold
Create Flask app, Dockerfile, Git repository layout, health endpoint, and README.

### SKY-102 — JSON Part 107 rule engine
Move mission thresholds into `rules/part107_rules.json` and implement repeatable evaluator logic.

### SKY-103 — Interactive operator UI
Build responsive front end with mission form, risk score, findings, checklist, and JSON output.

### SKY-104 — Test and validation
Add pytest coverage for GO and NO-GO mission scenarios.

### SKY-105 — Azure deployment
Containerize with Docker and document Azure Container Apps resource group, container build, ingress, health checks, public HTTPS URL, and validation steps.

## Definition of Done

- App runs locally with Docker.
- `/health` endpoint returns OK.
- Rule changes can be made through JSON without editing front-end code.
- README includes GitHub and Azure deployment instructions.
- Demo mission produces operator-facing go/no-go guidance.
