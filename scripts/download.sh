#!/bin/bash
# Download all data and models needed for this environment.
#
# Run on a node with internet access BEFORE building the container
# or submitting compute jobs.
#
# This script should be idempotent — safe to run multiple times.
# It should skip files that already exist.
#
# Update the storage estimate below as you add downloads.
#
# Estimated total download size: 0 GB
# Estimated disk usage after extraction: 0 GB
#
# This paper's benchmark data is generated procedurally. If external assets
# are added later, fetch them into data/downloads/ with idempotent guards.

set -e

cd /home/user

mkdir -p data/downloads
echo "Cycle-Sync synthetic experiments generate data procedurally; no external downloads are required."
