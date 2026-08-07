import unittest.mock

import codex_container.ollama


#============================================
def test_container_url_translates_host_localhost() -> None:
	url = codex_container.ollama.container_url("http://localhost:11434")

	assert url == "http://host.containers.internal:11434"


#============================================
def test_model_metadata_translates_ollama_show_response() -> None:
	response = {
		"capabilities": ["completion", "vision", "tools", "thinking"],
		"details": {
			"format": "gguf",
			"family": "qwen35",
			"parameter_size": "9.7B",
			"quantization_level": "Q4_K_M",
		},
		"model_info": {"qwen35.context_length": 262144},
	}
	with unittest.mock.patch("codex_container.ollama.post_json", return_value=response):
		metadata = codex_container.ollama.model_metadata(
			"http://localhost:11434", "qwen3.5:9b",
		)

	assert metadata.context_window == 262144
	assert metadata.capabilities == ("completion", "vision", "tools", "thinking")
	assert metadata.family == "qwen35"
	assert metadata.parameter_size == "9.7B"
