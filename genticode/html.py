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
  </body>
</html>\n"""
