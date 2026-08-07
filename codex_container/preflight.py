"""Fresh-start checks with user-actionable failure messages."""

import pathlib

import codex_container.config
import codex_container.ollama
import codex_container.podman
import codex_container.workspace


#============================================
def run_preflight(
	config: codex_container.config.StartConfig,
	runner: codex_container.podman.Runner = codex_container.podman.run_podman,
) -> codex_container.ollama.ModelMetadata:
	"""Check host services and input before creating a new agent.

	Args:
		config: Normalized fresh-agent configuration.
		runner: Injectable Podman runner.

	Returns:
		Selected model metadata discovered from Ollama.
	"""
	codex_container.workspace.validate_git_worktree(config.project_dir)
	codex_container.ollama.validate_model(config.ollama_url, config.model)
	metadata = codex_container.ollama.model_metadata(config.ollama_url, config.model)
	runner(["info", "--format", "{{.Host.OS}}"], None)
	runner(["image", "exists", config.image], None)
	container_ollama_url = codex_container.ollama.container_url(config.ollama_url) + "/api/tags"
	runner([
		"run", "--rm", "--network", "pasta", config.image, "sh", "-c",
		f"wget -q -O /dev/null {container_ollama_url}",
	], None)
	return metadata


#============================================
def dist_clean_command(project_dir: pathlib.Path) -> list[str]:
	"""Return the repository-owned cross-OS cleanup command.

	Args:
		project_dir: Project checkout to clean.

	Returns:
		Command to run from the project checkout.
	"""
	command = [str(project_dir / "devel" / "dist_clean.sh")]
	return command
