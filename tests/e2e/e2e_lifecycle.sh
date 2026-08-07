#!/bin/bash
set -eu
source source_me.sh
test ! -e docs/e2e-test.txt
trap 'result=$?; python3 stop.py || test $result -ne 0; exit $result' EXIT
python3 start.py -P 'write a test file docs/e2e-test.txt' < /dev/null
sleep 20; test -e docs/e2e-test.txt
python3 reconnect.py -P 'now remove the file'
sleep 20; test ! -e docs/e2e-test.txt
