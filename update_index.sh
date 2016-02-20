#!/usr/bin/env bash

git checkout master config.yml config.py fetch_tz.py generate_index.py \
                    generate_metadata.py generate_signatures.py \
                    base_metadata.json tzdata_files.py

python fetch_tz.py
python generate_signatures.py
python generate_metadata.py
python generate_index.py