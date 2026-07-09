#!/usr/bin/env bash
# Orchestrator overnight: tunggu CEC selesai (raw_D30.csv penuh), lalu jalankan
# expanded ablation (20 run, semua fungsi) -> multi-shift vectors, sekuensial.
set -e
cd "$(dirname "$0")"
PY="../../../.venv/Scripts/python.exe"
CEC_CSV="results_cec/raw_D30.csv"

echo "[queue] menunggu CEC selesai (butuh >1000 baris di $CEC_CSV)..."
while true; do
  if [ -f "$CEC_CSV" ]; then
    n=$(wc -l < "$CEC_CSV" 2>/dev/null || echo 0)
    if [ "$n" -gt 1000 ]; then
      echo "[queue] CEC selesai ($n baris). Lanjut."
      break
    fi
  fi
  sleep 120
done

echo "[queue] === EXPANDED ABLATION (20 run, F1-F13) ==="
"$PY" ablation.py --runs 20 --out results/ablation_full_D30.csv

echo "[queue] === MULTI-SHIFT (far + mixed, 15 run) ==="
"$PY" run_multishift.py --runs 15

echo "[queue] SEMUA JOB OVERNIGHT SELESAI."
