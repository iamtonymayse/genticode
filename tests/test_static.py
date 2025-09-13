import json
from pathlib import Path

from genticode.static.semgrep import normalize_semgrep, maybe_run_semgrep


def test_normalize_semgrep_fixture():
    data = json.loads((Path(__file__).parent / "fixtures/semgrep/sample.json").read_text())
    findings = normalize_semgrep(data)
    assert len(findings) == 2
    first = findings[0]
    for k in ("file", "start", "end", "rule", "severity", "message"):
        assert k in first


def test_maybe_run_semgrep_monkey(monkeypatch, tmp_path):
    data = (Path(__file__).parent / "fixtures/semgrep/sample.json").read_text()

    class FakeCP:
        def __init__(self, stdout: str):
            self.stdout = stdout

    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/semgrep")
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: FakeCP(stdout=data),
    )
    out = tmp_path / "semgrep.json"
    result = maybe_run_semgrep(tmp_path, out)
    assert result is not None
    assert out.exists()
    findings = normalize_semgrep(result)
    assert len(findings) == 2
