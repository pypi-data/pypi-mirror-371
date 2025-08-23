"""Utilities for interacting with Git."""

from __future__ import annotations

from pathlib import Path
import shlex
import subprocess


class Git:
    """Simple wrapper around common Git commands."""

    def __init__(self, path: Path = Path.cwd()) -> None:
        self.path = path

    def is_git_repo(self) -> bool:
        try:
            subprocess.run(
                shlex.split("git rev-parse --is-inside-work-tree"),
                check=True,
                capture_output=True,
                text=True,
                cwd=self.path,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def create_tag(self, tag_name: str) -> None:
        subprocess.run(
            shlex.split(f"git tag {tag_name}"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.path,
        )

    def push_tag(self, tag_name: str) -> None:
        subprocess.run(
            shlex.split(f"git push origin {tag_name}"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.path,
        )

    def push(self) -> None:
        subprocess.run(
            shlex.split("git push"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.path,
        )

    def add(self, file: str) -> None:
        subprocess.run(
            shlex.split(f"git add {file}"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.path,
        )

    def commit(self, message: str) -> None:
        subprocess.run(
            shlex.split(f"git commit -m '{message}'"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.path,
        )

    def list_tags(self) -> list[str]:
        """Return list of Git tags sorted alphanumerically ascending."""

        result = subprocess.run(
            shlex.split("git tag --list --sort=version:refname"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.path,
        )
        tags = result.stdout.strip().splitlines()
        return tags


__all__ = ["Git"]
