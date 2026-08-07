#!/usr/bin/env python3
"""Create a new disposable Codex agent for one Git project."""

import argparse
import sys

import codex_container.config
import codex_container.interviewer
import codex_container.lifecycle


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse fresh-start CLI overrides.

	Returns:
		Parsed command-line options.
	"""
	parser = argparse.ArgumentParser(description="Create a fresh disposable Codex agent.")
	parser.add_argument("-p", "--project", dest="project_value")
	parser.add_argument("-m", "--model", dest="model_value")
	parser.add_argument("-g", "--goal", dest="goal")
	parser.add_argument("-P", "--prompt", dest="prompt")
	clean_group = parser.add_mutually_exclusive_group()
	clean_group.add_argument("--dist-clean", dest="dist_clean", action="store_true")
	clean_group.add_argument("--no-dist-clean", dest="dist_clean", action="store_false")
	parser.add_argument("-n", "--dry-run-start", dest="dry_run_start", action="store_true")
	parser.set_defaults(dist_clean=None, dry_run_start=False)
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Gather values, then create and optionally attach a fresh agent."""
	args = parse_args()
	project_value = args.project_value
	model_value = args.model_value
	dist_clean_value = args.dist_clean
	if not sys.stdin.isatty():
		if project_value is None:
			project_value = "."
		if model_value is None:
			model_value = codex_container.config.DEFAULT_MODEL
		if dist_clean_value is None:
			dist_clean_value = False
	project_value, model_value, dist_clean = (
		codex_container.interviewer.collect_startup_values(
			project_value, model_value, dist_clean_value,
		)
	)
	config = codex_container.config.make_start_config(
		project_value,
		model_value,
		codex_container.config.DEFAULT_OLLAMA_URL,
		dist_clean,
		codex_container.config.DEFAULT_IMAGE,
		args.goal,
		args.prompt,
	)
	# Interactive users enter the fresh session; automation continues after bootstrap.
	detach = not sys.stdin.isatty()
	container_id = codex_container.lifecycle.start_fresh(
		config, detach, args.dry_run_start,
	)
	if container_id:
		print(f"Fresh agent created: {container_id}")


if __name__ == "__main__":
	main()
