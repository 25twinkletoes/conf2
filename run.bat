@echo off
python -m unittest discover -s tests
python -m src.main --config config.csv
