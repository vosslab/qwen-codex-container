# Changelog

## 2026-08-07

- Added a user-facing disposable Codex lifecycle with fresh start, reconnect, and stop commands.
- Added reusable configuration, interviewing, Podman, Ollama, workspace, bootstrap, and rendering modules.
- Kept durable work in the host Git checkout and made managed containers disposable runtime state.
- Added focused lifecycle tests and a flat human-facing lifecycle E2E runner.
- Set the default test model to `qwen3.5:9b` and keep host and container Ollama routes separate.
- Added the repository-owned `codexdev:latest` Containerfile and image build command.
- Updated the Podman connectivity probe to use the current `pasta` network mode.
- Made reconnect checks verify the live Codex tmux session before attaching.
- Started the tmux agent session detached instead of only detaching Podman exec.
- Bridged Codex's local Ollama provider port to Podman's host-service route.
- Simplified first-success and E2E lifecycle commands around project defaults.
- Added a beginner walkthrough covering creation, reconnect, audit, and cleanup.
- Removed the dry-run from the lifecycle E2E so it exercises a real agent.
- Removed the unnecessary `--detach` flag; noninteractive startup now returns automatically.
- Added `--goal`, which submits Codex's built-in `/goal` command after startup.
- Added `--prompt` as Codex's native positional initial message.
- Allowed `--prompt` and `--goal` together, sending the prompt before the goal.
- Pre-trusted the deliberate container workspace and enabled container-only
  YOLO mode so fresh agents do not stop for trust or approval questions.
- Delayed TUI goal delivery by four seconds until the trusted Codex session has
  rendered.
- Corrected the walkthrough's temporary-file name to match its executable steps.
- Clarified that container YOLO mode can freely change the mounted checkout.
- Made the lifecycle E2E explicitly noninteractive when run from a terminal.
- Made supplied empty CLI values fail validation instead of taking defaults.
- Added pure coverage for positional prompt and literal `/goal` delivery order.
- Removed dead parser state and brittle tests of constants and field storage.
- Added a random eight-character CRC32 suffix to every fresh container name.
- Removed the no-op `--clone` flag, workspace interview, and bind-mount field.
- Removed unused `profile.toml`, `model_catalog.json`, and `container.txt`
  bootstrap artifacts and their renderers.
- Added `reconnect.py -P/--prompt` for literal noninteractive messages to the
  same running Codex TUI.
- Changed the real lifecycle E2E to create, verify, remove, and recheck a file
  through initial and reconnect prompts.
- Added a used container-local Codex model catalog generated from Ollama's
  advertised context, modalities, capabilities, family, size, and quantization.
- Removed Codex's fallback-model warning without hard-coding a context window.
- Protected the real E2E's test file from overwrite and guaranteed container
  cleanup on both success and failure.
- Increased the real E2E observation waits to 20 seconds after a cold local
  model run demonstrated that 10 seconds was intermittent.
- Used Codex 0.147's current reasoning-summary catalog field after live parser
  output showed Ollama's legacy field name was ignored.
