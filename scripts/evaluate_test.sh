#!/bin/bash
# Evaluate the held-out test slice of saved method outputs.
#
# The test pass scores the same methods recorded by scores_train.json when
# that file exists, otherwise it enumerates all output manifests on disk.

set -e

cd /home/user

mkdir -p scoring

python eval/test/evaluate.py "$@"
