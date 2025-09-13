from __future__ import annotations


def to_sarif(report: dict) -> dict:
    # Minimal SARIF v2.1.0 structure with empty results.
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "genticode",
                        "semanticVersion": str(report.get("genticode_version", "0")),
                        "rules": [],
                    }
                },
                "results": [],
            }
        ],
    }

