import subprocess, sys
from pathlib import Path


def test_iast_null_provider():
    cp = subprocess.run([sys.executable, "-m", "genticode", "iast"], capture_output=True, text=True)
    assert cp.returncode == 0
    assert "IAST null provider" in cp.stdout

