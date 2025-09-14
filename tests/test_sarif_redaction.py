import json
from pathlib import Path

from genticode.sarif import to_sarif


def test_sarif_redacts_tokens(tmp_path):
    gc = tmp_path / ".genticode"
    (gc / "raw").mkdir(parents=True, exist_ok=True)
    # Write a fake semgrep result embedding a token
    semgrep = {
        "results": [
            {
                "check_id": "test.rule",
                "extra": {"severity": "high", "message": "leak ghp_ABCDEF0123456789ABCDE"},
                "path": "a.py",
                "start": {"line": 1},
                "end": {"line": 1},
            }
        ]
    }
    (gc / "raw" / "semgrep.json").write_text(json.dumps(semgrep))
    sarif = to_sarif({"genticode_version": "0.0"}, gc)
    out = json.dumps(sarif)
    assert "ghp_ABCDEF0123456789ABCDE" not in out
    assert "<REDACTED>" in out

