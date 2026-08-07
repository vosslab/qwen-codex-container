#!/usr/bin/env python3
"""Reconnect to the one currently running disposable Codex agent."""

import argparse

import codex_container.lifecycle
import codex_container.podman
import codex_container.workspace


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse optional project selection and noninteractive actions.

	Returns:
		Parsed command-line options.
	"""
	parser = argparse.ArgumentParser(description="Reconnect to the live Codex agent.")
	parser.add_argument("-p", "--project", dest="project_value")
	action_group = parser.add_mutually_exclusive_group()
	action_group.add_argument("-c", "--check", dest="check", action="store_true")
	action_group.add_argument("-P", "--prompt", dest="prompt")
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Find the existing runtime, then check, prompt, or attach to it."""
	args = parse_args()
	if args.project_value is not None:
		project_dir = codex_container.workspace.normalize_project_path(args.project_value)
		container = codex_container.podman.find_project_container(project_dir)
	else:
		container = codex_container.podman.find_only_container()
	codex_container.lifecycle.reconnect(container, args.check, args.prompt)
	if args.check:
		print(f"Reconnectable agent: {container.name}")
	if args.prompt is not None:
		print(f"Prompt sent to agent: {container.name}")


if __name__ == "__main__":
	main()
