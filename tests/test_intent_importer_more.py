import importlib.util
from pathlib import Path
import json


def _load(repo_root: Path):
    mod_path = repo_root / "tools/intent_import.py"
    spec = importlib.util.spec_from_file_location("intent_import", mod_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def test_validate_req_and_dec_failures(tmp_path):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    # Missing keys
    try:
        mod._validate_req({"data": {"id": "X"}})
        assert False
    except SystemExit:
        pass
    try:
        mod._validate_dec({"data": {"id": "D"}})
        assert False
    except SystemExit:
        pass


def test_print_diffs_outputs_unified(tmp_path, capsys):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    ch = mod.PendingChange(path=tmp_path/"f.txt", old="a\n", new="b\n")
    mod.print_diffs([ch])
    out = capsys.readouterr().out
    assert out.startswith('---') and '+++' in out

