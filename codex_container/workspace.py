"""Project path, git-worktree, and runtime naming helpers."""

import pathlib
import re
import secrets
import subprocess
import zlib


#============================================
def normalize_project_path(project_value: str) -> pathlib.Path:
	"""Expand and resolve a project path.

	Args:
		project_value: User-entered project path.

	Returns:
		Resolved project directory.
	"""
	if not project_value.strip():
		raise ValueError("a project folder is required")
	project_dir = pathlib.Path(project_value).expanduser().resolve()
	if not project_dir.is_dir():
		raise ValueError(f"project folder does not exist: {project_dir}")
	return project_dir


#============================================
def validate_git_worktree(project_dir: pathlib.Path) -> None:
	"""Require an existing Git work tree for durable agent work.

	Args:
		project_dir: Normalized project directory.

	Raises:
		ValueError: If the project is not a Git work tree.
	"""
	result = subprocess.run(
		["git", "-C", str(project_dir), "rev-parse", "--is-inside-work-tree"],
		check=False,
		capture_output=True,
		text=True,
	)
	if result.returncode != 0 or result.stdout.strip() != "true":
		raise ValueError(f"project is not a Git work tree: {project_dir}")


#============================================
def project_slug(project_dir: pathlib.Path) -> str:
	"""Create a Podman-safe slug from a project directory.

	Args:
		project_dir: Normalized project directory.

	Returns:
		A nonempty lowercase slug.
	"""
	slug = re.sub(r"[^a-z0-9]+", "-", project_dir.name.lower()).strip("-")
	if not slug:
		slug = "project"
	return slug


#============================================
def random_crc_suffix() -> str:
	"""Return an eight-character CRC32 of fresh random bytes.

	Returns:
		Lowercase hexadecimal CRC32 text.
	"""
	random_bytes = secrets.token_bytes(16)
	crc_value = zlib.crc32(random_bytes)
	suffix = f"{crc_value:08x}"
	return suffix


#============================================
def container_name(project_dir: pathlib.Path, crc_suffix: str) -> str:
	"""Return a unique managed container name for a project.

	Args:
		project_dir: Normalized project directory.
		crc_suffix: Random hexadecimal suffix for this fresh runtime.

	Returns:
		The project slug plus the supplied random CRC suffix.
	"""
	name = f"codexdev-{project_slug(project_dir)}-{crc_suffix}"
	return name
