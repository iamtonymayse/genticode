from pathlib import Path
from genticode.report import build_empty_report, add_pack_summary


def test_build_empty_report_and_add_pack_summary(tmp_path):
    r = build_empty_report(version="x.y.z", baseline_present=False)
    assert r["schema_version"] == "0.1.0"
    assert r["baseline"]["present"] is False
    add_pack_summary(r, pack="demo", counts={"findings": 3})
    assert any(p["name"] == "demo" and p["counts"]["findings"] == 3 for p in r["packs"])

