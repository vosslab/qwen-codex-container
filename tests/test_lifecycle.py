import pathlib
import subprocess
import unittest.mock

import codex_container.config
import codex_container.lifecycle
import codex_container.podman


#============================================
def make_config() -> codex_container.config.StartConfig:
	config = codex_container.config.make_start_config(
		str(pathlib.Path.cwd()), "model", "http://example.test:11434", False, "image",
	)
	return config


#============================================
def test_start_replaces_stale_agent() -> None:
	commands = []
	project_dir = pathlib.Path.cwd()
	stale = codex_container.podman.ManagedContainer("old", "codexdev-old", "Up", project_dir)

	def runner(argv: list[str], input_text: str | None) -> subprocess.CompletedProcess[str]:
		commands.append(argv)
		output = "new" if argv[0] == "create" else ""
		return subprocess.CompletedProcess(argv, 0, output, "")

	with unittest.mock.patch("codex_container.preflight.run_preflight"):
		with unittest.mock.patch("codex_container.podman.find_project_container", return_value=stale):
			with unittest.mock.patch("codex_container.bootstrap.bootstrap_fresh_agent"):
				container_id = codex_container.lifecycle.start_fresh(make_config(), True, False, runner)

	assert container_id == "new"
	assert commands[:2] == [["stop", "old"], ["rm", "old"]]


#============================================
def test_reconnect_attaches_without_creating() -> None:
	commands = []
	container = codex_container.podman.ManagedContainer("live", "codexdev-live", "Up 1 minute", pathlib.Path("/p"))

	def runner(argv: list[str], input_text: str | None) -> subprocess.CompletedProcess[str]:
		commands.append(argv)
		return subprocess.CompletedProcess(argv, 0, "", "")

	codex_container.lifecycle.reconnect(container, False, None, runner)

	assert commands == [
		["exec", "live", "tmux", "has-session", "-t", "codex"],
		["exec", "-it", "live", "tmux", "attach-session", "-t", "codex"],
	]


#============================================
def test_reconnect_prompt_sends_literal_message_without_attaching() -> None:
	commands = []
	container = codex_container.podman.ManagedContainer(
		"live", "codexdev-live", "Up 1 minute", pathlib.Path("/p"),
	)

	def runner(argv: list[str], input_text: str | None) -> subprocess.CompletedProcess[str]:
		commands.append(argv)
		return subprocess.CompletedProcess(argv, 0, "", "")

	codex_container.lifecycle.reconnect(container, False, "now remove the file", runner)

	assert commands == [
		["exec", "live", "tmux", "has-session", "-t", "codex"],
		[
			"exec", "live", "tmux", "send-keys", "-t", "codex", "-l",
			"now remove the file",
		],
		["exec", "live", "tmux", "send-keys", "-t", "codex", "Enter"],
	]


#============================================
def test_stop_removes_live_agent() -> None:
	commands = []
	container = codex_container.podman.ManagedContainer("live", "codexdev-live", "Up 1 minute", pathlib.Path("/p"))

	def runner(argv: list[str], input_text: str | None) -> subprocess.CompletedProcess[str]:
		commands.append(argv)
		return subprocess.CompletedProcess(argv, 0, "", "")

	codex_container.lifecycle.stop(container, runner)

	assert commands == [["stop", "live"], ["rm", "live"]]
