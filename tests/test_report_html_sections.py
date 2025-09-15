from genticode.html import render_html


def test_html_includes_prompt_supply_and_delta_sections():
    report = {
        "schema_version": "0.1.0",
        "genticode_version": "x",
        "summary": {"counts": {"total": 0}},
        "packs": [
            {"name": "prompt", "counts": {"prompts": 1, "lints": {"PROMPT_MISSING_ID": 2}}},
            {"name": "supply", "counts": {"license_violations": 1, "by_severity": {"high": 2}}},
        ],
        "delta": {
            "prompt": {"lints": {"PROMPT_MISSING_ID": 1}},
            "supply": {"license_violations": 1, "vulns": {"high": 1}},
        },
    }
    html = render_html(report)
    assert "Prompt Lints" in html
    assert "Supply (SBOM)" in html
    assert "Delta" in html
    assert "PROMPT_MISSING_ID" in html and "+1" in html
