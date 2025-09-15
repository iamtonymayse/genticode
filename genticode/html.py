from __future__ import annotations


def render_html(report: dict) -> str:
    total = report.get("summary", {}).get("counts", {}).get("total", 0)
    schema = report.get("schema_version", "?")
    ver = report.get("genticode_version", "?")
    packs = report.get("packs", []) or []
    tabs = "".join(
        f"<li><strong>{p.get('name')}</strong>: {p.get('counts', {}).get('findings', p.get('counts', {}).get('prompts', 0))}</li>"
        for p in packs
    )
    # Prompt lints summary
    prompt = next((p for p in packs if p.get("name") == "prompt"), None)
    prompt_lints = (prompt or {}).get("counts", {}).get("lints") or {}
    lint_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in sorted(prompt_lints.items()))
    # Supply summary
    supply = next((p for p in packs if p.get("name") == "supply"), None)
    sup_counts = (supply or {}).get("counts", {})
    sup_lic = int(sup_counts.get("license_violations", 0))
    sup_by = sup_counts.get("by_severity") or {}
    sev_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in sorted(sup_by.items()))
    # Delta if present
    delta = report.get("delta") or {}
    d_prompt = ((delta.get("prompt") or {}).get("lints") or {})
    d_supply = delta.get("supply") or {}
    d_sev_rows = "".join(f"<tr><td>{k}</td><td>{v:+d}</td></tr>" for k, v in sorted(((d_supply.get("vulns") or {})).items()))
    return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>Genticode Report</title>
    <style>
      body {{ font-family: -apple-system, system-ui, Segoe UI, Roboto, sans-serif; margin: 2rem; }}
      .meta {{ color: #555; }}
      .pill {{ display: inline-block; padding: 0.2rem 0.6rem; background: #eef; border-radius: 0.5rem; }}
      .tabs li {{ display: inline-block; margin-right: 1rem; }}
    </style>
  </head>
  <body>
    <h1>Genticode Report</h1>
    <p class=\"meta\">Schema: {schema} • Version: {ver}</p>
    <ul class=\"tabs\">{tabs}</ul>
    <p>Total findings: <span class=\"pill\">{total}</span></p>
    <h2>Prompt Lints</h2>
    <table><tr><th>Code</th><th>Count</th></tr>{lint_rows or '<tr><td colspan=2>None</td></tr>'}</table>
    <h2>Supply (SBOM)</h2>
    <p>License violations: <strong>{sup_lic}</strong></p>
    <table><tr><th>Severity</th><th>Count</th></tr>{sev_rows or '<tr><td colspan=2>None</td></tr>'}</table>
    <h2>Delta</h2>
    <p>Prompt lint delta: {d_prompt}</p>
    <p>Supply license delta: {int(d_supply.get('license_violations', 0)):+d}</p>
    <table><tr><th>Severity</th><th>Δ</th></tr>{d_sev_rows or '<tr><td colspan=2>0</td></tr>'}</table>
  </body>
</html>\n"""
