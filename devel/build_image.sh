#!/bin/bash
# Build the disposable Codex agent image used by start.py.

set -eu

podman build --tag codexdev:latest --file Containerfile .
