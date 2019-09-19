#!/usr/bin/env bash
set -e
git checkout master config.yml config.py fetch_tz.py generate_index.py \
                    generate_metadata.py generate_signatures.py \
                    base_metadata.json tzdata_files.py requirements.txt

git reset

# Activate or create a virtualenv
VENV_DIR=".venv"
ACTIVATE_LOC="${VENV_DIR}/bin/activate"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv ${VENV_DIR}
fi

source ${ACTIVATE_LOC}

# Update all the requirements
pip install -U pip
pip install -U -r requirements.txt

# Run the relevant scripts
python3 fetch_tz.py
python3 generate_signatures.py
python3 generate_metadata.py
python3 generate_index.py
