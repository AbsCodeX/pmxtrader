"""Documentation accuracy invariants (Batch K)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_FILES = [
    "docs/README.md",
    "docs/environment.md",
    "docs/testing.md",
    "docs/known-risks.md",
    "docs/official-links.md",
    "docs/project-structure.md",
    "docs/commands.md",
]

README_SETUP_SCRIPTS = [
    "scripts/setup-direnv.sh",
    "scripts/setup-dev.sh",
    "scripts/setup-hermes.sh",
]

README_RUN_COMMANDS = [
    "pmx",
    "scripts/pmx.sh",
]

ENV_VARS_IN_DOCS = [
    "KALSHI_API_KEY",
    "POLYMARKET_US_KEY_ID",
    "PMX_READ_ONLY",
    "PMX_DRY_RUN",
    "PMX_MAX_TRADE_CONTRACTS",
    "PMXT_DASHBOARD_HOST",
]

TEST_COMMANDS_IN_DOCS = [
    "pytest tests/",
    "smoke-functionality.sh",
    "ruff check",
]


def test_core_doc_files_exist():
    for rel in DOC_FILES:
        assert (ROOT / rel).is_file(), rel


def test_mkdocs_config_exists():
    assert (ROOT / "mkdocs.yml").is_file()
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "material" in mkdocs
    assert "docs/README.md" in mkdocs or "README.md" in mkdocs


def test_docs_build_script_exists():
    assert (ROOT / "scripts/docs-build.sh").is_file()
    assert (ROOT / "requirements-docs.txt").is_file()


def test_readme_links_to_new_guides():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for fragment in (
        "docs/README.md",
        "docs/environment.md",
        "docs/testing.md",
        "docs/known-risks.md",
        "docs/official-links.md",
        "docs/project-structure.md",
    ):
        assert fragment in readme, fragment


def test_readme_setup_scripts_exist():
    for rel in README_SETUP_SCRIPTS:
        assert (ROOT / rel).is_file(), rel


def test_readme_mentions_safety_env_vars():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "PMX_READ_ONLY" in readme
    assert "PMX_DRY_RUN" in readme
    assert "PMX_MAX_TRADE_CONTRACTS" in readme


def test_environment_doc_covers_key_vars():
    env_doc = (ROOT / "docs/environment.md").read_text(encoding="utf-8")
    for var in ENV_VARS_IN_DOCS:
        assert var in env_doc, var
    assert "pmxt/.env.example" in env_doc


def test_testing_doc_covers_ci_commands():
    testing = (ROOT / "docs/testing.md").read_text(encoding="utf-8")
    for cmd in TEST_COMMANDS_IN_DOCS:
        assert cmd in testing, cmd


def test_known_risks_mentions_real_money_and_dashboard():
    risks = (ROOT / "docs/known-risks.md").read_text(encoding="utf-8")
    assert "real money" in risks.lower() or "Real money" in risks
    assert "dashboard" in risks.lower()
    assert "Grok" in risks or "MCP" in risks


def test_official_links_has_pmxt_and_venues():
    links = (ROOT / "docs/official-links.md").read_text(encoding="utf-8")
    assert "pmxt.dev" in links
    assert "kalshi.com" in links
    assert "polymarket.us" in links


def test_readme_doc_links_resolve():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for match in re.finditer(r"\]\((docs/[^)]+)\)", readme):
        rel = match.group(1).split("#")[0]
        if rel.endswith(".md"):
            assert (ROOT / rel).is_file(), rel


def test_docs_theme_css_tokens():
    css = (ROOT / "docs/stylesheets/extra.css").read_text(encoding="utf-8")
    for token in ("--oa-text", "--oa-font", "--oa-mono", "pmx-docs-chrome", "pmx-topbar"):
        assert token in css, token


def test_inner_docs_no_legacy_glass_heroes():
    for path in (ROOT / "docs").rglob("*.md"):
        if path.name == "README.md" and path.parent.name == "docs":
            continue
        text = path.read_text(encoding="utf-8")
        assert "pmx-glass" not in text, path.relative_to(ROOT)
