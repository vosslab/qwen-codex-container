# Codex container architecture

The user-facing lifecycle stays intentionally small:

```text
start.py       Fresh agent.
reconnect.py   Same live agent.
stop.py        Agent and container removed.
```

The scripts delegate to reusable modules in `codex_container/`.

- `interviewer.py` asks only for startup values that the CLI did not supply.
- `config.py` normalizes fresh-start choices into `StartConfig`.
- `workspace.py` validates Git worktrees and derives runtime identity.
- `preflight.py` validates Podman, Ollama, the image, and container routing,
  then returns model metadata discovered from Ollama.
- `podman.py` builds and runs all managed-container commands.
- `ollama.py` owns endpoint and local-model discovery.
- `bootstrap.py` creates a fresh tmux-based Codex session.
- `rendering.py` creates the container-local Codex configuration, used model
  catalog, and shell environment.
- `lifecycle.py` owns the high-level start, reconnect, and stop decisions.

Managed containers have `codexdev.project`, `codexdev.slug`, and
`codexdev.role=agent` labels. A project has at most one managed runtime.
Container names add a random eight-character CRC32 suffix to the project slug.
`start.py` stops and removes stale matching state before it creates a new
container. `reconnect.py` only attaches to or sends a prompt to a live labeled
runtime. `stop.py` stops and removes it.

The host Git checkout is the only durable boundary. It is mounted read/write at
`/workspace`; the container and its Codex session are disposable.

Fresh startup queries Ollama's `/api/show` endpoint for the selected model.
The generated catalog maps Ollama's advertised context window and vision
capability into Codex's functional fields. It also records architecture family,
parameter size, quantization, and the complete capability list in the catalog
description. The generated Codex config references that catalog, so custom
Ollama models do not use Codex's generic fallback metadata. No context window
is hard-coded in the lifecycle.
