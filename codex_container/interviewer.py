"""Injectable prompts used only by fresh startup."""

import collections.abc

import codex_container.config


Input = collections.abc.Callable[[str], str]
Output = collections.abc.Callable[[str], None]


#============================================
def ask_project(input_func: Input = input, output_func: Output = print) -> str:
	"""Ask for the checkout that a new agent should use.

	Args:
		input_func: Function that reads a prompt.
		output_func: Function that writes an explanation.

	Returns:
		The project path entered by the user.
	"""
	output_func("Project folder [current folder]:")
	project = input_func("> ").strip()
	if not project:
		project = "."
	return project


#============================================
def ask_model(input_func: Input = input) -> str:
	"""Ask for the requested Ollama model.

	Args:
		input_func: Function that reads a prompt.

	Returns:
		The entered model, or the normal default.
	"""
	prompt = f"Model [{codex_container.config.DEFAULT_MODEL}]: "
	model = input_func(prompt).strip()
	if not model:
		model = codex_container.config.DEFAULT_MODEL
	return model


#============================================
def ask_dist_clean(input_func: Input = input) -> bool:
	"""Ask whether to clean cross-OS build artifacts before startup.

	Args:
		input_func: Function that reads a prompt.

	Returns:
		True when the user requests a dist-clean.
	"""
	answer = input_func("Clean Linux build artifacts [no]: ").strip().lower()
	if answer in ("", "n", "no"):
		return False
	if answer in ("y", "yes"):
		return True
	raise ValueError("answer yes or no")


#============================================
def collect_startup_values(
	project_value: str | None,
	model_value: str | None,
	dist_clean_value: bool | None,
	input_func: Input = input,
	output_func: Output = print,
) -> tuple[str, str, bool]:
	"""Combine CLI overrides with only the required interviewer prompts.

	Args:
		project_value: Optional CLI project path.
		model_value: Optional CLI model name.
		dist_clean_value: Optional CLI cleanup choice.
		input_func: Function that reads a prompt.
		output_func: Function that writes an explanation.

	Returns:
		Project, model, and dist-clean choice.
	"""
	if project_value is None:
		project_value = ask_project(input_func, output_func)
	if model_value is None:
		model_value = ask_model(input_func)
	if dist_clean_value is None:
		dist_clean_value = ask_dist_clean(input_func)
	values = (project_value, model_value, dist_clean_value)
	return values
