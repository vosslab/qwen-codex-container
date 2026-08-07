"""Text renderers for the fresh agent's container-local configuration."""

import json

import codex_container.config
import codex_container.ollama


#============================================
def render_environment(config: codex_container.config.StartConfig) -> str:
	"""Render shell exports used to launch a fresh session.

	Args:
		config: Normalized fresh-agent configuration.

	Returns:
		Shell-compatible environment declarations.
	"""
	environment = (
		"export OLLAMA_HOST='" + codex_container.ollama.container_url(config.ollama_url) + "'\n"
		"export CODEX_MODEL='" + config.model + "'\n"
		"export CODEX_HOME='/root/.codexdev'\n"
	)
	return environment


#============================================
def render_codex_config() -> str:
	"""Render dynamic catalog selection and the fixed workspace trust policy.

	Returns:
		TOML that loads discovered metadata and trusts `/workspace`.
	"""
	text = (
		'model_catalog_json = "/root/.codexdev/model.json"\n\n'
		'[projects."/workspace"]\n'
		'trust_level = "trusted"\n'
	)
	return text


#============================================
def render_model_catalog(
	config: codex_container.config.StartConfig,
	metadata: codex_container.ollama.ModelMetadata,
) -> str:
	"""Render an Ollama-derived model entry in Codex's catalog format.

	Args:
		config: Normalized fresh-agent configuration.
		metadata: Selected model facts reported by Ollama.

	Returns:
		Indented JSON consumed by Codex at startup.
	"""
	modalities = ["text"]
	if "vision" in metadata.capabilities:
		modalities.append("image")
	description = (
		f"Ollama {metadata.family} model; {metadata.parameter_size}; "
		f"{metadata.quantization_level}; {metadata.format}; capabilities: "
		+ ", ".join(metadata.capabilities)
	)
	model = {
		"slug": config.model,
		"display_name": config.model,
		"description": description,
		"context_window": metadata.context_window,
		"max_context_window": metadata.context_window,
		"shell_type": "default",
		"visibility": "list",
		"supported_in_api": True,
		"priority": 0,
		"truncation_policy": {"mode": "bytes", "limit": 10000},
		"input_modalities": modalities,
		"base_instructions": "",
		"support_verbosity": True,
		"default_verbosity": "low",
		"supports_parallel_tool_calls": False,
		"supports_reasoning_summary_parameter": False,
		"supported_reasoning_levels": [],
		"experimental_supported_tools": [],
	}
	catalog = {"models": [model]}
	text = json.dumps(catalog, indent=2) + "\n"
	return text
