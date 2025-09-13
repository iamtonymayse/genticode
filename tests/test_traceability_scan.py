from pathlib import Path
from genticode.traceability.parser import scan_test_coverage


def test_scan_test_coverage(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_a.py").write_text("# AC_1 in this test\n")
    (tmp_path / "tests/test_b.py").write_text("# no id here\n")
    cov = scan_test_coverage(tmp_path, ["AC_1", "AC_2"])
    assert cov["AC_1"] >= 1 and cov["AC_2"] == 0

