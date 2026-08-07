# Disposable Codex Podman agent

Give developers a fresh Codex coding agent for a local Git checkout in a
disposable Podman container, backed by a local Ollama model, while useful file
changes stay durable on the host.

## Keep the work, discard the runtime

The host Git checkout is the handoff boundary. Codex works in that real checkout,
while its Linux environment, tmux session, and container remain disposable.

| Part | During a session | After `./stop.py` |
| --- | --- | --- |
| Git checkout | Mounted read/write at `/workspace` | Files and changes remain |
| Codex session | Reconnectable through tmux | Removed with the container |
| Container | Fresh for the selected project | Stopped and removed |
| Next start | Replaces stale managed runtime | Uses the same durable checkout |

The lifecycle is deliberately small:

```text
./start.py       Create a fresh agent.
./reconnect.py   Reconnect to the same live agent.
./stop.py        Stop the agent and remove its container.
```

- Use a local Ollama model without copying the project into a container volume.
- Reconnect to the same live Codex conversation as often as needed.
- Discover model context, capabilities, family, size, and quantization from Ollama.
- Validate Git, Podman, the image, the model, and container-to-Ollama routing before start.

> Important: the selected checkout is mounted read/write, trusted by Codex, and
> used with approval and sandbox checks bypassed. The container isolates the
> runtime, not the project files. Use a checkout and instructions you trust.

## Quick start

You need Bash, Python 3.12, Git, a running Podman service, and a running Ollama
service. The included `Brewfile` pins Python 3.12 for macOS; Podman and Ollama
remain host-managed prerequisites.

Pull the default model and build the repository-owned container image once:

```bash
ollama pull qwen3.5:9b
./devel/build_image.sh
```

Preview the exact Podman create command without changing runtime state:

```bash
./start.py --dry-run-start -p . -m qwen3.5:9b
```

Then start a real agent with a useful first task:

```bash
./start.py --prompt 'Read this checkout and summarize its purpose.'
```

Press Enter to accept the current folder, `qwen3.5:9b`, and no build cleanup.
Codex opens in the mounted checkout. After it returns the summary, detach from
tmux with `Ctrl-b d`, verify that the same agent is available, and stop it:

```bash
./reconnect.py --check
./stop.py
```

Successful commands report a reconnectable managed-agent name, followed by
`Agent stopped and container removed.` See
[`docs/INSTALL.md`](docs/INSTALL.md) for the complete setup path.

## Continue one conversation

Start with an ordinary initial prompt, detach with `Ctrl-b d`, and send another
message to the same live Codex TUI without attaching:

```bash
./start.py --prompt 'Read AGENTS.md and summarize the project rules.'
./reconnect.py --prompt 'Inspect git status and summarize the current worktree.'
```

Attach whenever interactive work is useful, then stop after worthwhile changes
are saved in the checkout:

```bash
./reconnect.py
./stop.py
```

Starting again always creates a new agent; it never resumes a stopped one. One
project has at most one managed runtime, and `start.py` replaces stale matching
runtime state before creating the fresh container. See
[`docs/USAGE.md`](docs/USAGE.md) for every supported flag and lifecycle variant.

## Documentation

- [`docs/INSTALL.md`](docs/INSTALL.md) - install the model and build the image.
- [`docs/USAGE.md`](docs/USAGE.md) - use start, reconnect, stop, prompts, goals, and checks.
- [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md) - follow one complete file-based session.
- [`docs/CODE_ARCHITECTURE.md`](docs/CODE_ARCHITECTURE.md) - understand ownership,
  managed-container identity, and the durable checkout boundary.

## License

The project is available under the
[`GNU Lesser General Public License v3`](LICENSE.LGPL-3.0.md).
