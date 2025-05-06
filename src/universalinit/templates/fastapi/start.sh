#!/bin/bash

source venv/bin/activate

uvicorn src.api.main:app --host 0.0.0.0 --port 3000 --reload
