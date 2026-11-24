# Scientist Constraints

## Interface
Submit a method as a solver script `scripts/solvers/cycle_sync.sh <input_dir> <output_dir>` (see `briefing/evaluation.md`): it reads the observations of each instance and writes an `n x 3` array of camera locations per instance. The evaluators run it on fixed instances; you do not produce score files yourself, and any score file you write is overwritten.

## Data and Problem Instances
The benchmark instances are fixed by the evaluators: 20 public train instances per setting in `data/instances/train/` and 40 hidden test instances per setting. You may generate as many additional development instances as you like with `data/synthetic.py` (same settings as the benchmark), but the scored instances cannot be replaced, resized or made easier.

## Information Available to a Solver
A solver may use only the inputs it is given: the camera count, the edge list, the observed directions and the setting's name. It must not read ground-truth locations, corruption labels, the evaluators' files, or anything left on disk by an evaluation run, and must not try to locate the hidden test instances.

## Evaluation
Do not modify `eval/`, the metrics, the alignment, or the failure rules. Do not edit `scripts/evaluate_train.sh` / `scripts/evaluate_test.sh`.

## Resource Scale
There is no time limit per instance, but a solver must run unattended, deterministically (fix any random seed) and offline. Learned components may be trained only on instances you generate with `data/synthetic.py`; no external camera datasets or pretrained models.

## Compliance Checklist
- [ ] The method is registered as `scripts/solvers/cycle_sync.sh` and writes `locations` for every instance
- [ ] The solver uses only `n`, `edges`, `directions` and `experiment` from its input files
- [ ] No ground truth, corruption labels or evaluator files are read
- [ ] `eval/` and the evaluation scripts are unchanged
- [ ] Outputs are deterministic for a given input
