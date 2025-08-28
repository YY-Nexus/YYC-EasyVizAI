#!/usr/bin/env bash
set -e
echo "[+] Installing backend deps"
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
deactivate
echo "[+] Installing frontend deps"
cd frontend && pnpm install
echo "[+] Done. Run 'make dev' to start."