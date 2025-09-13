import json
from pathlib import Path
import importlib.util


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def test_group_failures_and_write(tmp_path):
    mod = load_module(Path("scripts/attempt.py"))
    # minimal pytest JSON
    data = {
        "tests": [
            {"nodeid": "t::a", "outcome": "failed", "call": {"longrepr": "AssertionError"}},
            {"nodeid": "t::b", "outcome": "passed"},
            {"nodeid": "t::c", "outcome": "failed", "call": {"longrepr": "ImportError: x"}},
        ]
    }
    groups = mod.group_failures(data)
    assert "Test" in groups and "Tooling" in groups
    idx = mod.next_attempt_index(tmp_path)
    # write into tmp attempt dir
    old = mod.ATTEMPTS_DIR
    oldr = mod.REPORTS_DIR
    try:
        mod.ATTEMPTS_DIR = tmp_path
        mod.REPORTS_DIR = tmp_path
        jpath, mpath = mod.write_attempt(idx, {"exit_code": 1, "groups": groups, "env": {"python": "x"}})
        assert jpath.exists() and mpath.exists()
        loaded = json.loads(jpath.read_text())
        assert loaded["exit_code"] == 1
    finally:
        mod.ATTEMPTS_DIR = old
        mod.REPORTS_DIR = oldr


def test_decision_helper():
    dec = load_module(Path("scripts/lessons_decide.py"))
    prev = {"groups": {"Test": [{"n": 1}]}}
    curr = {"groups": {"Test": [{"n": 2}], "Code": [{"n": 3}]}}
    d, pct = dec.decide(prev, curr)
    assert d == "RETRY" and pct > 50.0


def test_attempt_build_summary_and_index(tmp_path):
    mod = load_module(Path("scripts/attempt.py"))
    data = {"tests": [
        {"outcome": "failed", "call": {"longrepr": "timeout"}},
        {"outcome": "failed", "call": {"longrepr": "Unhandled exception"}},
    ]}
    summ = mod.build_summary(1, data)
    assert summ["exit_code"] == 1 and summ["counts"]["Environment"] == 1 and summ["counts"]["Code"] == 1
    # existing attempt files increment index
    (tmp_path / "attempt-2.json").write_text("{}")
    assert mod.next_attempt_index(tmp_path) == 3


def test_lessons_decide_main(tmp_path, capsys):
    dec = load_module(Path("scripts/lessons_decide.py"))
    prev = tmp_path / "prev.json"
    curr = tmp_path / "curr.json"
    prev.write_text(json.dumps({"groups": {"Code": [{"n": 1}]}}))
    curr.write_text(json.dumps({"groups": {"Code": [{"n": 1}], "Environment": [{"n": 2}]}}))
    rc = dec.main(["--prev", str(prev), "--curr", str(curr)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "RETRY" in out or "SPLIT" in out


def test_attempt_main_integration(tmp_path, monkeypatch):
    mod = load_module(Path("scripts/attempt.py"))
    # Redirect paths into tmp
    old_attempts, old_reports, old_raw = mod.ATTEMPTS_DIR, mod.REPORTS_DIR, mod.RAW_JSON
    mod.ATTEMPTS_DIR = tmp_path / "attempts"
    mod.REPORTS_DIR = tmp_path / "reports"
    mod.RAW_JSON = tmp_path / "pytest.json"

    class FakeCP:
        def __init__(self, returncode=1):
            self.returncode = returncode

    def fake_run(cmd, text=True):
        # Write a minimal JSON to RAW_JSON
        mod.RAW_JSON.parent.mkdir(parents=True, exist_ok=True)
        mod.RAW_JSON.write_text(json.dumps({
            "tests": [
                {"outcome": "failed", "call": {"longrepr": "AssertionError"}}
            ]
        }))
        return FakeCP(1)

    monkeypatch.setattr("subprocess.run", fake_run)
    try:
        rc = mod.main()
        assert rc == 1
        # Attempt 1 files written under tmp dirs
        assert (mod.ATTEMPTS_DIR / "attempt-1.json").exists()
        assert (mod.REPORTS_DIR / "attempt-1.md").exists()
    finally:
        mod.ATTEMPTS_DIR, mod.REPORTS_DIR, mod.RAW_JSON = old_attempts, old_reports, old_raw


def test_lessons_decide_split_case():
    dec = load_module(Path("scripts/lessons_decide.py"))
    prev = {"groups": {"Test": [{}], "Code": [{}]}}
    curr = {"groups": {"Test": [{}], "Code": [{}]}}
    d, pct = dec.decide(prev, curr)
    assert d == "SPLIT" and pct == 0.0
