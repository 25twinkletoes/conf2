#!/usr/bin/env bash
python3 -m unittest discover -s tests
python3 -m src.main --config config.csv
