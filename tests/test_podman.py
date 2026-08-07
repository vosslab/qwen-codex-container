import pathlib

import codex_container.config
import codex_container.podman
import codex_container.workspace


#============================================
def test_container_name_includes_project_and_crc() -> None:
	name = codex_container.workspace.container_name(pathlib.Path("/projects/example"), "12ab34cd")

	assert name == "codexdev-example-12ab34cd"


#============================================
def test_create_argv_labels_the_project() -> None:
	config = codex_container.config.make_start_config(
		str(pathlib.Path.cwd()), "model", "http://example.test:11434", False, "image",
	)
	argv = codex_container.podman.create_argv(config)

	assert f"codexdev.project={pathlib.Path.cwd()}" in argv


#============================================
def test_parse_containers_preserves_project_identity() -> None:
	project_dir = pathlib.Path.cwd() / "project"
	containers = codex_container.podman.parse_containers(
		f"abc\tUp 1 minute\tcodexdev-x\t{project_dir}\n",
	)

	assert containers[0].project_dir == project_dir
