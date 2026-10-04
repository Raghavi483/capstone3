"""
MediCard — Meaningful Lines of Code (LOC) Audit Tool (Section 19).
Counts non-blank, non-comment lines of code across:
- Backend application code (domain, services, repositories, controllers, utils, main, seed)
- Frontend client code (HTML, CSS, JS)
- Test suites (unit, architecture, security, E2E)
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def count_file_loc(filepath: Path) -> int:
    """Count non-empty, non-comment lines in a source file."""
    ext = filepath.suffix.lower()
    loc = 0
    in_block_comment = False

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue

                if ext == ".py":
                    if s.startswith('"""') or s.startswith("'''"):
                        if s.count('"""') == 2 or s.count("'''") == 2:
                            continue
                        in_block_comment = not in_block_comment
                        continue
                    if in_block_comment:
                        if '"""' in s or "'''" in s:
                            in_block_comment = False
                        continue
                    if s.startswith("#"):
                        continue
                    loc += 1

                elif ext in [".js", ".css"]:
                    if s.startswith("/*") and s.endswith("*/"):
                        continue
                    if s.startswith("/*"):
                        in_block_comment = True
                        continue
                    if in_block_comment:
                        if "*/" in s:
                            in_block_comment = False
                        continue
                    if s.startswith("//"):
                        continue
                    loc += 1

                elif ext == ".html":
                    if s.startswith("<!--") and s.endswith("-->"):
                        continue
                    if s.startswith("<!--"):
                        in_block_comment = True
                        continue
                    if in_block_comment:
                        if "-->" in s:
                            in_block_comment = False
                        continue
                    loc += 1

                else:
                    loc += 1
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return loc


def scan_directory(dir_path: Path, extensions: list[str]) -> tuple[int, dict[str, int]]:
    """Scan directory recursively for files with given extensions."""
    total = 0
    breakdown = {}
    if not dir_path.exists():
        return total, breakdown

    for path in sorted(dir_path.rglob("*")):
        if path.is_file() and path.suffix.lower() in extensions:
            if "__pycache__" in str(path) or ".pytest_cache" in str(path):
                continue
            loc = count_file_loc(path)
            rel = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
            breakdown[rel] = loc
            total += loc
    return total, breakdown


def generate_loc_report() -> dict:
    # 1. Backend application
    backend_dirs = [
        PROJECT_ROOT / "src",
    ]
    backend_loc = 0
    backend_files = {}
    for d in backend_dirs:
        loc, files = scan_directory(d, [".py"])
        backend_loc += loc
        backend_files.update(files)

    # 2. Frontend application
    frontend_dir = PROJECT_ROOT / "frontend"
    frontend_loc, frontend_files = scan_directory(frontend_dir, [".html", ".css", ".js"])

    # 3. Test suites
    tests_dir = PROJECT_ROOT / "tests"
    tests_loc, tests_files = scan_directory(tests_dir, [".py"])

    # 4. Support and automation scripts
    scripts_dir = PROJECT_ROOT / "scripts"
    scripts_loc, scripts_files = scan_directory(scripts_dir, [".py"])

    total_meaningful_loc = backend_loc + frontend_loc + tests_loc + scripts_loc

    print("=" * 75)
    print(" MediCard (BC-AINE-017) — Meaningful Codebase LOC Audit (Section 19)")
    print("=" * 75)
    print(f"{'Category':<35} | {'Source Files':<12} | {'Meaningful LOC':<15}")
    print("-" * 75)
    print(f"{'1. Backend Application (src/)':<35} | {len(backend_files):<12} | {backend_loc:<15}")
    print(f"{'2. Frontend Application (frontend/)':<35} | {len(frontend_files):<12} | {frontend_loc:<15}")
    print(f"{'3. Test Suites (tests/)':<35} | {len(tests_files):<12} | {tests_loc:<15}")
    print(f"{'4. Automation Scripts (scripts/)':<35} | {len(scripts_files):<12} | {scripts_loc:<15}")
    print("=" * 75)
    print(f"{'TOTAL MEANINGFUL LOC':<35} | {len(backend_files) + len(frontend_files) + len(tests_files) + len(scripts_files):<12} | {total_meaningful_loc:<15}")
    print("=" * 75)
    target = 3000
    status = "MET & EXCEEDED (>= 3,000)" if total_meaningful_loc >= target else "UNDER TARGET"
    print(f"Capstone Target Status: {status} (Target: {target} LOC)\n")

    return {
        "backend_loc": backend_loc,
        "frontend_loc": frontend_loc,
        "tests_loc": tests_loc,
        "scripts_loc": scripts_loc,
        "total_loc": total_meaningful_loc,
        "backend_files": backend_files,
        "frontend_files": frontend_files,
        "tests_files": tests_files,
        "scripts_files": scripts_files
    }


if __name__ == "__main__":
    generate_loc_report()
