# Hardening: Cycle-Sync camera-location gym (final pass)

There is no `REVIEW.md` for this gym, so this pass works from `REDTEAM.md` alone. It ran in two steps in the same iteration:

1. **First half (commit `71e9b15`).** It closed the red-team shortcuts:
   - hidden fixed instances;
   - an evaluator-run solver interface;
   - fail-closed scoring;
   - 40 test instances per setting;
   - exact WLS.

   Its job ran but failed `validate.py`. It also exposed that the paper's main claim had nearly vanished.
2. **Second half (this document's numbers).**
   - It read the authors' released code and restored the paper's own data model and unstated parameters.
   - It checked the effect in one exploration job (`redteam/hardening/explore/`).
   - It regenerated everything in one final job (`c510115c-144`), with `redteam/hardening/summary.md` holding the full table.

"Gain" below is the rank's sum before cross-attempt normalisation. It is computed over both experiments (weight 0.5 each) and all three error metrics, as |coefficient| × the improvement over the stored reference on the hidden test. Wins and the paired SE come from the 80 hidden-test instances, comparing each method with the reference on the same instance.

## What changed in this pass and why

### The data generator now follows the authors' code

The authors' repository (github.com/sli743/Cycle-Sync) ships ports of the lab's `UniformCorruptionModel.m` and `AdvCorruptionModel.m`. Its README says the Python and MATLAB releases use "the same synthetic corruption models". In those models a clean edge observes `Normalize(g*_ij + sigma u)`, where `g*_ij` is the true unit direction and `u` a uniformly random unit vector. In the adversarial model the noise is added to every edge after corruption.

The gym had read the paper's Eqs. 9–10 literally, adding `sigma N(0, I)` to `t_i - t_j`. That gives every clean edge a residual of about the same size, which is exactly the regime where reweighting by residual alone works well.

I compared both models on public seeds (`redteam/hardening/explore/results.md`, 16 instances per setting):

| data model | Cycle-Sync (uniform / adversarial) | λ=0 ablation | wins of Cycle-Sync over λ=0 | schedule order vs paper Tables 14–15 |
|---|---|---|---|---|
| Eq. 9–10 as written (old gym) | 0.175 / 0.116 | 0.182 / 0.123 | 5/16, 2/16 per setting; gap within noise | reverse schedule beats the paper's schedule |
| authors' generator (now) | 0.275 / 0.215 | 0.335 / 0.257 | 16/16, 16/16 | all five schedules in the paper's order, in both settings |

Only the authors' generator reproduces the paper's ablation, so it is the paper's actual setting. The change is to the problem's data, not the method's procedure.

### Method parameters the paper does not state now come from the authors' code

- **T-AAB temperatures.** The gym had invented 1, 1.4, …, 1.4⁴ on π-normalised scores. They are now the authors' τ = 2, 4, 8, 16, 20 on radian scores.
- **Clipping.** h is clipped to [1e-8, 10], instead of clipping the weights to [1e-8, 1e8].
- **Kept from the paper's own text** where the release departs from it:
  - the exact geodesic arc distance of Sec. 2.2 (the release uses arccos of the squared projection norm);
  - the average over every 3-cycle in Eq. 6 (the release samples 100 cycles at random).
- **Exact WLS**, from the first half, is kept. The authors' active-set solver also reaches the exact constrained minimiser.

The earlier settings stay available as flags (`--taab-temps gym --weight-clip weight`) and are scored as the variant `prev_taab_clip`.

### The paper's λ=0 number now sits on the right method

The paper's Table 14/15 column "0" is λ_t = 0 inside the Cycle-Sync loop, with a T-AAB start. That is now `cycle_sync_residual_only`, and the paper's 0.36 / 0.32 are attached to it in `scoring/reference.json`.

`welsch_irls` (the same reweighting from uniform weights) and the new `lud` (Least Unsquared Deviations by IRLS, the paper's main comparison method) are self-contained baselines without paper numbers. No paper value was changed.

### Docs

`briefing/problem.md`, `briefing/evaluation.md`, `briefing/method.md`, `briefing/overview.md` and `scoring/EXPERIMENTS.md`, `TARGETS.md`, `CONSTRAINTS.md` and `DIRECTION.md` described the old artifact-manifest protocol and the `benchmark_instance_valid_rate` metric. They now describe the solver interface, the fixed and hidden instances, the failure rule and the three error metrics.

### Unchanged

- Weights: 0.5 / 0.5 per experiment, and 1.0 / 0.4 / 0.6 for median / mean / p90. The paper's headline is the median; mean and p90 guard against sacrificing the tail.
- The evaluators, the metrics and the test size.

## Do better results score higher?

Yes, by far more than the test's noise. The bootstrap std of the reference's weighted error over test instances is 0.008.

| variant | before: red-team gym (5 test instances) | first half (Eq. 9 data, exact WLS) | **now** (paired SE, wins/80) | now, train |
|---|---|---|---|---|
| **better:** Cycle-Sync, then an unweighted refit on its top (1−q)·\|E\| edges by final weight | +0.030 | +0.020 | **+0.102** (0.004, 79/80) | +0.102 |
| better: same, top 0.8·(1−q)·\|E\| edges | — | — | **+0.032** (0.004, 66/80) | +0.041 |
| previous iteration's T-AAB temperatures and weight clipping | — | (was the reference) | +0.006 (0.004, 44/80): tie | +0.037 |
| pre-hardening implementation (approximate WLS, legacy softmin) | — | −0.084 | −0.027 (0.005, 18/80) | +0.011 |
| **weaker:** t_max = 3 | −0.464 | −0.417 | **−0.222** (0.014, 2/80) | −0.263 |
| **weaker:** λ = 1 (cycle-only weights) | −0.205 | −0.137 | **−0.162** (0.011, 1/80) | −0.145 |
| λ = t/(t+5) (fast) | −0.036 | −0.025 | −0.026 (0.003, 14/80) | −0.031 |
| λ = 10/(t+10) (reverse) | −0.0004 | +0.0005 | −0.011 (0.005, 31/80) | −0.003 |

The refit gains in each experiment separately:
- uniform: +0.042 (39/40 wins);
- adversarial: +0.060 (40/40 wins).

Train and test agree on every clear effect. The two exceptions are near-ties: the previous T-AAB settings, and the pre-hardening implementation, whose train slice has only 20 instances per setting.

## Reproduction of the paper's claim (hidden test, 40 instances per setting)

| method | uniform median (paper Table 14) | adversarial median (paper Table 15) | gain vs reference |
|---|---|---|---|
| `cycle_sync`, λ = t/(t+10) (reference) | 0.2832 (0.24) | 0.2041 (0.17) | 0 |
| `cycle_sync_reverse`, 10/(t+10) | 0.2866 (0.27) | 0.2084 (0.18) | −0.011 |
| `cycle_sync_fast`, t/(t+5) | 0.2969 (0.29) | 0.2070 (0.17) | −0.026 |
| `cycle_sync_cycle_only`, λ = 1 | 0.3442 (0.37) | 0.2301 (0.20) | −0.162 |
| `cycle_sync_residual_only`, λ = 0 | 0.3331 (0.36) | 0.2496 (0.32) | −0.110 (1/80 wins) |
| `welsch_irls` (baseline) | 0.3395 | 0.2616 | −0.126 (2/80 wins) |
| `lud` (baseline) | 0.6073 | 0.7041 | −1.013 (0/80 wins) |

- **The core claim reproduces.** Cycle reweighting beats residual-only reweighting in both settings, on 79/80 instances.
- **The paper's schedule is the best of the five**, as the paper reports. Reverse and fast are close; cycle-only and λ = 0 are clearly worse.
- **The absolute errors are 15–20% above the paper's** for Cycle-Sync, and the λ = 0 gap is smaller than the paper's (15–18% vs 33–47%).
- **Exact recovery also reproduces** (public seeds, `explore/results.md`): median error below 1e-8 on 5/5 noiseless instances at q = 0.8 uniform and q = 0.4 adversarial, while LUD fails, as in the paper's Fig. 3.
- `python validate.py --post-design --compare` passes, including the paper-consistency check that failed in the first half: the λ = 0 number had been 2.5× off.

## Reference score before and after

| | uniform median / mean / p90 | adversarial median / mean / p90 | test size |
|---|---|---|---|
| red-team gym | 0.1939 / — / — | 0.1237 / — / — | 5 per setting, chosen by file-name hash from agent-written artifacts |
| first half | 0.1728 / 0.2043 / 0.3211 | 0.1166 / 0.1923 / 0.2183 | 40 hidden, Eq. 9 data |
| **now** | **0.2832 / 0.3482 / 0.5866** | **0.2041 / 0.2816 / 0.4076** | 40 hidden, authors' generator |

The errors are higher now because the restored noise model is harder for every method, not because the method got worse. On the same instances the previous reference settings score within 0.006 of it.

The reference is deterministic, and no wall-clock limit sits anywhere in the method's path or the evaluator. Rerunning it inside the variant pass gives bit-identical scores.

## Shortcuts (hidden test, through the real evaluator)

| shortcut (red-team folder → hardening solver) | before | now | fix |
|---|---|---|---|
| copy ground truth from the agent's own artifacts (`copy_truth`, incl. forged truth) | **+0.441** | −2.96 (`sc_read_hidden_truth`: searched every .npz in the workspace and /tmp, matched 0/40) | Solvers receive only `n`, `edges`, `directions`, `experiment`. The truth lives only in `eval/test/instances/` (unrecorded 128-bit seeds) and is deleted from disk while solvers run. |
| oracle corruption labels (`oracle_mask`) | **+0.135** | not expressible | Labels are never given to solvers. |
| easier instances, smaller σ or q (`easier_instances`) | **+0.208 / +0.081** | not expressible | The evaluator owns the instances; solvers cannot create them. |
| drop the hardest cameras (`trim_cameras`) | **+0.046** | −2.96 (`sc_trim`, 40/40 failed) | Wrong shape ⇒ the instance scores its worst value. |
| seed cherry-picking / split steering | **+0.026 / +0.012** | not expressible | Fixed hidden instances, not agent-chosen files. |
| drop the failed experiment (manifest, `scores_train.json`, `reference.json`) | **0.000** (honest −0.236) | −1.53 (`sc_crash_adversarial`) | Every registered solver is run on every experiment, and a crash scores worst. Experiment and metric lists live in `eval/test/evaluate.py`; nothing is read from `scoring/`. `cycle_sync` is always scored. |
| NaN outputs | conditional (NaN in the JSON) | −2.96 (`sc_nan`) | Non-finite ⇒ worst; the JSON never holds NaN. |
| forged `scores_test.json` | conditional **+0.441** | −2.96 (`sc_forge_scores`) | The file is deleted at the start and rewritten after every solver run; a file forged during the run is overwritten. |
| partial outputs | — | −1.48 (`sc_partial`, 20/40 failed per setting) | Missing instance ⇒ worst. |
| all cameras at one point / 1e300-scale outputs | −3.26 | −2.96 / −2.94 | Capped at the worst value; overflow-safe normalisation. |

## Headroom check

- **Bound.** The reference sits at the bound of no scored metric. All three are errors bounded below by 0, and the reference is at 0.20–0.59.
- **Room above.**
  - A variant that uses no hidden information gains +0.102 on the hidden test.
  - An oracle least-squares fit on the truly clean edges reaches 0.171 / 0.134 median error on public seeds, against the reference's 0.275 / 0.215 on the same seeds, so most of the gap is still open.
  - Neither one simple variant nor the oracle reaches the bound: σ = 0.2 noise sets a floor.
- **No experiment was added.** Headroom exists in both scored experiments.
- **Baselines.** All score clearly below the reference on a scale with room above it: residual-only Welsch IRLS −0.126, λ = 0 ablation −0.110, LUD −1.01. On public seeds, a single unweighted least-squares solve scores −1.37 / −1.83 weighted cost per setting.
- **Brute force.**
  - Not rerun on the new data.
  - Hypothesise-and-verify over inlier sets cannot work here. With q = 0.7, a random rigid subset of the ≈2n edges needed to fix 100 cameras is clean with probability about 0.3^200.
  - The red team's budgeted version of that search scored −2.53 on the old data.
  - The objective needs ground truth, so no private search over the hidden test is possible.

## Left open, stated plainly

- **Git history.** `eval/test/instances/*.npz` are committed, and so are the obsolete Eq. 9 instances from the first half. Whatever hides `eval/test/` from future agents must also keep them away from its git history; the gym cannot enforce that.
- **Process memory.** A solver runs as a child of the evaluator, which holds the test truth in memory. Reading the parent's memory is not defended, per the brief's rule on the process environment.
- **The setting's name reaches the solver** (`experiment`), so a method can use the public q of each setting; `better_refit` does. This is public problem information, not hidden data.
- **Honest alternatives the test cannot separate** from the reference:
  - the previous iteration's T-AAB temperatures and weight clipping: +0.006, within 1.6 paired SE;
  - the reverse schedule on the uniform setting: +0.0015.
  These are headroom limits for hyperparameter tweaks, not loopholes.
- **Paper magnitudes are not matched exactly.** Cycle-Sync's absolute errors are 15–20% above the paper's, and its margin over λ = 0 is about half the paper's. The ordering of all five schedules matches.
- **Not reproduced: Eq. 9–10 vs the release.** The paper's Eqs. 9–10 differ from the generator that produced its tables. The gym now follows the release; the noise model is stated in `data/synthetic.py` and `briefing/evaluation.md`.
- **Not reproduced: real-image experiments.** The ETH3D / IMC-PT / 1DSfM pipelines (MPLS-cycle rotations, STE directions) remain out of scope.
