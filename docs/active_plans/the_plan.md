# User-centric lifecycle plan

## Core lifecycle

The user-facing interface is:

```text
start.py
reconnect.py
stop.py
```

These commands have deliberately different meanings.

### `start.py`

`start.py` always creates a fresh agent environment.

A previous container is never reused, resumed, attached, or selected by
`start.py`.

This is repo policy and part of the isolation model. A new start means:

1. Gather startup choices through the shared interviewer.
2. Validate the project and local services.
3. Remove stale runtime state for that project when appropriate.
4. Create a fresh container.
5. Mount the real project checkout read/write.
6. Bootstrap the fresh agent environment.
7. Start a fresh Codex session.
8. Attach for interactive input, or return for noninteractive automation.

Fresh-agent behavior is a required invariant, not an optimization.

The project checkout is durable. Container state is disposable.

### `reconnect.py`

`reconnect.py` reconnects to the currently running agent.

This is the only user-facing command that attaches to an existing instance.

Running it repeatedly attaches to the same live container and tmux session:

```text
./reconnect.py
./reconnect.py
```

No new agent is created.

For noninteractive automation, `--prompt` sends an ordinary message to the same
live TUI and returns without attaching:

```text
./reconnect.py --prompt 'now remove the file'
```

If no reconnectable container exists, report that clearly and exit nonzero.

### `stop.py`

`stop.py` ends the current agent and removes its container.

The normal operation is:

```text
stop
remove container
```

There is no stopped-container lifecycle to preserve.

Worthwhile output already exists in the host checkout. Codex container state is
temporary runtime state.

After `stop.py`, `reconnect.py` has nothing to reconnect to.

The next `start.py` creates a fresh agent.

---

# Shared module structure

Keep the visible scripts thin:

```text
start.py
reconnect.py
stop.py

codex_container/
    __init__.py
    interviewer.py
    config.py
    workspace.py
    preflight.py
    podman.py
    ollama.py
    bootstrap.py
    rendering.py
```

## Shared interviewer

`interviewer.py` owns user input for `start.py`.

The important design is interviewer-first with CLI overrides.

Interactive use:

```text
./start.py
```

Example:

```text
Project folder [current folder]:
>

Model [qwen3.5:9b]:
>
```

CLI values override interviewer questions:

```text
./start.py -p ~/nsh/PROBLEMS/peptidyle-learning-engine
./start.py -p ~/nsh/PROBLEMS/peptidyle-learning-engine -m qwen3.5:9b
./start.py --goal 'write a file docs/e2e-test.txt'
./start.py --prompt 'Explain this project before changing any files.'
```

For each startup input:

1. Use the CLI value when supplied.
2. Otherwise ask through `interviewer.py`.
3. Normalize the result through shared configuration code.

This preserves both convenient interactive use and deterministic automation.

Normal interactive startup attaches to the fresh Codex session so the user can
give it work. Noninteractive automation uses the current project folder and
interviewer defaults, then returns after bootstrap. `--prompt` is Codex's
ordinary positional initial message. `--goal` sends the built-in `/goal`
command to the live Codex TUI. They may be combined, with the initial prompt
sent first and the goal second.

The interviewer should expose small functions such as:

```text
ask_project()
ask_model()
ask_dist_clean()
```

Input and output callables are injectable for pure tests.

`reconnect.py` and `stop.py` need much less interviewing. They should discover
the current managed container directly when the state is unambiguous.

---

# Runtime identity

A project can have at most one currently reconnectable managed agent.

Use Podman labels to identify it:

```text
codexdev.project=<absolute project path>
codexdev.slug=<project slug>
codexdev.role=agent
```

Each fresh container name combines the project slug with an eight-character
CRC32 of fresh random bytes:

```text
codexdev-<slug>-<crc32>
```

`start.py` treats an existing managed container as stale runtime state to be
replaced rather than something to resume.

`reconnect.py` treats it as the current live agent.

