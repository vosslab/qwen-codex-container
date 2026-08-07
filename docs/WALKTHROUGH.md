# Agent walkthrough

This walkthrough shows how one disposable agent keeps working in the real
project checkout. It creates and removes one temporary file named
`docs/e2e-test.txt`.

## Start the agent

Open a terminal in a Git project. Start a fresh agent with a real first task:

```bash
./start.py --goal 'write a file docs/e2e-test.txt'
```

The option sends Codex the built-in `/goal write a file docs/e2e-test.txt`
command. When Codex confirms the file exists, disconnect without stopping the
agent:

```text
Ctrl-b d
```

`Ctrl-b d` is the tmux detach shortcut. The agent and its container continue
to run. Wait a moment, then reconnect:

```bash
./reconnect.py
```

## Remove the file

At the same Codex prompt, type this request:

```text
Delete docs/e2e-test.txt. Confirm that it is gone and do not recreate it.
```

Disconnect again with `Ctrl-b d`, wait a moment, then reconnect:

```bash
./reconnect.py
```

Ask Codex to audit the result:

```text
Audit this project and confirm that docs/e2e-test.txt does not exist.
Do not create or modify files.
```

After Codex confirms the file is absent, disconnect one last time with
`Ctrl-b d`. End the disposable runtime:

```bash
./stop.py
```

The container and session are removed. The walkthrough's temporary file is
absent from the checkout.
