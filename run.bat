@echo off
pip install -q fastapi uvicorn pytest
python -m blastradius --repo sample_project --serve --port 8000
