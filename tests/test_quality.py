import json
from pathlib import Path

from genticode.quality.linter import maybe_run_quality


def test_maybe_run_quality_sums_tools(monkeypatch, tmp_path):
    # Simulate both tools present
    calls = {"ruff": 0, "eslint": 0}

    def which(name):
        return "/usr/bin/" + name

    class FakeCP:
        def __init__(self, stdout: str):
            self.stdout = stdout

    def fake_run(cmd, cwd, capture_output, text, check):
        if "ruff" in cmd[0]:
            calls["ruff"] += 1
            # ruff JSON is a list per file
            return FakeCP(stdout=json.dumps([{"filename": "a.py", "messages": []}, {"filename": "b.py", "messages": []}]))
        else:
            calls["eslint"] += 1
            # eslint JSON list with messages arrays
            return FakeCP(stdout=json.dumps([
                {"filePath": "a.js", "messages": [{"ruleId": "x", "severity": 2}]},
                {"filePath": "b.js", "messages": [{"ruleId": "y", "severity": 1}, {"ruleId": "z", "severity": 1}]}
            ]))

    monkeypatch.setattr("shutil.which", which)
    monkeypatch.setattr("subprocess.run", fake_run)
    counts = maybe_run_quality(tmp_path)
    # 2 ruff items + 3 eslint messages
    assert counts["findings"] == 5
    assert calls["ruff"] == 1 and calls["eslint"] == 1
    bysev = counts["by_severity"]
    assert bysev.get("error") == 1 and bysev.get("warning") == 4
