# Evaluation

## Protocol: solvers on fixed instances

A method is a **solver**: an executable script `scripts/solvers/<name>.sh` taking two arguments,

    bash scripts/solvers/<name>.sh <input_dir> <output_dir>

`<input_dir>` holds one file `inst_XXX.npz` per problem instance with

- `n` — number of cameras (100),
- `edges` — `m x 2` integer array of camera pairs `(i, j)` with `i < j`,
- `directions` — `m x 3` unit vectors; row `e` approximates `(t_i - t_j) / ||t_i - t_j||` for edge `e = (i, j)`,
- `experiment` — the setting's name (`uniform_high_noise` or `adversarial_high_noise`).

The solver must write `<output_dir>/inst_XXX.npz` (same file name) containing `locations`, an `n x 3` finite array of estimated camera locations. Nothing else in the output is read.

The evaluators own the instances and the ground truth; a solver only ever sees the observations above. Every registered solver is run on every instance of every experiment, and every number is recomputed from the returned locations.

- `scripts/evaluate_train.sh` (and `scripts/evaluate.sh`) run every registered solver on the public train instances in `data/instances/train/` (20 per setting, ground truth included, regenerable with `python data/make_instances.py`) and write `scoring/scores_train.json` (`scoring/scores.json`).
- `scripts/evaluate_test.sh` runs every registered solver on hidden test instances (40 per setting) drawn from the same generator with unpublished seeds, and writes `scoring/scores_test.json`. The hidden test ranks methods; you cannot see or regenerate its instances.

Both sides use the same generator, the same interface and the same metrics, so an honest method scores alike on both.

## Metrics

For each instance the estimate is aligned to the ground truth by the L1 similarity fit (one global scale and translation minimising the sum of per-camera Euclidean distances, the paper's gauge), and the per-camera errors are computed. Per experiment, the reported value is the mean over instances of:

- `median_location_error` (primary, the paper's headline metric) — median per-camera error;
- `mean_location_error` — mean per-camera error;
- `p90_location_error` — 90th-percentile per-camera error (tail failures).

All are lower-is-better. The ranking weighs both experiments equally and, within each, the median, mean and p90 errors with coefficients 1.0, 0.4 and 0.6.

## Failures

A solver that exits non-zero, or an instance whose output is missing, unreadable, of the wrong shape, or non-finite, scores that instance at the error of the uninformative output that puts every camera at one point (about 1.5 median error); valid outputs are capped at the same value. A failed experiment therefore costs its worst value rather than disappearing.

The method key `cycle_sync` is always scored (at the failure value if `scripts/solvers/cycle_sync.sh` is missing): the method being ranked is the one registered as `scripts/solvers/cycle_sync.sh`. Other registered solvers are scored alongside it for comparison.

## Experiments

Both settings use `n = 100` cameras with i.i.d. standard Gaussian 3D locations, an Erdos-Renyi viewing graph with edge probability `p = 0.5`, and noise level `sigma = 0.2`: a clean edge observes its true unit direction plus `sigma` times a uniformly random unit vector, renormalised (see `data/synthetic.py`).

- `uniform_high_noise`: each edge is, with probability `q = 0.7`, replaced by an unrelated uniformly random unit direction.
- `adversarial_high_noise`: each edge is, with probability `q = 0.45`, replaced by the direction between the same two cameras in a second, independent camera configuration, so the corrupted edges agree with each other; noise is then added to every edge.
