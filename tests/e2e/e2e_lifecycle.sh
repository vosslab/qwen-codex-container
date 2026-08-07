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
