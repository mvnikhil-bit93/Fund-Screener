"""Conservative static import guard, not a proof of runtime function purity."""

import ast
import sys
from importlib.util import resolve_name
from pathlib import Path

PURE_ROOTS = frozenset(
    {
        "__future__",
        "abc",
        "bisect",
        "collections",
        "dataclasses",
        "datetime",
        "decimal",
        "enum",
        "fractions",
        "functools",
        "hashlib",
        "itertools",
        "json",
        "math",
        "operator",
        "re",
        "statistics",
        "struct",
        "typing",
        "numpy",
        "polars",
        "pydantic",
    }
)
FORBIDDEN_CALLS = frozenset({"open", "input", "exec", "eval", "__import__", "breakpoint"})
CLOCK_CALLS = frozenset({"now", "utcnow", "today"})


def allowed(module: str, package: str) -> bool:
    if module in {"ledger.types", "ledger"}:
        return module == "ledger.types"
    if module.startswith("ledger.types."):
        return True
    if module == "engines" or module.startswith("engines."):
        return package == "engines"
    return module.partition(".")[0] in PURE_ROOTS


def inspect_source(source: str, module: str, package: str) -> list[str]:
    """Resolve relative imports so they cannot escape the allowed namespace."""
    errors = []
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom, ast.Call)):
            continue
        imported: list[str] = []
        if isinstance(node, ast.Import):
            imported = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            name = "." * node.level + (node.module or "")
            if node.level:
                try:
                    name = resolve_name(name, module)
                except ImportError:
                    errors.append(f"line {node.lineno}: relative import escapes its package")
                    continue
            # 'from . import io' must check the imported submodule as well.
            imported = (
                [name + "." + alias.name for alias in node.names] if node.module is None else [name]
            )
        for name in imported:
            if not allowed(name, package):
                errors.append(f"line {node.lineno}: {name} is not a permitted pure import")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in FORBIDDEN_CALLS:
                errors.append(f"line {node.lineno}: {func.id} is forbidden in pure modules")
            elif isinstance(func, ast.Attribute) and func.attr in CLOCK_CALLS:
                errors.append(f"line {node.lineno}: clock calls are forbidden in pure modules")
    return errors


def check(root: Path) -> list[str]:
    engines = root / "packages/engines/src/engines"
    ledger = root / "packages/ledger/src/ledger"
    files = sorted(engines.rglob("*.py"))
    files += [path for path in [ledger / "__init__.py", ledger / "types.py"] if path.exists()]
    files += sorted((ledger / "types").rglob("*.py"))
    errors = []
    for path in files:
        package = "engines" if path.is_relative_to(engines) else "ledger"
        base = engines if package == "engines" else ledger
        parent = ".".join((package, *path.relative_to(base).parts[:-1]))
        for error in inspect_source(path.read_text(), parent, package):
            errors.append(f"{path.relative_to(root)}: {error}")
    return errors


def main() -> int:
    errors = check(Path(__file__).resolve().parents[1])
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Engine and ledger-types static import checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
