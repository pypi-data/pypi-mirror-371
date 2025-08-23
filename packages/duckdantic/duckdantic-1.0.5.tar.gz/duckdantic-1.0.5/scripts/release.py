#!/usr/bin/env python3
"""Release script for Duckdantic.

This script helps with the release process by:
1. Checking that all tests pass
2. Building the package
3. Creating a git tag
4. Optionally pushing to trigger the release workflow
"""

import argparse
import subprocess
import sys


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    result = subprocess.run(
        cmd, check=False, shell=True, capture_output=True, text=True
    )

    if check and result.returncode != 0:
        sys.exit(1)

    return result


def check_git_status() -> None:
    """Ensure we're on main branch and working directory is clean."""
    # Check current branch
    result = run_command("git rev-parse --abbrev-ref HEAD")
    branch = result.stdout.strip()
    if branch != "main":
        sys.exit(1)

    # Check for uncommitted changes
    result = run_command("git status --porcelain")
    if result.stdout.strip():
        sys.exit(1)


def run_tests() -> None:
    """Run the test suite."""
    run_command("uv run pytest")


def build_package() -> None:
    """Build the package."""
    run_command("uv build")


def get_version() -> str:
    """Get the current version from git tags."""
    result = run_command("git describe --tags --abbrev=0", check=False)
    if result.returncode == 0:
        return result.stdout.strip()
    return "v0.0.0"


def create_tag(version: str) -> None:
    """Create a new git tag."""
    run_command(f"git tag -a {version} -m 'Release {version}'")


def push_tag(version: str, dry_run: bool = False) -> None:
    """Push the tag to trigger release workflow."""
    if dry_run:
        return

    run_command(f"git push origin {version}")


def main() -> None:
    """Main release process."""

    parser = argparse.ArgumentParser(description="Release Duckdantic")
    parser.add_argument("version", help="Version to release (e.g., v1.0.0)")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually push")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument(
        "--skip-build", action="store_true", help="Skip building package"
    )

    args = parser.parse_args()

    version = args.version
    if not version.startswith("v"):
        version = f"v{version}"

    # Pre-flight checks
    check_git_status()

    if not args.skip_tests:
        run_tests()

    if not args.skip_build:
        build_package()

    # Create and push tag
    create_tag(version)
    push_tag(version, dry_run=args.dry_run)

    if args.dry_run:
        print(f"✅ Dry run complete. Tag {version} created but not pushed.")
    else:
        print(f"🎉 Successfully released {version}!")


if __name__ == "__main__":
    main()
