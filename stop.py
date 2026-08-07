#!/usr/bin/env python3
"""Gracefully stop and remove a disposable Codex agent container."""

import argparse

import codex_container.lifecycle
import codex_container.podman
import codex_container.workspace


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse optional project selection.

	Returns:
		Parsed command-line options.
	"""
	parser = argparse.ArgumentParser(description="Stop and remove the live Codex agent.")
	parser.add_argument("-p", "--project", dest="project_value")
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Select and remove the managed runtime without touching the checkout."""
	args = parse_args()
	if args.project_value:
		project_dir = codex_container.workspace.normalize_project_path(args.project_value)
		container = codex_container.podman.find_project_container(project_dir)
	else:
		container = codex_container.podman.find_only_container()
	codex_container.lifecycle.stop(container)
	print("Agent stopped and container removed.")


if __name__ == "__main__":
	main()
