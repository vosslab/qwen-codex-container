"""High-level fresh-start, reconnect, and stop decisions."""

import subprocess

import codex_container.bootstrap
import codex_container.config
import codex_container.podman
import codex_container.preflight


#============================================
def start_fresh(
	config: codex_container.config.StartConfig,
	detach: bool,
	dry_run: bool,
	runner: codex_container.podman.Runner = codex_container.podman.run_podman,
) -> str | None:
	"""Replace stale state and create one completely fresh agent.

	Args:
		config: Normalized startup configuration.
		detach: Whether to leave the user unattached after bootstrap.
		dry_run: Whether to print the create command without changing runtime state.
		runner: Injectable Podman runner.

	Returns:
		New container ID, or None for a dry run.
	"""
	if dry_run:
		print("podman " + " ".join(codex_container.podman.create_argv(config)))
		return None
	metadata = codex_container.preflight.run_preflight(config, runner)
	stale = codex_container.podman.find_project_container(config.project_dir, runner)
	if stale:
		codex_container.podman.stop_container(stale.container_id, runner)
		codex_container.podman.remove_container(stale.container_id, runner)
	if config.dist_clean:
		result = subprocess.run(
			codex_container.preflight.dist_clean_command(config.project_dir),
			cwd=config.project_dir,
			check=False,
		)
		if result.returncode != 0:
			raise RuntimeError("devel/dist_clean.sh failed")
	container_id = codex_container.podman.create_container(config, runner)
	codex_container.podman.start_container(container_id, runner)
	codex_container.bootstrap.bootstrap_fresh_agent(container_id, config, metadata, runner)
	if not detach:
		codex_container.podman.attach_container(container_id, runner)
	return container_id


#============================================
def reconnect(
	container: codex_container.podman.ManagedContainer | None,
	check_only: bool,
	prompt: str | None,
	runner: codex_container.podman.Runner = codex_container.podman.run_podman,
) -> None:
	"""Attach to one already-running agent without creating anything.

	Args:
		container: Managed runtime selected by project or unambiguous discovery.
		check_only: Whether to validate rather than attach.
		prompt: Optional ordinary message to send without attaching.
		runner: Injectable Podman runner.

	Raises:
		RuntimeError: If no live agent is available.
	"""
	if container is None:
		raise RuntimeError("no reconnectable agent exists; run start.py")
	if not container.status.lower().startswith("up"):
		raise RuntimeError("managed agent is not running; run start.py for a fresh agent")
	codex_container.podman.verify_session(container.container_id, runner)
	if prompt is not None:
		codex_container.podman.send_session_message(container.container_id, prompt, runner)
	elif not check_only:
		codex_container.podman.attach_container(container.container_id, runner)


#============================================
def stop(
	container: codex_container.podman.ManagedContainer | None,
	runner: codex_container.podman.Runner = codex_container.podman.run_podman,
) -> None:
	"""Gracefully stop and remove disposable runtime state.

	Args:
		container: Managed runtime selected by project or unambiguous discovery.
		runner: Injectable Podman runner.

	Raises:
		RuntimeError: If no managed container exists.
	"""
	if container is None:
		raise RuntimeError("no managed agent exists to stop")
	if container.status.lower().startswith("up"):
		codex_container.podman.stop_container(container.container_id, runner)
	codex_container.podman.remove_container(container.container_id, runner)