`stop.py` removes it.

---

# `start.py`

`start.py` is optimized around the question:

```text
What project should a fresh agent work on?
```

Startup sequence:

1. Parse CLI overrides.
2. Ask the interviewer for missing inputs.
3. Build normalized configuration.
4. Run preflight.
5. Resolve the fresh container specification.
6. Remove stale managed container state for this project.
7. Create the new container.
8. Perform first-start cleanup and bootstrap.
9. Start fresh Codex.
10. Attach for interactive input, or return for noninteractive automation.

There is no automatic resume logic in this path.

There is no existing-session selection.

There is no stopped-container restart.

A call to `start.py` means a fresh agent every time.

---

# `reconnect.py`

`reconnect.py` is intentionally narrow.

Sequence:

1. Identify the managed container for the project or current context.
2. Verify that it is reconnectable.
3. Send a supplied prompt and return, or attach to its existing tmux session.

Repeated calls attach to the same live agent.

The script should do very little configuration work because configuration was
already established by `start.py`.

Example:

```text
./reconnect.py
```

CLI project selection may remain available where needed:

```text
./reconnect.py -p ~/nsh/PROBLEMS/peptidyle-learning-engine
```

CLI prompt delivery is available for automation:

```text
./reconnect.py -P 'now remove the file'
```

The command never creates a replacement agent.

---

# `stop.py`

`stop.py` is intentionally destructive to runtime state.

Sequence:

1. Identify the managed container.
2. Request a graceful stop.
3. Remove the container.
4. Confirm removal.

The host checkout remains untouched.

Container-local runtime state is considered disposable.

Example:

```text
./stop.py
```

After successful completion:

```text
./reconnect.py
```

must fail because there is no live agent.

A later:

```text
./start.py
```

creates a completely new agent.

---

# Container persistence

Persistent container state should be minimized.

The important durable content is:

```text
host project checkout
git history
files created by the agent
```

Do not design the normal lifecycle around keeping an old Codex container alive.

The repository is the handoff point between agents.

This matches the repo policy of using fresh agents and keeps stale agent context
from silently carrying into new work.

---

# Cross-OS build cleanup

The existing project boundary remains:

```text
./devel/dist_clean.sh
```

A fresh container starts from a clean Linux build state when required.

Tracked host-side artifacts include:

```text
target/
node_modules/
dist_wasm/
.pytest_cache/
.venv/
__pycache__/
```

`--dist-clean` remains a `start.py` CLI override.

Bootstrap decisions belong to the new agent being created, rather than being
used to justify reusing an old container.

The deliberate `/workspace` mount is pre-trusted in the container-local Codex
configuration. Codex runs in YOLO mode there, so a new agent starts without
trust or approval questions.

---

# Shared modules

## `config.py`

Create normalized startup configuration after CLI and interviewer inputs are
combined.

For example:

```python
@dataclasses.dataclass
class StartConfig:
	project_dir: pathlib.Path
	model: str
	ollama_url: str
	dist_clean: bool
	goal: str | None
	prompt: str | None
```

Keep derived names in shared helpers.

## `workspace.py`

Responsibilities:

```text
normalize project paths
validate git work trees
derive slugs
locate the managed runtime container
read project labels
```

## `preflight.py`

Preflight for a fresh start checks:

1. Podman machine availability.
2. Project path.
3. Git work tree.
4. Host Ollama availability.
5. Requested model.
6. Container-to-Ollama connectivity.
7. Model context window, modalities, capabilities, and descriptive metadata.
8. Image availability.

Model metadata must be discovered from Ollama. The lifecycle does not contain a
hard-coded model context window. Context and vision map to functional Codex
fields; the remaining Ollama facts are recorded in the catalog description.

Failures print a concrete remedy where available.

## `podman.py`

Keep construction separate from execution.

Core operations:

```text
create_container()
start_container()
attach_container()
stop_container()
remove_container()
find_project_container()
```

The public scripts should not construct raw Podman argv independently.

