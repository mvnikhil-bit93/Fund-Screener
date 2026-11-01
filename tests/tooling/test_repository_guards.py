"""Prove the scaffold checks reject violations rather than just exit zero."""

from pathlib import Path

import pytest

from scripts.check_allowlist import check
from scripts.check_engine_imports import inspect_source


@pytest.mark.parametrize(
    "declaration",
    [
        '[project]\ndependencies = ["requests>=2"]',
        '[project.optional-dependencies]\nlive = ["requests>=2"]',
        '[dependency-groups]\nlive = ["requests>=2"]',
        '[build-system]\nrequires = ["requests>=2"]',
    ],
)
def test_unapproved_dependency_is_rejected(tmp_path: Path, declaration: str) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.fund-intel.allowlist]\npytest = "Offline checks"\n' + declaration
    )
    assert any("requests needs an allowlist entry" in error for error in check(tmp_path))


def test_workspace_member_dependencies_are_checked(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.fund-intel.allowlist]\npytest = "Offline checks"\n'
    )
    member = tmp_path / "packages" / "ledger"
    member.mkdir(parents=True)
    (member / "pyproject.toml").write_text('[project]\ndependencies = ["requests"]\n')
    assert any("packages/ledger/pyproject.toml" in error for error in check(tmp_path))


def test_allowlist_canonicalizes_names_and_requires_reasons(tmp_path: Path) -> None:
    manifest = tmp_path / "pyproject.toml"
    manifest.write_text(
        '[tool.fund-intel.allowlist]\nmy_package = "Typed models"\n'
        '[project]\ndependencies = ["my-package>=1"]\n'
    )
    assert check(tmp_path) == []
    manifest.write_text(manifest.read_text().replace('"Typed models"', '""'))
    assert check(tmp_path)


@pytest.mark.parametrize(
    "source",
    [
        "import access",
        "from ledger import io",
        "from ledger.views import latest_as_of",
        "import pathlib",
        "import requests",
        "import os",
        "import random",
        "import time",
        "from .. import access",
        "open('holdings.csv')",
        "__import__('os')",
        "from datetime import datetime\ndatetime.now()",
    ],
)
def test_impure_engine_imports_or_calls_are_rejected(source: str) -> None:
    assert inspect_source(source, "engines", "engines")


def test_engine_can_use_its_helpers_and_pure_ledger_types() -> None:
    source = (
        "from ledger.types import Holding\nfrom . import _common\n"
        "from datetime import date\nimport polars as pl\n"
    )
    assert inspect_source(source, "engines", "engines") == []


def test_ledger_types_cannot_hide_io_or_engine_dependencies() -> None:
    assert inspect_source("from . import io", "ledger", "ledger")
    assert inspect_source("import engines", "ledger", "ledger")
