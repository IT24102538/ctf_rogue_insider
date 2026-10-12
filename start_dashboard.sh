#!/bin/bash
set -eu

command -v python3 >/dev/null 2>&1 || {
    echo "Error: Python 3 is required to run the scoring dashboard." >&2
    exit 1
}

cd "$(dirname "$0")/ctf_dashboard"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
python -m pip install -r requirements.txt
exec python app.py
