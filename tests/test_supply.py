import json
from pathlib import Path

from genticode.supply.license import evaluate_licenses
from genticode.supply.sbom import maybe_cyclonedx_py, maybe_cyclonedx_npm


def test_license_evaluator_counts():
    data = json.loads((Path(__file__).parent / "fixtures/sbom/python.json").read_text())
    total, detail = evaluate_licenses(data, allow={"MIT"}, deny={"AGPL-3.0"}, fail_on_unknown=True)
    assert total == 1
    assert detail["deny"] == ["AGPL-3.0"]
    # Unknown license path
    data["components"].append({"type": "library", "name": "mystery", "licenses": [{"license": {"id": "FooBar-1.0"}}]})
    total2, detail2 = evaluate_licenses(data, allow={"MIT"}, deny={"AGPL-3.0"}, fail_on_unknown=True)
    assert total2 == 2
    assert "FooBar-1.0" in detail2["unknown"]


def test_maybe_cyclonedx_py_reads_output(monkeypatch, tmp_path):
    out = tmp_path / "sbom.json"
    sample = (Path(__file__).parent / "fixtures/sbom/python.json").read_text()

    class FakeCP:
        def __init__(self, stdout: str = ""):
            self.stdout = stdout

    def fake_run(*a, **k):
        out.write_text(sample)
        return FakeCP()

    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/cyclonedx-py")
    monkeypatch.setattr("subprocess.run", fake_run)
    data = maybe_cyclonedx_py(tmp_path, out)
    assert data is not None
    assert "components" in data


def test_maybe_cyclonedx_npm_reads_stdout(monkeypatch, tmp_path):
    out = tmp_path / "sbom-node.json"
    sample = (Path(__file__).parent / "fixtures/sbom/python.json").read_text()

    class FakeCP:
        def __init__(self, stdout: str):
            self.stdout = stdout

    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/npx")
    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeCP(stdout=sample))
    data = maybe_cyclonedx_npm(tmp_path, out)
    assert data is not None
    assert "components" in data


def test_maybe_cyclonedx_py_reads_stdout(monkeypatch, tmp_path):
    out = tmp_path / "sbom.json"
    sample = (Path(__file__).parent / "fixtures/sbom/python.json").read_text()

    class FakeCP:
        def __init__(self, stdout: str):
            self.stdout = stdout

    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/cyclonedx-py")
    # Do not create output file; rely on stdout
    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeCP(stdout=sample))
    data = maybe_cyclonedx_py(tmp_path, out)
    assert data is not None
    assert "components" in data


def test_cyclonedx_tools_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert maybe_cyclonedx_py(tmp_path, tmp_path / "x.json") is None
    assert maybe_cyclonedx_npm(tmp_path, tmp_path / "y.json") is None
