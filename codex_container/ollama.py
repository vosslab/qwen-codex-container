"""Ollama endpoint and model checks used by fresh startup."""

import dataclasses
import json
import urllib.request


@dataclasses.dataclass(frozen=True)
class ModelMetadata:
	"""Ollama facts that Codex can use for one selected model."""

	context_window: int
	capabilities: tuple[str, ...]
	format: str
	family: str
	parameter_size: str
	quantization_level: str


#============================================
def normalize_url(url: str) -> str:
	"""Return an endpoint without a trailing slash.

	Args:
		url: User supplied Ollama endpoint.

	Returns:
		Normalized endpoint.
	"""
	normalized = url.strip().rstrip("/")
	if not normalized.startswith(("http://", "https://")):
		raise ValueError("Ollama URL must start with http:// or https://")
	return normalized


#============================================
def container_url(host_url: str) -> str:
	"""Translate a host-local Ollama endpoint for Podman containers.

	Args:
		host_url: Ollama endpoint used for host-side discovery.

	Returns:
		Endpoint reachable from the disposable container.
	"""
	normalized = normalize_url(host_url)
	container_endpoint = normalized.replace("localhost", "host.containers.internal")
	container_endpoint = container_endpoint.replace("127.0.0.1", "host.containers.internal")
	return container_endpoint


#============================================
def request_json(url: str) -> dict:
	"""Read one JSON response from Ollama with a short timeout.

	Args:
		url: Endpoint to query.

	Returns:
		Parsed JSON object.

	Raises:
		RuntimeError: If the decoded response is not a JSON object.
	"""
	with urllib.request.urlopen(url, timeout=5) as response:  # nosec B310
		payload = response.read().decode("utf-8")
	data = json.loads(payload)
	if not isinstance(data, dict):
		raise RuntimeError(f"unexpected Ollama response from {url}")
	return data


#============================================
def post_json(url: str, payload: dict) -> dict:
	"""Send one JSON request to Ollama and decode its JSON response.

	Args:
		url: Endpoint to query.
		payload: JSON request body.

	Returns:
		Parsed JSON object.

	Raises:
		RuntimeError: If the decoded response is not a JSON object.
	"""
	encoded = json.dumps(payload).encode("utf-8")
	request = urllib.request.Request(url, data=encoded, method="POST")
	request.add_header("Content-Type", "application/json")
	with urllib.request.urlopen(request, timeout=5) as response:  # nosec B310
		response_text = response.read().decode("utf-8")
	data = json.loads(response_text)
	if not isinstance(data, dict):
		raise RuntimeError(f"unexpected Ollama response from {url}")
	return data


#============================================
def list_models(url: str) -> list[str]:
	"""Return locally available Ollama model names.

	Args:
		url: Normalized Ollama endpoint.

	Returns:
		Available model names.
	"""
	data = request_json(f"{normalize_url(url)}/api/tags")
	models = data["models"]
	names = [model["name"] for model in models]
	return names


#============================================
def validate_model(url: str, model: str) -> None:
	"""Require the selected model to be locally available.

	Args:
		url: Normalized Ollama endpoint.
		model: Requested model name.
	"""
	if model not in list_models(url):
		raise ValueError(f"Ollama model is unavailable: {model}; run `ollama pull {model}`")


#============================================
def model_metadata(url: str, model: str) -> ModelMetadata:
	"""Discover the selected model's Codex-relevant metadata.

	Args:
		url: Normalized Ollama endpoint.
		model: Requested model name.

	Returns:
		Validated model facts reported by Ollama.

	Raises:
		RuntimeError: If required model metadata is absent or malformed.
	"""
	data = post_json(f"{normalize_url(url)}/api/show", {"model": model})
	model_info = data["model_info"]
	if not isinstance(model_info, dict):
		raise RuntimeError(f"Ollama returned invalid model_info for {model}")
	context_window = None
	for key, value in model_info.items():
		if (
			isinstance(key, str)
			and key.endswith(".context_length")
			and isinstance(value, int)
			and not isinstance(value, bool)
			and value > 0
		):
			context_window = value
			break
	if context_window is None:
		raise RuntimeError(f"Ollama did not report a context window for {model}")
	capabilities_value = data["capabilities"]
	if not isinstance(capabilities_value, list) or not all(
		isinstance(capability, str) for capability in capabilities_value
	):
		raise RuntimeError(f"Ollama returned invalid capabilities for {model}")
	capabilities = tuple(capabilities_value)
	if "completion" not in capabilities:
		raise RuntimeError(f"Ollama model does not support completion: {model}")
	if "tools" not in capabilities:
		raise RuntimeError(f"Ollama model does not support tool calling: {model}")
	details = data["details"]
	if not isinstance(details, dict):
		raise RuntimeError(f"Ollama returned invalid details for {model}")
	format_value = details["format"]
	family = details["family"]
	parameter_size = details["parameter_size"]
	quantization_level = details["quantization_level"]
	if not all(
		isinstance(value, str) and value
		for value in (format_value, family, parameter_size, quantization_level)
	):
		raise RuntimeError(f"Ollama returned incomplete model details for {model}")
	metadata = ModelMetadata(
		context_window=context_window,
		capabilities=capabilities,
		format=format_value,
		family=family,
		parameter_size=parameter_size,
		quantization_level=quantization_level,
	)
	return metadata
