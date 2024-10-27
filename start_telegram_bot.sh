#/bin/bash

cd .
source .venv/bin/activate

PYTHONPATH="${PYTHONPATH}:." python telegram/main.py