## `ollama.py`

Own:

```text
URL normalization
model discovery
context and capability discovery
host reachability
container reachability
```

## `bootstrap.py`

Own fresh-agent bootstrap decisions and project-specific tool installation.

Do not make bootstrap state a reason for preserving an old agent container.

## `rendering.py`

Render:

```text
container environment
Codex trust configuration
used Ollama-derived Codex model catalog
```

from the same normalized configuration.

---

# Human-centric E2E test

The lifecycle E2E test should read like the human workflow rather than an
implementation test.

Requirements:

- short, readable commands
- maximum 80 characters per line
- flat linear commands
- no loops
- no helper functions
- report each lifecycle step before running it
- describe the expected state before each file-existence check
- use repo-facing tools
- very few or no environment variables
- no direct Podman commands
- exercise `start.py`
- verify a prompt-created file exists
- exercise `reconnect.py --prompt`
- verify the prompt removed the file
- finish with `stop.py`

Target shape:

```bash
#!/bin/bash
set -eu
source source_me.sh

echo "Preparing lifecycle test (docs/e2e-test.txt must be absent)..."
test ! -e docs/e2e-test.txt
trap 'r=$?; echo "Stopping..."; python3 stop.py || test $r -ne 0; exit $r' EXIT

echo "Starting a fresh Codex agent..."
python3 start.py -P 'write a test file docs/e2e-test.txt' < /dev/null

echo "Waiting for Codex to create docs/e2e-test.txt..."
sleep 20
test -e docs/e2e-test.txt
echo "Created docs/e2e-test.txt."

echo "Reconnecting to the same Codex agent..."
python3 reconnect.py -P 'now remove the file'

echo "Waiting for Codex to remove docs/e2e-test.txt..."
sleep 20
test ! -e docs/e2e-test.txt
echo "Removed docs/e2e-test.txt."
```

The exact repo-supported flags should come from the implementation rather than
inventing E2E-only infrastructure.

The important test sequence is:

```text
start with a write prompt
verify the file
send a removal prompt to the same agent
verify the file is absent
stop
```

The messages narrate the same start, wait, reconnect, and stop flow a person
uses. The precheck protects an existing file at the test path. The exit trap
always runs `stop.py`, including after an assertion failure.

The test should exercise the real user interface. Shared Python unit tests cover
internal command construction and decisions.

---

# Pure tests

Keep detailed behavior in unit tests where complexity belongs.

Test the interviewer with injected input:

```text
CLI project overrides project question
CLI model overrides model question
missing project invokes project question
defaults are accepted
goal and prompt overrides may be combined
```

Test lifecycle decisions:

```text
start always requests fresh creation
start replaces stale managed runtime
reconnect selects existing runtime
reconnect never creates runtime
reconnect prompt sends literal TUI input without attaching
stop requests stop and removal
Ollama metadata becomes the used Codex catalog
```

Test rendering and naming independently.

Test argv construction independently.

The E2E script should not duplicate these implementation checks.

---

# Documentation

Lead every user document with the lifecycle:

```text
./start.py
./reconnect.py
./stop.py
```

Explain the semantics directly:

```text
start.py       create a fresh agent
reconnect.py   reconnect to that live agent
stop.py        end the agent and remove its container
```

Document that starting again intentionally creates a new agent.

Document the repository checkout as the durable boundary between agents.

Implementation details such as Podman naming, labels, tmux, Ollama routing, and
bootstrap hashes belong later in the documentation.

---

# Success criteria

The lifecycle should be understandable without knowing Podman:

```text
start.py
    Fresh agent.

reconnect.py
    Same live agent.

reconnect.py
    Same live agent again.

stop.py
    Agent gone. Container gone.

start.py
    New fresh agent.
```

`start.py` never reconnects to or resumes an earlier instance.

`reconnect.py` never creates a new agent.

`stop.py` removes the container.

The host project checkout is the durable source of worthwhile work.
