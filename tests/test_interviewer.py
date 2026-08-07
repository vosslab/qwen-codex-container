import codex_container.config
import codex_container.interviewer


#============================================
def test_model_prompt_uses_9b_default() -> None:
	model = codex_container.interviewer.ask_model(lambda prompt: "")

	assert model == codex_container.config.DEFAULT_MODEL


#============================================
def test_project_prompt_accepts_current_folder_default() -> None:
	project = codex_container.interviewer.ask_project(lambda prompt: "", lambda message: None)

	assert project == "."


#============================================
def test_dist_clean_prompt_accepts_default() -> None:
	dist_clean = codex_container.interviewer.ask_dist_clean(lambda prompt: "")

	assert dist_clean is False


#============================================
def test_cli_values_skip_interviewer_prompts() -> None:
	def fail_input(prompt: str) -> str:
		raise RuntimeError("interviewer should not run")

	values = codex_container.interviewer.collect_startup_values(
		"project", "model", True, fail_input,
	)

	assert values == ("project", "model", True)


#============================================
def test_missing_project_uses_injected_interviewer() -> None:
	answers = iter(["chosen-project", "", ""])

	def next_answer(prompt: str) -> str:
		answer = next(answers)
		return answer

	values = codex_container.interviewer.collect_startup_values(
		None, None, None, next_answer, lambda message: None,
	)

	assert values[0] == "chosen-project"
