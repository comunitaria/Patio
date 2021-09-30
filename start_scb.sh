#!/bin/bash

# Requirements: Python3.7 and 'apt install python3-venv python3-dev', npm

# exit when any command fails
set -e

# Pull the repository to get latest updates, this will work after
# first checkout.
git pull

VENV_DIR="/opt/patio/scb_env"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual env..."
  python3.7 -m venv $VENV_DIR
  source "${VENV_DIR}/bin/activate"
  pip install -r ./energy_manager_flow/requirements.txt
fi

source "${VENV_DIR}/bin/activate"

trap 'kill $BGPID; exit' TERM

cd ./mam_client
npm install
./node_modules/.bin/ts-node src/publisher.ts &
BGPID=$!

sleep 15
cd ../energy_manager_flow
python main.py


wait

