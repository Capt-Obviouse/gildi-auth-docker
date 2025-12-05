#!/usr/bin/env python3
"""
End-to-end update helper for Alliance Auth Docker deployment.

Flow:
 1. Run `python manage.py packagemonitorcli install` inside allianceauth_cli
 2. Parse `pkg==version` specs from its output
 3. Update ONLY matching packages in conf/requirements.txt
 4. docker compose build
 5. docker compose --env-file=.env up -d
 6. Run migrations and collectstatic inside the new image

Run this from the repo root:
  python scripts/update_from_packagemonitor.py
"""

import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQ_PATH = PROJECT_ROOT / "conf" / "requirements.txt"
SERVICE_CLI = "aa_cli"


def run(cmd, capture=False, allow_failure=False):
    """
    Run a shell command.
    - If capture=True, return stdout as text.
    - If allow_failure=True, do not raise on non-zero, just return (stdout, stderr, returncode).
    """
    print("+", " ".join(cmd))
    if capture or allow_failure:
        result = subprocess.run(cmd, text=True, capture_output=True)
        if not allow_failure and result.returncode != 0:
            print("Command failed with stderr:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            raise subprocess.CalledProcessError(
                result.returncode, cmd, output=result.stdout, stderr=result.stderr
            )
        if allow_failure:
            return result.stdout, result.stderr, result.returncode
        return result.stdout
    else:
        subprocess.run(cmd, check=True)


def parse_specs(text: str):
    """
    Extract specs like 'name==1.2.3' from arbitrary text.
    Supports ==, >=, <=, ~=, !=, ===.
    """
    pattern = re.compile(r"([A-Za-z0-9_.\-]+)\s*(==|>=|<=|~=|!=|===)\s*([^\s,]+)")
    specs = {}
    for name, op, ver in pattern.findall(text):
        specs[name.lower()] = f"{name}{op}{ver}"
    return specs


def load_existing_packages(req_path: Path):
    """
    Reads requirements.txt and returns:
      - {lower_name -> line_index}
      - list of original lines
    Ignores comments / blank lines.
    """
    packages = {}
    lines = req_path.read_text().splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        m = re.match(r"([A-Za-z0-9_.\-]+)", stripped)
        if m:
            pkg = m.group(1).lower()
            packages[pkg] = i

    return packages, lines


def update_requirements(req_path: Path, updates: dict):
    """
    Only updates packages already present in requirements.txt.
    Returns (updated_count, ignored_count).
    """
    pkg_map, lines = load_existing_packages(req_path)
    updated = 0
    ignored = 0

    for pkg_lower, new_spec in updates.items():
        if pkg_lower in pkg_map:
            index = pkg_map[pkg_lower]
            print(f"  - updating {lines[index]!r} -> {new_spec!r}")
            lines[index] = new_spec
            updated += 1
        else:
            ignored += 1

    req_path.write_text("\n".join(lines) + "\n")
    return updated, ignored


def main():
    if not REQ_PATH.exists():
        print(f"ERROR: requirements file not found at {REQ_PATH}", file=sys.stderr)
        sys.exit(1)

    print("Step 1: Running packagemonitor CLI inside Docker...")
    stdout, stderr, rc = run(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            SERVICE_CLI,
            "packagemonitorcli",
            "install",
        ],
        allow_failure=True,
    )

    if rc != 0:
        print("\nERROR: packagemonitor CLI returned non-zero exit code:", rc, file=sys.stderr)
        print("STDERR:", file=sys.stderr)
        print(stderr, file=sys.stderr)
        print("STDOUT (last lines):", file=sys.stderr)
        for line in stdout.strip().splitlines()[-10:]:
            print(line, file=sys.stderr)
        sys.exit(rc)

    print("\n--- packagemonitor output (truncated) ---")
    lines = stdout.strip().splitlines()
    for line in lines[-10:]:
        print(line)
    print("----------------------------------------\n")

    print("Step 2: Parsing package specs from output...")
    specs = parse_specs(stdout)
    if not specs:
        print("No 'pkg==version' specs found in output. Nothing to do.", file=sys.stderr)
        sys.exit(1)

    print(f"  Found {len(specs)} package spec(s) from packagemonitor CLI.")
    print("Step 3: Updating existing packages in conf/requirements.txt...")
    updated, ignored = update_requirements(REQ_PATH, specs)
    print(f"  Updated {updated} package(s). Ignored {ignored} not present in requirements.txt.\n")

    if updated == 0:
        print("No packages were updated. Skipping rebuild / deploy.")
        sys.exit(0)

    print("Step 4: Rebuilding Docker images...")
    run(["docker", "compose", "build"])

    print("Step 5: Bringing stack up with new images...")
    run(["docker", "compose", "up", "-d"])

    print("Step 6: Running migrations...")
    run(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            SERVICE_CLI,
            "migrate",
        ]
    )

    print("Step 7: Running collectstatic...")
    run(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            SERVICE_CLI,
            "collectstatic",
            "--noinput",
        ]
    )

    print("\nAll done. Packages updated, image rebuilt, services restarted, migrations & collectstatic run.")


if __name__ == "__main__":
    main()

