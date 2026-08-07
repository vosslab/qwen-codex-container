# Disposable Codex Podman agent

Create a fresh, disposable Codex agent for a local Git checkout while keeping
all worthwhile work durable in that checkout.

```text
./start.py       Create a fresh agent.
./reconnect.py   Reconnect to the same live agent.
./stop.py        Stop the agent and remove its container.
```

Starting again always creates a new agent; it never resumes a previous one.
Use [`docs/USAGE.md`](docs/USAGE.md) for setup, flags, and lifecycle examples.
Use [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md) for a first agent session.
Use [`docs/CODE_ARCHITECTURE.md`](docs/CODE_ARCHITECTURE.md) for the reusable
module boundary and managed-container identity.
