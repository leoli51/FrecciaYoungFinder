#/bin/bash

cd .
source .venv/bin/activate

PYTHONPATH="${PYTHONPATH}:." TELEGRAM_BOT_TOKEN="insert token here" python telegram/main.py