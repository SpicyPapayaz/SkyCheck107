from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
RULES_PATH = BASE_DIR / "rules" / "part107_rules.json"
PROFILE_PATH = BASE_DIR / "data" / "risk_profiles.json"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@dataclass(frozen=True)
class Finding:
    rule_id: str
    status: str
    severity: str
    title: str
    message: str
    regulation: str
    recommendation: str

    def as_dict(self) -> Dict[str, str]:
        return self.__dict__.copy()


class MissionRuleEngine:
    """JSON-driven FAA Part 107-style pre-flight evaluator.

    The engine intentionally keeps rules in JSON to demonstrate maintainable,
    repeatable checks. It is advisory software, not an FAA authorization system.
    """

    def __init__(self, rules_path: Path = RULES_PATH, profile_path: Path = PROFILE_PATH) -> None:
        self.rules = load_json(rules_path)
        self.profiles = load_json(profile_path)

    def evaluate(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self._normalize(mission)
        findings: List[Finding] = []

        findings.extend(self._check_numeric_rules(normalized))
        findings.extend(self._check_airspace(normalized))
        findings.extend(self._check_night(normalized))
        findings.extend(self._check_operation_flags(normalized))
        findings.extend(self._check_location_risk(normalized))

        score = self._risk_score(normalized, findings)
        decision = self._decision(score, findings)
        checklist = self._checklist(normalized, decision)

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mission": normalized,
            "decision": decision,
            "risk_score": score,
            "findings": [finding.as_dict() for finding in findings],
            "checklist": checklist,
            "config_version": self.rules["meta"]["version"],
            "disclaimer": self.rules["meta"]["disclaimer"],
        }

    def _normalize(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        def number(name: str, default: float = 0.0) -> float:
            value = mission.get(name, default)
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        def boolean(name: str) -> bool:
            value = mission.get(name, False)
            if isinstance(value, bool):
                return value
            return str(value).lower() in {"1", "true", "yes", "on"}

        return {
            "mission_name": str(mission.get("mission_name") or "Untitled Mission").strip(),
            "pilot_name": str(mission.get("pilot_name") or "Remote PIC").strip(),
            "location": str(mission.get("location") or "Unknown").strip(),
            "latitude": number("latitude"),
            "longitude": number("longitude"),
            "altitude_agl_ft": number("altitude_agl_ft"),
            "visibility_sm": number("visibility_sm"),
            "wind_speed_mph": number("wind_speed_mph"),
            "cloud_clearance_horizontal_ft": number("cloud_clearance_horizontal_ft"),
            "cloud_clearance_vertical_ft": number("cloud_clearance_vertical_ft"),
            "airspace_class": str(mission.get("airspace_class") or "G").upper(),
            "laanc_authorization": boolean("laanc_authorization"),
            "daylight_condition": str(mission.get("daylight_condition") or "day").lower(),
            "anti_collision_lights": boolean("anti_collision_lights"),
            "visual_observer": boolean("visual_observer"),
            "operations_over_people": boolean("operations_over_people"),
            "operations_over_moving_vehicles": boolean("operations_over_moving_vehicles"),
            "near_airport_nm": number("near_airport_nm", 10),
            "near_emergency": boolean("near_emergency"),
            "remote_id_ready": boolean("remote_id_ready"),
            "notes": str(mission.get("notes") or "").strip(),
        }

    def _finding(self, rule: Dict[str, Any], status: str, message: str, recommendation: str | None = None) -> Finding:
        return Finding(
            rule_id=rule["id"],
            status=status,
            severity=rule.get("severity", "info"),
            title=rule["title"],
            message=message,
            regulation=rule.get("regulation", "Operational best practice"),
            recommendation=recommendation or rule.get("recommendation", "Review before flight."),
        )

    def _check_numeric_rules(self, mission: Dict[str, Any]) -> List[Finding]:
        results: List[Finding] = []
        for rule in self.rules["numeric_rules"]:
            value = mission[rule["field"]]
            operator = rule["operator"]
            threshold = rule["threshold"]
            passed = value <= threshold if operator == "<=" else value >= threshold
            status = "pass" if passed else "fail"
            template = rule["pass_message"] if passed else rule["fail_message"]
            results.append(self._finding(rule, status, template.format(value=value, threshold=threshold)))
        return results

    def _check_airspace(self, mission: Dict[str, Any]) -> List[Finding]:
        rule = self.rules["special_rules"]["controlled_airspace"]
        controlled = mission["airspace_class"] in rule["controlled_classes"]
        if controlled and not mission["laanc_authorization"]:
            return [self._finding(rule, "fail", f"Class {mission['airspace_class']} airspace selected without LAANC/ATC authorization.")]
        if controlled:
            return [self._finding(rule, "caution", f"Class {mission['airspace_class']} requires valid authorization and altitude grid compliance.")]
        return [self._finding(rule, "pass", "Class G selected; controlled-airspace authorization was not indicated as required by this tool.")]

    def _check_night(self, mission: Dict[str, Any]) -> List[Finding]:
        rule = self.rules["special_rules"]["night_operations"]
        condition = mission["daylight_condition"]
        if condition in {"night", "civil_twilight"} and not mission["anti_collision_lights"]:
            return [self._finding(rule, "fail", f"{condition.replace('_', ' ').title()} selected without anti-collision lighting.")]
        if condition in {"night", "civil_twilight"}:
            return [self._finding(rule, "caution", "Night/twilight operation selected; verify pilot training, lighting, visibility, and local authorization conditions.")]
        return [self._finding(rule, "pass", "Daylight operation selected.")]

    def _check_operation_flags(self, mission: Dict[str, Any]) -> List[Finding]:
        findings: List[Finding] = []
        for key, rule in self.rules["operation_flags"].items():
            active = mission[key]
            status = "caution" if active else "pass"
            message = rule["active_message"] if active else rule["inactive_message"]
            findings.append(self._finding(rule, status, message))
        return findings

    def _check_location_risk(self, mission: Dict[str, Any]) -> List[Finding]:
        rule = self.rules["special_rules"]["location_risk"]
        messages = []
        status = "pass"

        if mission["near_airport_nm"] < 5:
            status = "caution"
            messages.append("Mission is within 5 NM of an airport; verify airspace, traffic pattern, and local restrictions.")
        if mission["near_emergency"]:
            status = "fail"
            messages.append("Emergency/public safety activity flagged; do not interfere with emergency response.")
        if not mission["remote_id_ready"]:
            status = "caution" if status != "fail" else status
            messages.append("Remote ID readiness not confirmed.")

        if not messages:
            messages.append("No additional location-risk flags were selected.")
        return [self._finding(rule, status, " ".join(messages))]

    def _risk_score(self, mission: Dict[str, Any], findings: List[Finding]) -> int:
        weights = self.profiles["weights"]
        score = self.profiles["base_score"]
        for finding in findings:
            score += weights.get(finding.status, 0)
            if finding.status in {"caution", "fail"}:
                score += weights.get(finding.severity, 0)

        score += min(15, math.ceil(mission["wind_speed_mph"] / 4))
        score += 8 if mission["visibility_sm"] < 5 else 0
        score += 10 if mission["visual_observer"] is False and mission["daylight_condition"] != "day" else 0
        return max(0, min(score, 100))

    def _decision(self, score: int, findings: List[Finding]) -> Dict[str, str]:
        has_fail = any(f.status == "fail" for f in findings)
        caution_count = sum(1 for f in findings if f.status == "caution")
        if has_fail or score >= 70:
            return {
                "status": "NO-GO",
                "tone": "critical",
                "summary": "Mission should not launch until blocking issues are corrected.",
            }
        if caution_count or score >= 40:
            return {
                "status": "CONDITIONAL GO",
                "tone": "warning",
                "summary": "Mission may proceed only after the listed mitigations are verified by the Remote PIC.",
            }
        return {
            "status": "GO",
            "tone": "success",
            "summary": "Mission inputs are within the configured advisory thresholds.",
        }

    def _checklist(self, mission: Dict[str, Any], decision: Dict[str, str]) -> List[Dict[str, str]]:
        items = [
            ("Airspace", "Verify FAA UAS Facility Map/LAANC status and local restrictions before launch."),
            ("Weather", "Confirm latest METAR/TAF or local weather source: visibility, winds, gusts, precipitation."),
            ("Aircraft", "Inspect propellers, battery health, firmware, Remote ID, compass/GNSS, and return-to-home altitude."),
            ("Crew", "Brief Remote PIC, visual observer, lost-link, emergency, and sterile cockpit procedures."),
            ("Site", "Establish launch zone, bystander buffer, landing alternate, and emergency landing area."),
        ]
        if decision["status"] != "GO":
            items.insert(0, ("Mitigation", "Resolve all fail/caution items or document the mitigation before flying."))
        if mission["daylight_condition"] != "day":
            items.append(("Night Ops", "Confirm night training, anti-collision lighting, crew adaptation, and obstacle scan."))
        return [{"category": category, "task": task} for category, task in items]


engine = MissionRuleEngine()
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/evaluate")
def evaluate():
    payload = request.get_json(force=True, silent=True) or {}
    return jsonify(engine.evaluate(payload))


@app.get("/api/rules")
def rules():
    return jsonify(load_json(RULES_PATH))


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "uav-mission-planner"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
