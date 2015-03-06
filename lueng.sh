#!/bin/bash

cd "$( dirname "$0" )" && pwd
python3 src/Main.py &
MAIN_PID=$!

function clean_up {
    kill $(ps -o pid= --ppid ${MAIN_PID})
    kill ${MAIN_PID}
    exit 0
}
trap clean_up SIGTERM SIGKILL SIGINT

wait
