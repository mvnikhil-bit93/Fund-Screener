"""Exercise import-linter's actual configuration against an isolated violation."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_import_linter_rejects_an_engine_access_import(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    shutil.copy2(root / ".importlinter", tmp_path / ".importlinter")
    sources = []
    for namespace in ("ledger", "ingest", "engines", "access"):
        source = root / "packages" / namespace / "src"
        target = tmp_path / "packages" / namespace / "src"
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
        sources.append(str(target))
    violation = tmp_path / "packages/engines/src/engines/_forbidden_probe.py"
    violation.write_text("import access\n")
    # Only the temporary copy is mutated. The real packages stay clean.
    environment = {**os.environ, "PYTHONPATH": os.pathsep.join(sources)}
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from importlinter.cli import lint_imports_command; "
            "raise SystemExit(lint_imports_command())",
            "--no-cache",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "BROKEN" in result.stdout
    assert "engines._forbidden_probe -> access" in result.stdout
