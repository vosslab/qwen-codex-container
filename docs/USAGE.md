# Codex container lifecycle

Use the three root commands in this order:

```text
./start.py
./reconnect.py
./stop.py
```

- `start.py` creates a fresh agent. It never resumes or reconnects to an old one.
- `reconnect.py` attaches to the same live agent and may be run repeatedly.
- `stop.py` ends the agent and removes its container.

The project checkout is the durable handoff boundary. Files created by an agent
remain in the local Git checkout after `stop.py`; container-local session state
does not. Starting again intentionally creates a new agent.

## Start a fresh agent

From the project checkout, run the command without flags:

```bash
./start.py
```

Press Enter to accept the current project folder, `qwen3.5:9b`, and no build
cleanup. Then use the same short commands when you need the live agent again
or are ready to end it:

```bash
./reconnect.py
./stop.py
```

Use flags only when an unusual run needs a different project or model:

```bash
./start.py -p ~/nsh/example -m qwen3.5:9b
```

Use `--goal` to send Codex's built-in `/goal` command immediately after the
fresh session starts:

```bash
./start.py --goal 'write a file docs/e2e-test.txt'
```

Use `--prompt` for Codex's ordinary positional initial message. Combine it
with `--goal` when the agent needs both an initial message and an ongoing
objective:

```bash
./start.py --prompt 'Read AGENTS.md.' --goal 'write a file docs/e2e-test.txt'
```

When standard input is interactive, `start.py` attaches to the new Codex
session. Automated noninteractive runs create the session and return so their
checks can continue.

The default host Ollama endpoint is `http://localhost:11434`; the container
uses Podman's `host.containers.internal` route automatically. The default
workspace is a read/write bind mount of the real project checkout.

The fresh container trusts its deliberate `/workspace` mount and runs Codex in
YOLO mode. Trust and approval questions are disabled, and the agent can freely
change the selected read/write project checkout. Use this only with a project
and initial instructions you trust.

`--dist-clean` runs the selected project's `devel/dist_clean.sh` before the
fresh container starts. `--dry-run-start` prints the planned container creation
command without creating a container.

Fresh start checks that Podman is available, the project is a Git worktree, the
chosen Ollama model is local, the image exists, and the container can reach
Ollama. Startup also reads the selected model's context window, capabilities,
architecture family, parameter size, and quantization from Ollama. It writes a
container-local Codex model catalog automatically; users do not configure a
context window or catalog. Build the repository-owned image before the first
real start:

```bash
./devel/build_image.sh
```

The image installs Codex with the official `@openai/codex` package, then starts
Codex with its supported Ollama local-provider mode. See the official
[Codex CLI documentation](https://developers.openai.com/codex/cli/) for the
CLI installation and local-provider details.

## Reconnect and stop

Reconnect to the one running agent:

```bash
./reconnect.py
```

Use `--check` to verify that an existing agent is reconnectable without opening
an interactive tmux session. If more than one managed agent exists, select one
with `--project`; reconnect never creates a replacement agent.

Use `--prompt` to send an ordinary message to the running agent and return
without opening the interactive session:

```bash
./reconnect.py --prompt 'now remove the file'
```

`--prompt` and `--check` are mutually exclusive. Sending a prompt preserves the
same agent, thread, and project context.

Stop and remove the agent after its work is saved in the checkout:

```bash
./stop.py
```

After a successful stop, `reconnect.py` fails because no live agent remains.

For a complete first-use session, follow [WALKTHROUGH.md](WALKTHROUGH.md).
