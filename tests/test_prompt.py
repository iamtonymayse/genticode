from pathlib import Path
import json
import ast

from genticode.prompt.detect import scan_paths
from genticode.prompt.manifest import build_manifest, _lint_codes
from genticode.prompt.autofix import suggest_autofix


FIXT = Path(__file__).parent / "fixtures" / "prompt"


def test_prompt_detection_python_and_ts():
    spans = scan_paths([FIXT / "sample.py", FIXT / "sample.ts"])
    # Expect multiple spans across files
    assert len(spans) >= 3
    files = {s.file.name for s in spans}
    assert {"sample.py", "sample.ts"}.issubset(files)
    # Spans have line information
    for s in spans:
        assert s.start >= 1
        assert s.end >= s.start
    roles = {s.role for s in spans}
    assert "system" in roles
    assert "user" in roles


def test_manifest_build_and_lints():
    spans = scan_paths([FIXT / "sample.py", FIXT / "sample.ts"])
    m = build_manifest(spans)
    assert m["schema"] == "prompt-manifest/0.1"
    assert len(m["items"]) >= 2
    # Each item has required fields
    first = m["items"][0]
    for k in ("id", "file", "start", "end", "role", "version", "source_hash", "lints"):
        assert k in first
    # Lint codes detect placeholders and long URLs
    codes = _lint_codes("PROMPT_ID: ABC v2 visit https://example.com/" + "a" * 100)
    assert "LONG_URL" in codes
    assert "PROMPT_MISSING_ID" not in codes
    assert "PROMPT_MISSING_VERSION" not in codes
    codes2 = _lint_codes("token sk-ABCDEF0123456789ABCDE")
    assert "SECRET_PLACEHOLDER" in codes2


def test_autofix_python_extract_constant():
    src = (FIXT / "sample.py").read_text()
    # literal appears in file
    lit = "You are a helpful assistant.\nFollow the user's instructions carefully.\n"
    fix = suggest_autofix("py", src, lit, "deadbeef1234")
    # patched code compiles
    ast.parse(fix.patched)
    assert "PROMPT_DEADBEEF1234" in fix.patched


def test_autofix_js_extract_constant():
    src = (FIXT / "sample.ts").read_text()
    lit = "You are a coding agent.\nRespond concisely.\n"
    fix = suggest_autofix("ts", src, lit, "cafebabefeed")
    assert "const PROMPT_CAFEBABEFEED = `" in fix.patched
    assert "PROMPT_CAFEBABEFEED" in fix.patched


def test_scan_repo_skips_internal(tmp_path):
    # Create structure with ignored dirs
    (tmp_path / ".genticode").mkdir()
    (tmp_path / ".venv").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "code").mkdir()
    (tmp_path / "code" / "a.py").write_text("X = 'You are test'\n")
    from genticode.prompt.detect import scan_repo

    spans = scan_repo(tmp_path)
    assert any(s.file.name == "a.py" for s in spans)


def test_scan_paths_handles_syntax_error(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("def oops(:\n  x=1\n")
    spans = scan_paths([bad])
    assert spans == []


def test_cli_check_emits_manifest(tmp_path, monkeypatch):
    # Run check within a temp dir copying fixtures to ensure isolation
    work = tmp_path
    (work / "tests/fixtures/prompt").mkdir(parents=True)
    (work / "tests/fixtures/prompt/sample.py").write_text((FIXT / "sample.py").read_text())
    (work / "tests/fixtures/prompt/sample.ts").write_text((FIXT / "sample.ts").read_text())

    # Create a minimal package to invoke module
    import subprocess, sys
    from shutil import copytree

    copytree((Path(__file__).parents[1] / "genticode"), work / "genticode")
    (work / "PRIORITY.yaml").write_text("# stub\n")

    cp = subprocess.run([sys.executable, "-m", "genticode", "check"], cwd=work, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    assert (work / ".genticode/prompts.manifest.json").exists()
    report = json.loads((work / ".genticode/report.json").read_text())
    packs = {p["name"]: p for p in report.get("packs", [])}
    assert "prompt" in packs
    assert packs["prompt"]["counts"]["prompts"] >= 2
