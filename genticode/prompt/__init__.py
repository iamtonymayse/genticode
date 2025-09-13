from .detect import scan_repo
from .manifest import build_manifest
from .autofix import suggest_autofix

__all__ = ["scan_repo", "build_manifest", "suggest_autofix"]

