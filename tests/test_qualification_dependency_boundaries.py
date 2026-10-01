"""Static dependency-direction contract for qualification domains."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "licensetown"


def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = "." * node.level + module
            yield module


def _domain_import_violations(domain: str, forbidden: tuple[str, ...]):
    violations = []
    for path in sorted((ROOT / domain).rglob("*.py")):
        for imported in _imports(path):
            normalized = imported.lstrip(".")
            if any(
                normalized == target
                or normalized.startswith(f"{target}.")
                or imported.startswith(f"..{target.rsplit('.', 1)[-1]}")
                for target in forbidden
            ):
                violations.append(f"{path.relative_to(ROOT)} -> {imported}")
    return violations


def test_common_does_not_import_qualification_domains():
    assert _domain_import_violations(
        "common", ("licensetown.pt", "licensetown.takken")
    ) == []


def test_pt_and_takken_do_not_import_each_other():
    assert _domain_import_violations("pt", ("licensetown.takken",)) == []
    assert _domain_import_violations("takken", ("licensetown.pt",)) == []


def test_takken_scaffold_contains_no_python_implementation_outside_metadata():
    python_files = {
        path.relative_to(ROOT / "takken").as_posix()
        for path in (ROOT / "takken").rglob("*.py")
    }
    assert python_files == {"__init__.py", "config.py"}
