import shutil
import subprocess
from pathlib import Path

from genticode.supply.sbom import maybe_cyclonedx_py, maybe_cyclonedx_npm


def test_cyclonedx_py_exception(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/cyclonedx-py" if name == "cyclonedx-py" else shutil.which(name))
    def boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr("subprocess.run", boom)
    assert maybe_cyclonedx_py(tmp_path, tmp_path / "o.json") is None


def test_cyclonedx_npm_exception(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/npx" if name == "npx" else shutil.which(name))
    def boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr("subprocess.run", boom)
    assert maybe_cyclonedx_npm(tmp_path, tmp_path / "o.json") is None

