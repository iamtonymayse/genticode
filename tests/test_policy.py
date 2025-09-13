from pathlib import Path
import textwrap


def test_policy_load_defaults_when_missing(tmp_path, monkeypatch):
    from genticode import policy
    cfg = policy.load(tmp_path / "nope.yaml")
    assert cfg.get_phase() in {"warn", "new_code_only", "hard"}
    assert cfg.get_budget("static", "high") == 0


def test_policy_load_and_validate(tmp_path):
    from genticode import policy
    p = tmp_path / "policy.yaml"
    p.write_text(textwrap.dedent(
        """
        version: 1
        severity_map: {info: 0, low: 10, medium: 50, high: 80}
        progressive_enforcement: {phase: hard}
        packs:
          static: {enabled: true, timeout_s: 120}
        budgets:
          static: {high: 0}
        """
    ))
    cfg = policy.load(p)
    assert cfg.get_phase() == "hard"
    assert cfg.get_budget("static", "high") == 0
    assert cfg.packs["static"].timeout_s == 120
    # budget default path
    assert cfg.get_budget("static", "medium", default=3) == 3
    # severity map applied
    assert cfg.severity_map["low"] == 10


def test_policy_rejects_bad_types(tmp_path):
    from genticode import policy
    p = tmp_path / "policy.yaml"
    p.write_text("severity_map: [1,2,3]\n")
    try:
        policy.load(p)
    except policy.PolicyError as e:
        assert "severity_map" in str(e)
    else:
        raise AssertionError("expected PolicyError")


def test_policy_invalid_phase(tmp_path):
    from genticode import policy
    p = tmp_path / "policy.yaml"
    p.write_text("progressive_enforcement: {phase: maybe}\n")
    try:
        policy.load(p)
    except policy.PolicyError as e:
        assert "progressive_enforcement" in str(e)
    else:
        raise AssertionError("expected PolicyError")


def test_policy_root_must_be_mapping(tmp_path):
    from genticode import policy
    p = tmp_path / "policy.yaml"
    p.write_text("[1,2,3]\n")
    try:
        policy.load(p)
    except policy.PolicyError as e:
        assert "root" in str(e)
    else:
        raise AssertionError("expected PolicyError")


def test_policy_safe_load_exception_raises(tmp_path, monkeypatch):
    from genticode import policy
    p = tmp_path / "policy.yaml"
    p.write_text("version: 1\n")
    import yaml as _yaml
    monkeypatch.setattr(_yaml, "safe_load", lambda *a, **k: (_ for _ in ()).throw(ValueError("boom")))
    try:
        policy.load(p)
    except policy.PolicyError as e:
        assert "Failed to load policy" in str(e)
    else:
        raise AssertionError("expected PolicyError")


def test_policy_empty_yaml_uses_defaults(tmp_path):
    from genticode import policy
    p = tmp_path / "policy.yaml"
    p.write_text("\n")
    cfg = policy.load(p)
    assert cfg.version == 1
    assert cfg.get_phase() in {"warn", "new_code_only", "hard"}


def test_policy_packs_mapping_and_ruleset(tmp_path):
    from genticode import policy
    p = tmp_path / "policy.yaml"
    p.write_text(textwrap.dedent(
        """
        packs:
          static: {enabled: false, timeout_s: 42, ruleset: strict}
        budgets:
          static: {high: 1}
        progressive_enforcement: {phase: new_code_only}
        """
    ))
    cfg = policy.load(p)
    assert cfg.packs["static"].enabled is False
    assert cfg.packs["static"].timeout_s == 42
    assert cfg.packs["static"].ruleset == "strict"
    assert cfg.get_phase() == "new_code_only"
    assert cfg.get_budget("static", "high") == 1


def test_policy_pack_must_be_mapping(tmp_path):
    from genticode import policy
    p = tmp_path / "policy.yaml"
    p.write_text("packs: {static: true}\n")
    try:
        policy.load(p)
    except policy.PolicyError as e:
        assert "pack 'static'" in str(e)
    else:
        raise AssertionError("expected PolicyError")
