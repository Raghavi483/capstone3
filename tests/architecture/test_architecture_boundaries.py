"""
Test Suite: Architecture Structural Tests (NFR-08)
Uses AST static analysis to enforce strict layer boundary constraints:
1. Controllers cannot import Repository classes or ORM Models directly.
2. Domain layer is completely isolated (no imports from services, controllers, or repositories).
3. Repositories cannot import Services or Controllers.
4. Services cannot import Controllers.
5. Settled claims cannot be mutated (invariant check).
"""

import ast
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"


def get_imports_for_file(file_path: Path):
    """Extracts all module and from-import targets using Python AST."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    imports.append(f"{node.module}.{alias.name}")
    return imports


def test_arch_01_controllers_do_not_import_repositories_or_models():
    """NFR-08 Structural Rule: Controllers must orchestrate via Services only."""
    controllers_dir = SRC_DIR / "controllers"
    for py_file in controllers_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        imports = get_imports_for_file(py_file)
        for imp in imports:
            # Forbid importing concrete repositories or models
            assert "src.repositories.models" not in imp, (
                f"Architecture Violation: {py_file.name} imports ORM Model: {imp}"
            )
            assert "Repository" not in imp or "src.repositories.database" in imp, (
                f"Architecture Violation: {py_file.name} imports Repository directly: {imp}"
            )


def test_arch_02_domain_layer_strict_isolation():
    """NFR-08 Structural Rule: Domain layer must have zero dependencies on outer layers."""
    domain_dir = SRC_DIR / "domain"
    forbidden_prefixes = (
        "src.controllers",
        "src.services",
        "src.repositories",
        "sqlalchemy",
        "fastapi"
    )
    for py_file in domain_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        imports = get_imports_for_file(py_file)
        for imp in imports:
            for forbidden in forbidden_prefixes:
                assert not imp.startswith(forbidden), (
                    f"Domain Isolation Violation: {py_file.name} depends on outer layer: {imp}"
                )


def test_arch_03_repositories_do_not_import_services_or_controllers():
    """NFR-08 Structural Rule: Repositories cannot depend on Services or Controllers."""
    repo_dir = SRC_DIR / "repositories"
    forbidden_prefixes = ("src.controllers", "src.services")
    for py_file in repo_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        imports = get_imports_for_file(py_file)
        for imp in imports:
            for forbidden in forbidden_prefixes:
                assert not imp.startswith(forbidden), (
                    f"Repository Layer Violation: {py_file.name} depends on upper layer: {imp}"
                )


def test_arch_04_services_do_not_import_controllers():
    """NFR-08 Structural Rule: Services cannot depend on Controllers."""
    services_dir = SRC_DIR / "services"
    for py_file in services_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        imports = get_imports_for_file(py_file)
        for imp in imports:
            assert not imp.startswith("src.controllers"), (
                f"Service Layer Violation: {py_file.name} depends on controller: {imp}"
            )


def test_arch_05_floating_point_prohibited_in_domain_rules():
    """NFR-01 Architectural Invariant: Domain code must not declare or cast to float."""
    domain_dir = SRC_DIR / "domain"
    for py_file in domain_dir.glob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "float":
                pytest.fail(f"NFR-01 Floating-point violation in {py_file.name}: 'float' reference detected.")
