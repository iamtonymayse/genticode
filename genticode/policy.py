from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    yaml = None  # type: ignore


@dataclass
class PackConfig:
    enabled: bool = True
    timeout_s: int = 600
    ruleset: Optional[str] = None


@dataclass
class PolicyConfig:
    version: int = 1
    severity_map: Dict[str, int] = field(default_factory=lambda: {"info": 0, "low": 20, "medium": 50, "high": 80, "critical": 95})
    progressive_enforcement: Dict[str, Any] = field(default_factory=lambda: {"phase": "new_code_only"})
    packs: Dict[str, PackConfig] = field(default_factory=dict)
    budgets: Dict[str, Any] = field(default_factory=dict)
    licenses: Dict[str, Any] = field(default_factory=dict)

    def get_phase(self) -> str:
        return str(self.progressive_enforcement.get("phase", "warn"))

    def get_budget(self, pack: str, severity: str, default: int = 0) -> int:
        p = self.budgets.get(pack, {})
        return int(p.get(severity, default))


class PolicyError(Exception):
    pass


def _validate_dict(d: dict, key: str, typ):
    if key in d and not isinstance(d[key], typ):
        raise PolicyError(f"Invalid type for '{key}': expected {typ.__name__}")


def load(path) -> PolicyConfig:
    """Load and validate policy.yaml into PolicyConfig.

    Minimal YAML schema with helpful errors; supports missing file by returning defaults.
    """
    cfg = PolicyConfig()
    try:
        if yaml is None:
            # Fallback: treat as defaults if PyYAML missing
            return cfg
        import os
        if not os.path.exists(path):
            return cfg
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except Exception as e:
        raise PolicyError(f"Failed to load policy: {e}")

    if not isinstance(raw, dict):
        raise PolicyError("policy root must be a mapping")

    # Top-level validations
    _validate_dict(raw, "version", int)
    _validate_dict(raw, "severity_map", dict)
    _validate_dict(raw, "progressive_enforcement", dict)
    _validate_dict(raw, "packs", dict)
    _validate_dict(raw, "budgets", dict)
    _validate_dict(raw, "licenses", dict)

    if "version" in raw:
        cfg.version = int(raw["version"])
    if "severity_map" in raw:
        if not all(isinstance(v, int) for v in raw["severity_map"].values()):
            raise PolicyError("severity_map values must be integers")
        cfg.severity_map = dict(raw["severity_map"])
    if "progressive_enforcement" in raw:
        pe = raw["progressive_enforcement"]
        phase = pe.get("phase", "warn")
        if phase not in {"warn", "new_code_only", "hard"}:
            raise PolicyError("progressive_enforcement.phase must be one of: warn,new_code_only,hard")
        cfg.progressive_enforcement = {"phase": phase}
    if "budgets" in raw:
        cfg.budgets = dict(raw["budgets"])  # structure free-form per pack
    if "packs" in raw:
        packs: Dict[str, PackConfig] = {}
        for name, val in raw["packs"].items():
            if not isinstance(val, dict):
                raise PolicyError(f"pack '{name}' must be a mapping")
            enabled = bool(val.get("enabled", True))
            timeout_s = int(val.get("timeout_s", 600))
            ruleset = val.get("ruleset")
            packs[name] = PackConfig(enabled=enabled, timeout_s=timeout_s, ruleset=ruleset)
        cfg.packs = packs

    # Optional license rules (allow/deny/fail_on_unknown)
    if "licenses" in raw:
        cfg.licenses = dict(raw["licenses"])  # type: ignore[assignment]

    return cfg
