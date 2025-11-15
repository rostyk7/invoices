#!/bin/bash

if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

uv pip install -r requirements.txt || pip install -r requirements.txt

uv pip install -e ../lib/ || pip install -e ../lib/

python app.py

