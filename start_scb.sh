#!/bin/bash

# Requirements: Python3.7 and 'apt install python3-venv'

# exit when any command fails
set -e

VENV_DIR="${HOME}/scb_env"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual env..."
  python3.7 -m venv $VENV_DIR
  source "${VENV_DIR}/bin/activate"
  pip install -r ./energy_manager_flow/requirements.txt
fi

source "${VENV_DIR}/bin/activate"

trap 'kill $BGPID; exit' TERM

cd ./mam_client
./node_modules/.bin/ts-node src/publisher.ts &
BGPID=$!

sleep 5
cd ../energy_manager_flow
python main.py


wait

