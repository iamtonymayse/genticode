from genticode.sarif import _level_from_severity


def test_level_from_severity_variants():
    assert _level_from_severity("CRITICAL") == "error"
    assert _level_from_severity("medium") == "warning"
    assert _level_from_severity("info") == "note"

