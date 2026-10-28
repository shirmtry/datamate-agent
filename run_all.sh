#!/bin/bash
# Run auto_solver over all public questions in batches of 50 (resume-safe).
cd "$(dirname "$0")"
for s in $(seq 0 50 950); do
  python3 auto_solver.py --start $s --end $((s+50)) || echo "batch $s failed"
done
