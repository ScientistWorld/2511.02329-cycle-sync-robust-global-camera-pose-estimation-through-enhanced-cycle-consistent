#!/bin/bash
# Exploration job (final hardening pass, step 1 of 2): compare the paper's
# Eq. 9-10 data model with the authors' released generator, the gym's T-AAB
# settings with the authors', the paper's lambda=0 ablation and simple
# baselines, and headroom variants, on public seeds. Writes
# redteam/hardening/explore/results.{md,json}. Touches no score file.

set -e

cd /home/user

python -c "import sys, numpy, scipy; print(sys.version); print('numpy', numpy.__version__, 'scipy', scipy.__version__)"
python redteam/hardening/explore/explore.py
