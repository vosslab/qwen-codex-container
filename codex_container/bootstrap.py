"""Bootstrap a new, disposable Codex session inside a fresh container."""

import shlex

import codex_container.config
import codex_container.ollama
import codex_container.podman
import codex_container.rendering


#============================================
def bootstrap_fresh_agent(
	container_id: str,
	config: codex_container.config.StartConfig,
	metadata: codex_container.ollama.ModelMetadata,
	runner: codex_container.podman.Runner = codex_container.podman.run_podman,
) -> None:
	"""Write container-local settings and launch a new tmux Codex session.

	Args:
		container_id: Newly started container.
		config: Normalized fresh-agent configuration.
		metadata: Selected model facts reported by Ollama.
		runner: Injectable Podman runner.
	"""
	environment = codex_container.rendering.render_environment(config)
	codex_config = codex_container.rendering.render_codex_config()
	model_catalog = codex_container.rendering.render_model_catalog(config, metadata)
	runner(["exec", "-i", container_id, "sh", "-c", "mkdir -p /root/.codexdev"], None)
	runner(
		["exec", "-i", container_id, "sh", "-c", "cat > /root/.codexdev/environment.sh"],
		environment,
	)
	runner(
		["exec", "-i", container_id, "sh", "-c", "cat > /root/.codexdev/config.toml"],
		codex_config,
	)
	runner(
		["exec", "-i", container_id, "sh", "-c", "cat > /root/.codexdev/model.json"],
		model_catalog,
	)
	# Codex's Ollama provider probes localhost, so bridge its loopback port to the host service.
	runner([
		"exec", "-d", container_id, "socat", "TCP-LISTEN:11434,fork,reuseaddr",
		"TCP:host.containers.internal:11434",
	], None)
	runner([
		"exec", container_id, "wget", "-q", "-O", "/dev/null",
		"http://localhost:11434/api/tags",
	], None)
	command = (
		". /root/.codexdev/environment.sh && cd /workspace && "
		"codex --oss --local-provider ollama --model \"$CODEX_MODEL\" "
		"--dangerously-bypass-approvals-and-sandbox"
	)
	# Codex accepts one ordinary initial prompt as its final positional argument.
	if config.prompt:
		command += " " + shlex.quote(config.prompt)
	runner([
		"exec", "-d", container_id, "tmux", "new-session", "-d", "-s", "codex", command,
	], None)
	# Goals have no CLI flag, so the live TUI must receive its built-in slash command.
	if config.goal:
		# Allow the TUI to finish its initial render before literal input arrives.
		runner(["exec", container_id, "sleep", "4"], None)
		goal_command = "/goal " + config.goal
		codex_container.podman.send_session_message(container_id, goal_command, runner)
