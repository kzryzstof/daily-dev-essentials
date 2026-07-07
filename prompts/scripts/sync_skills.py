#!/usr/bin/env python3
"""Copy this repository's skills and references into local Claude/Copilot folders.

The script intentionally only installs into ~/.claude and/or ~/.copilot when those
folders already exist. It creates the nested skills directory as needed.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable

IGNORED_NAMES = {".DS_Store", "__pycache__"}
TARGET_FOLDERS = (".claude", ".copilot", ".gemini", ".codex", ".junie")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy acs-workflow skills and references to existing ~/.claude "
            "and ~/.copilot folders."
        )
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="Home directory that contains .claude/.copilot (defaults to current user home).",
    )
    parser.add_argument(
        "--target",
        choices=TARGET_FOLDERS,
        action="append",
        help="Limit installation to one target folder. Can be passed more than once.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be copied without changing any files.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def discover_skill_sources(skills_root: Path) -> list[tuple[Path, str, set[str]]]:
    """Return (source path, destination name, ignored child names) for all skills."""
    if not (skills_root / "SKILL.md").is_file():
        raise FileNotFoundError(f"Missing root skill file: {skills_root / 'SKILL.md'}")

    root_skill_children = {
        child.name
        for child in skills_root.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    }
    skill_sources: list[tuple[Path, str, set[str]]] = [
        (skills_root, skills_root.name, root_skill_children)
    ]

    for child in sorted(skills_root.iterdir()):
        if child.is_dir() and (child / "SKILL.md").is_file():
            skill_sources.append((child, child.name, set()))

    return skill_sources


def should_ignore(_: str, names: Iterable[str], extra_ignored_names: set[str]) -> set[str]:
    return {name for name in names if name in IGNORED_NAMES or name in extra_ignored_names}


def copy_directory(source: Path, destination: Path, extra_ignored_names: set[str], dry_run: bool) -> None:
    if dry_run:
        print(f"  - {source} -> {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        destination,
        dirs_exist_ok=True,
        ignore=lambda directory, names: should_ignore(directory, names, extra_ignored_names),
    )


def install_to_target(
    target_root: Path,
    skill_sources: list[tuple[Path, str, set[str]]],
    references_root: Path,
    dry_run: bool,
) -> None:
    skills_destination = target_root / "skills"
    print(f"Installing to {target_root}:")

    for source, destination_name, ignored_children in skill_sources:
        copy_directory(source, skills_destination / destination_name, ignored_children, dry_run)

    copy_directory(references_root, skills_destination / "references", set(), dry_run)


def main() -> int:
    args = parse_args()
    root = repo_root()
    skills_root = root / "skills"
    references_root = root / "references"

    if not references_root.is_dir():
        raise FileNotFoundError(f"Missing references directory: {references_root}")

    skill_sources = discover_skill_sources(skills_root)
    requested_targets = tuple(args.target) if args.target else TARGET_FOLDERS
    existing_targets = [args.home / target for target in requested_targets if (args.home / target).is_dir()]

    if not existing_targets:
        requested = ", ".join(str(args.home / target) for target in requested_targets)
        print(f"No existing target folders found ({requested}). Nothing copied.")
        return 0

    if args.dry_run:
        print("Dry run: no files will be changed.")

    for target_root in existing_targets:
        install_to_target(target_root, skill_sources, references_root, args.dry_run)

    skipped_targets = [args.home / target for target in requested_targets if not (args.home / target).is_dir()]
    for target_root in skipped_targets:
        print(f"Skipped missing target folder: {target_root}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

