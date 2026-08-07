"""Normalized startup configuration."""

import dataclasses
import pathlib

import codex_container.workspace


DEFAULT_MODEL = "qwen3.5:9b"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_IMAGE = "codexdev:latest"


@dataclasses.dataclass(frozen=True)
class StartConfig:
	"""Values required to create one fresh agent."""

	project_dir: pathlib.Path
	model: str
	ollama_url: str
	dist_clean: bool
	image: str
	goal: str | None = None
	prompt: str | None = None


#============================================
def make_start_config(
	project_value: str,
	model_value: str,
	ollama_url: str,
	dist_clean: bool,
	image: str,
	goal: str | None = None,
	prompt: str | None = None,
) -> StartConfig:
	"""Normalize user-supplied startup values.

	Args:
		project_value: Project directory selected by the user.
		model_value: Ollama model selected by the user.
		ollama_url: Ollama endpoint visible from the container.
		dist_clean: Whether fresh startup cleans Linux build artifacts.
		image: Podman image that provides Codex and tmux.

	Returns:
		A normalized immutable configuration.
	"""
	model = model_value.strip()
	image_name = image.strip()
	if not model:
		raise ValueError("model name is required")
	if not image_name:
		raise ValueError("container image is required")
	if goal is not None and not goal.strip():
		raise ValueError("goal text is required")
	if prompt is not None and not prompt.strip():
		raise ValueError("prompt text is required")
	project_dir = codex_container.workspace.normalize_project_path(project_value)
	config = StartConfig(
		project_dir=project_dir,
		model=model,
		ollama_url=ollama_url.rstrip("/"),
		dist_clean=dist_clean,
		image=image_name,
		goal=goal.strip() if goal is not None else None,
		prompt=prompt.strip() if prompt is not None else None,
	)
	return config
