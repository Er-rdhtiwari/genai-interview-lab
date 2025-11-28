#!/usr/bin/env bash
source .venv/bin/activate
export PYTHONPATH=src
uvicorn day01_mini_rag.app.main:app --reload
