import json
import pathlib
import subprocess

import codex_container.bootstrap
import codex_container.config
import codex_container.ollama


#============================================
def test_positional_prompt_precedes_literal_goal_command() -> None:
	events = []
	catalog_text = None
	config = codex_container.config.make_start_config(
		str(pathlib.Path.cwd()),
		"model",
		"http://example.test:11434",
		False,
		"image",
		"write a file",
		"Read AGENTS.md.",
	)
	metadata = codex_container.ollama.ModelMetadata(
		context_window=262144,
		capabilities=("completion", "vision", "tools", "thinking"),
		format="gguf",
		family="qwen35",
		parameter_size="9.7B",
		quantization_level="Q4_K_M",
	)

	def runner(argv: list[str], input_text: str | None) -> subprocess.CompletedProcess[str]:
		nonlocal catalog_text
		if argv[-1] == "cat > /root/.codexdev/model.json":
			catalog_text = input_text
		if "new-session" in argv:
			events.append(("start", argv[-1]))
		if "send-keys" in argv and "-l" in argv:
			events.append(("literal", argv[-1]))
		if "send-keys" in argv and argv[-1] == "Enter":
			events.append(("enter", argv[-1]))
		return subprocess.CompletedProcess(argv, 0, "", "")

	codex_container.bootstrap.bootstrap_fresh_agent("container", config, metadata, runner)

	assert events[0][0] == "start" and events[0][1].endswith(" 'Read AGENTS.md.'")
	assert events[1:] == [
		("literal", "/goal write a file"),
		("enter", "Enter"),
	]
	assert catalog_text is not None
	model = json.loads(catalog_text)["models"][0]
	assert model["context_window"] == 262144
	assert model["max_context_window"] == 262144
	assert model["input_modalities"] == ["text", "image"]
	assert "tools" in model["description"]
