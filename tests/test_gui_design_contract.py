import sys
from pathlib import Path

ROOT = Path("/Users/davidusa/REPOS/Knowledge_Atlas")
sys.path.insert(0, str(ROOT))

from scripts.check_gui_design_contract import evaluate_file, load_config


def write_html(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def test_good_html_passes_required_checks(tmp_path: Path):
    config = load_config(ROOT / "config" / "gui_design_success_conditions.json")
    html = """
    <html>
      <head>
        <title>Good Page</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>.grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }</style>
      </head>
      <body>
        <nav>Menu</nav>
        <div class="hero-title">Start Here</div>
        <a href="next.html" class="btn-primary">Go</a>
        <div class="page-purpose">Purpose</div>
        <div>Evidence and sources</div>
      </body>
    </html>
    """
    path = write_html(tmp_path, "good.html", html)
    results = evaluate_file(path, config)
    required_failures = [r for r in results if r.severity == "required" and not r.passed]
    assert required_failures == []


def test_missing_title_fails_required_checks(tmp_path: Path):
    config = load_config(ROOT / "config" / "gui_design_success_conditions.json")
    html = """
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>@media (max-width: 700px) { .x { display:block; } }</style>
      </head>
      <body>
        <nav>Menu</nav>
        <h1>Page</h1>
      </body>
    </html>
    """
    path = write_html(tmp_path, "bad.html", html)
    results = evaluate_file(path, config)
    failed = {r.check_id for r in results if r.severity == "required" and not r.passed}
    assert "has_title" in failed
