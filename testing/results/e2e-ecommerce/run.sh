#!/bin/bash
cd /home/openclaw/.openclaw/workspace-TVKAgent6/cosmos-intent-sdk/testing/results/e2e-ecommerce/app
source .venv/bin/activate
export COSMOS_ENDPOINT=http://localhost:8081
export COSMOS_KEY="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
python main.py
