"""Podman command construction and managed-container operations."""

import collections.abc
import dataclasses
import pathlib
import subprocess

import codex_container.config
import codex_container.workspace


Runner = collections.abc.Callable[[list[str], str | None], subprocess.CompletedProcess[str]]


@dataclasses.dataclass(frozen=True)
class ManagedContainer:
	"""A managed container discovered through its labels."""

	container_id: str
	name: str
	status: str
	project_dir: pathlib.Path


#============================================
def run_podman(argv: list[str], input_text: str | None = None) -> subprocess.CompletedProcess[str]:
	"""Run one Podman command and preserve its diagnostic output.

	Args:
		argv: Arguments after the Podman executable.
		input_text: Optional standard input for the command.

	Returns:
		Completed command result.

	Raises:
		RuntimeError: If Podman reports failure.
	"""
	command = ["podman", *argv]
	if argv[:2] == ["exec", "-it"]:
		result = subprocess.run(command, check=False, text=True)
	else:
		result = subprocess.run(
			command,
			check=False,
			capture_output=True,
			input=input_text,
			text=True,
		)
	if result.returncode != 0:
		message = result.stderr.strip() or result.stdout.strip()
		raise RuntimeError(f"podman {' '.join(argv)} failed: {message}")
	return result


#============================================
def create_argv(config: codex_container.config.StartConfig) -> list[str]:
	"""Build the fresh-container command without executing it.

	Args:
		config: Normalized fresh-agent configuration.

	Returns:
		Podman arguments that create the disposable agent container.
	"""
	project_path = str(config.project_dir)
	crc_suffix = codex_container.workspace.random_crc_suffix()
	name = codex_container.workspace.container_name(config.project_dir, crc_suffix)
	argv = [
		"create",
		"--name", name,
		"--label", f"codexdev.project={project_path}",
		"--label", f"codexdev.slug={codex_container.workspace.project_slug(config.project_dir)}",
		"--label", "codexdev.role=agent",
		"--volume", f"{project_path}:/workspace:rw",
		"--workdir", "/workspace",
		config.image,
		"sleep", "infinity",
	]
	return argv


#============================================
def parse_containers(output: str) -> list[ManagedContainer]:
	"""Parse stable tab-separated output from `podman ps`.

	Args:
		output: Tab-separated id, status, name, and project values.

	Returns:
		Managed containers represented by the output.
	"""
	containers = []
	for line in output.splitlines():
		parts = line.split("\t")
		if len(parts) != 4:
			continue
		container = ManagedContainer(
			container_id=parts[0],
			status=parts[1],
			name=parts[2],
			project_dir=pathlib.Path(parts[3]),
		)
		containers.append(container)
	return containers


#============================================
def find_project_container(
	project_dir: pathlib.Path,
	runner: Runner = run_podman,
) -> ManagedContainer | None:
	"""Find a managed container for exactly one project.

	Args:
		project_dir: Project whose runtime should be found.
		runner: Injectable Podman runner.

	Returns:
		The matching container, or None when no runtime exists.

	Raises:
		RuntimeError: If duplicate managed runtimes exist.
	"""
	format_value = "{{.ID}}\t{{.Status}}\t{{.Names}}\t{{.Label \"codexdev.project\"}}"
	result = runner([
		"ps", "-a", "--filter", "label=codexdev.role=agent", "--filter",
		f"label=codexdev.project={project_dir}", "--format", format_value,
	], None)
	containers = parse_containers(result.stdout)
	if len(containers) > 1:
		raise RuntimeError(f"multiple managed agents exist for {project_dir}; run stop.py")
	if not containers:
		return None
	container = containers[0]
	return container


#============================================
def find_only_container(runner: Runner = run_podman) -> ManagedContainer | None:
	"""Find the sole managed container when project context is omitted.

	Args:
		runner: Injectable Podman runner.

	Returns:
		The one managed container, or None if none exist.

	Raises:
		RuntimeError: If project selection is ambiguous.
	"""
	format_value = "{{.ID}}\t{{.Status}}\t{{.Names}}\t{{.Label \"codexdev.project\"}}"
	result = runner([
		"ps", "-a", "--filter", "label=codexdev.role=agent", "--format", format_value,
	], None)
	containers = parse_containers(result.stdout)
	if len(containers) > 1:
		raise RuntimeError("multiple managed agents exist; select one with --project")
	if not containers:
		return None
	container = containers[0]
	return container


#============================================
def create_container(
	config: codex_container.config.StartConfig,
	runner: Runner = run_podman,
) -> str:
	"""Create a fresh managed container.

	Args:
		config: Fresh-agent configuration.
		runner: Injectable Podman runner.

	Returns:
		The new container ID.
	"""
	result = runner(create_argv(config), None)
	container_id = result.stdout.strip()
	return container_id


#============================================
def start_container(container_id: str, runner: Runner = run_podman) -> None:
	"""Start a previously created fresh container.

	Args:
		container_id: Container to start.
		runner: Injectable Podman runner.
	"""
	runner(["start", container_id], None)


#============================================
def attach_container(container_id: str, runner: Runner = run_podman) -> None:
	"""Attach the terminal to the existing Codex tmux session.

	Args:
		container_id: Running agent container.
		runner: Injectable Podman runner.
	"""
	runner(["exec", "-it", container_id, "tmux", "attach-session", "-t", "codex"], None)


#============================================
def verify_session(container_id: str, runner: Runner = run_podman) -> None:
	"""Require the fresh agent's tmux session to still be running.

	Args:
		container_id: Running agent container.
		runner: Injectable Podman runner.
	"""
	runner(["exec", container_id, "tmux", "has-session", "-t", "codex"], None)


#============================================
def send_session_message(
	container_id: str,
	message: str,
	runner: Runner = run_podman,
) -> None:
	"""Send one literal user message to the running Codex TUI.

	Args:
		container_id: Running agent container.
		message: Text to submit at the Codex prompt.
		runner: Injectable Podman runner.
	"""
	if not message.strip():
		raise ValueError("prompt text is required")
	runner([
		"exec", container_id, "tmux", "send-keys", "-t", "codex", "-l", message,
	], None)
	runner(["exec", container_id, "tmux", "send-keys", "-t", "codex", "Enter"], None)


#============================================
def stop_container(container_id: str, runner: Runner = run_podman) -> None:
	"""Request a graceful container stop.

	Args:
		container_id: Running or stale container.
		runner: Injectable Podman runner.
	"""
	runner(["stop", container_id], None)


#============================================
def remove_container(container_id: str, runner: Runner = run_podman) -> None:
	"""Remove stopped disposable runtime state.

	Args:
		container_id: Stopped container.
		runner: Injectable Podman runner.
	"""
	runner(["rm", container_id], None)
