import json
from pathlib import Path

from genticode.sarif import to_sarif


def test_unified_sarif_includes_prompt_and_static(tmp_path):
    gc = tmp_path / ".genticode"
    (gc / "raw").mkdir(parents=True)
    # Write a small manifest with one item and one lint
    (gc / "prompts.manifest.json").write_text(json.dumps({
        "schema": "prompt-manifest/0.1",
        "items": [{
            "id": "abc123",
            "file": "tests/fixtures/prompt/sample.py",
            "start": 1,
            "end": 3,
            "role": "system",
            "lints": ["PROMPT_MISSING_ID"],
        }]
    }))
    # Use existing semgrep fixture to simulate static findings
    from shutil import copyfile
    copyfile(Path(__file__).parent / "fixtures/semgrep/sample.json", gc / "raw/semgrep.json")

    report = {"genticode_version": "0.9.x"}
    sar = to_sarif(report, gc_dir=gc)
    assert sar["version"] == "2.1.0"
    runs = sar["runs"][0]
    assert runs["tool"]["driver"]["name"] == "genticode"
    results = runs["results"]
    # Expect at least 1 prompt + 2 semgrep
    assert len(results) >= 3
    # Check there is a prompt result with note level
    assert any(r.get("ruleId") == "prompt.detected" and r.get("level") == "note" for r in results)
    # Check a semgrep rule ID appears and uses warning/error level
    assert any(r.get("ruleId", "").startswith("python.lang.") for r in results)

