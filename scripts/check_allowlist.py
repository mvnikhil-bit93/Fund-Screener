"""Check direct workspace, extra, development, and build dependencies."""

import sys
import tomllib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name


def requirements(document: dict[str, Any]) -> Iterator[str]:
    """Include every declared group, even when it is not currently installed."""
    project = document.get("project", {})
    yield from project.get("dependencies", [])
    for extra in project.get("optional-dependencies", {}).values():
        yield from extra
    for group in document.get("dependency-groups", {}).values():
        for entry in group:
            if isinstance(entry, str):
                yield entry
    yield from document.get("build-system", {}).get("requires", [])


def check(root: Path) -> list[str]:
    """Return actionable errors without modifying any project files."""
    root_document = tomllib.loads((root / "pyproject.toml").read_text())
    allowlist = root_document.get("tool", {}).get("fund-intel", {}).get("allowlist", {})
    allowed = {
        canonicalize_name(name)
        for name, reason in allowlist.items()
        if isinstance(reason, str) and reason.strip()
    }
    errors = []
    paths = [root / "pyproject.toml", *sorted(root.glob("packages/*/pyproject.toml"))]
    for path in paths:
        document = tomllib.loads(path.read_text())
        for specification in requirements(document):
            try:
                name = canonicalize_name(Requirement(specification).name)
            except InvalidRequirement:
                errors.append(f"{path.relative_to(root)}: invalid requirement {specification!r}")
                continue
            if name not in allowed:
                errors.append(
                    f"{path.relative_to(root)}: {name} needs an allowlist entry with a reason"
                )
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = check(root)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("All direct dependencies have documented allowlist entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
