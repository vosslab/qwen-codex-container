# Installation

Install and start Podman and Ollama on the host. Pull the model used by the
default interviewer choice:

```bash
ollama pull qwen3.5:9b
```

Build the disposable Linux image from this repository:

```bash
./devel/build_image.sh
```

The image provides Git, tmux, socat, wget, and the official `@openai/codex` CLI.
`start.py` uses Codex's Ollama local-provider mode for the selected model.

Continue with [USAGE.md](USAGE.md) for the fresh-agent lifecycle.
