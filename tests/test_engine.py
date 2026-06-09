from app import MissionRuleEngine


def test_go_mission():
    result = MissionRuleEngine().evaluate({
        "altitude_agl_ft": 200,
        "visibility_sm": 6,
        "cloud_clearance_horizontal_ft": 2500,
        "cloud_clearance_vertical_ft": 800,
        "airspace_class": "G",
        "daylight_condition": "day",
        "remote_id_ready": True
    })
    assert result["decision"]["status"] == "GO"


def test_no_go_for_altitude_and_visibility():
    result = MissionRuleEngine().evaluate({
        "altitude_agl_ft": 450,
        "visibility_sm": 2,
        "cloud_clearance_horizontal_ft": 1000,
        "cloud_clearance_vertical_ft": 300,
        "airspace_class": "D",
        "laanc_authorization": False
    })
    assert result["decision"]["status"] == "NO-GO"
    assert any(f["rule_id"] == "ALT-400" and f["status"] == "fail" for f in result["findings"])
