import json
from pathlib import Path

from genticode.supply.sbom import maybe_cyclonedx_npm


def test_maybe_cyclonedx_npm_reads_file(monkeypatch, tmp_path):
    out = tmp_path / "sbom-node.json"
    sample = (Path(__file__).parent / "fixtures/sbom/python.json").read_text()

    class FakeCP:
        def __init__(self, stdout: str = ""):
            self.stdout = stdout

    def fake_run(*a, **k):
        out.write_text(sample)
        return FakeCP()

    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/npx")
    monkeypatch.setattr("subprocess.run", fake_run)
    data = maybe_cyclonedx_npm(tmp_path, out)
    assert data is not None and "components" in data

