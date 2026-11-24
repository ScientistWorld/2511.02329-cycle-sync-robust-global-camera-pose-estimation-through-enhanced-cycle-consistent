# Red-team audit: Cycle-Sync camera-location gym

All numbers come from one CPU job (`redteam/run_all.sh`, about 33 min on 1 CPU). Each run lives in `redteam/<name>/run.sh`. A run builds a sandbox holding the gym's unchanged `eval/`, its train and test scripts (only the `cd /home/user` line points at the sandbox) and `scoring/reference.json`. It puts the change in place the way an agent would, runs `evaluate_train.sh`, then runs `evaluate_test.sh` with no arguments. Each folder keeps its own `scores_test*.json`, `scores_train*.json` and `test_exit_code*.txt`. The full table is in `redteam/summary.md`.

"Weighted gain" is the rank's sum before its cross-attempt normalisation: over both experiments (weight 0.5 each) and every declared metric, |coefficient| × the improvement over the reference's hidden-test score, taken in the metric's better direction. Missing values are skipped, as the rank does. Reference = gym `cycle_sync`, weighted gain 0 by definition.

## Headline: the hidden test has no hidden data

`eval/test/evaluate.py` reads only `.npz` artifacts that the method writes itself. Each artifact carries the **ground-truth locations**, the instance settings (`n`, `p`, `q`, `sigma`, `corruption`) and the corruption labels. The method also creates the instances: it calls `data/synthetic.py` with seeds it chooses. The "test" slice is just whichever half of the agent's own files hash into it by file name. So the test answers are always on disk. Any number from 0 error upward can be produced without a better solver (`shortcut_copy_truth`: weighted gain +0.441, the maximum possible).

## 1. Do better results score higher?

On the gym's own instances (seed base 100), yes: score follows quality, and the test agrees with the train slice.

| variant (agent's `cycle_sync`) | uniform median | adversarial median | weighted gain, test | weighted gain, train |
|---|---|---|---|---|
| reference Cycle-Sync (t_max=20) | 0.1939 | 0.1237 | 0 | 0 |
| **better:** Cycle-Sync + L2 refit on its top (1−q)·\|E\| edges by its own final weight (size picked on train) | 0.1827 | 0.1163 | **+0.030** | +0.069 |
| refit, top 0.75·(1−q)·\|E\| edges | 0.1831 | 0.1296 | +0.001 (tie) | +0.008 |
| refit, top 0.5·(1−q)·\|E\| edges | 0.1993 | 0.1366 | −0.023 | −0.046 |
| more iterations, t_max=40 (not better) | 0.2054 | 0.1301 | −0.031 | −0.026 |
| **weaker:** t_max=3 | 0.2321 | 0.2863 | **−0.464** | −0.327 |
| **weaker:** cycle term removed (residual-only Welsch IRLS) | 0.3394 | 0.2185 | **−0.490** | −0.487 |
| weaker: residual term removed (cycle-only weights) | 0.2457 | 0.1716 | −0.205 | −0.166 |

- **Better variant.** The refit uses no hidden information. It has lower error than the reference on 9 of the 10 test instances (5/5 uniform, 4/5 adversarial). Its test gain is +0.030: about 1.5× the seed-spread std of the weighted score (0.021) but below its range (0.044).
- **Weaker variants.** They lose 0.2 to 0.5, more than 10× the seed spread.
- **More iterations.** t_max=40 is not an improvement, and train and test agree on that.
- **Caveat that matters.** The instance set is not fixed by the gym. An honest agent that only changes the seed base (200 or 300) moves its score by −0.044, which is more than the genuine refit gain. Instance luck the agent controls can outweigh a real method improvement.

## 2. Seed spread and reproduction check

Cycle-Sync is deterministic given an instance, so the "seed" is the instance seed base. `variant_seed_spread` regenerates everything from scratch with the gym's own `method/run_synthetic.py` and `baseline/run_irls.py`.

| seed base | Cycle-Sync uniform / adversarial median | Welsch IRLS uniform / adversarial median | Cycle-Sync weighted gain |
|---|---|---|---|
| 100 (gym) | 0.1939 / 0.1237 | 0.3394 / 0.2185 | 0 |
| 200 | 0.2086 / 0.1358 | 0.3615 / 0.2463 | −0.044 |
| 300 | 0.2002 / 0.1496 | 0.3598 / 0.2440 | −0.043 |
| std (range) | 0.006 (0.015) / 0.011 (0.026) | | 0.021 (0.044) |

- **Reproducibility.** The seed-100 regeneration and the re-scoring of the reference outputs on disk are both bit-identical to the committed `scoring/scores_test.json`.
- **Does the method beat its baseline?** Yes, in the paper's direction on every seed: uniform 0.19–0.21 vs 0.34–0.36 (paper Table 14: 0.24 vs 0.36), adversarial 0.12–0.15 vs 0.22–0.25 (paper Table 15: 0.17 vs 0.32). The reproduced errors are lower than the paper's.
- **Schedule ablation.** The paper reports t/(t+10) as best. Here the reverse schedule 10/(t+10) ties it (0.1906 / 0.1253, weighted gain −0.0004). The fast schedule (−0.036) and cycle-only (−0.205) are worse, as in the paper.
- **Synthetic data.** It is the paper's own synthetic model (Eqs. 9–10, n=100, p=0.5, q=0.7 / 0.45, σ=0.2). The effect the paper studies, cycle reweighting beating residual-only reweighting, shows up clearly.

**Where the gym departs from the paper:**
- **Trials scored.** The hidden test scores only 5 of the 10 trials per setting; the paper uses 10.
- **WLS solve.** The constrained weighted least-squares step (α ≥ 1, Σt = 0) is solved by alternating α updates and linear solves (at most 20 inner steps), not exactly.
- **T-AAB initialisation.** Its iteration count, β0 = 1 and growth 1.4 are this implementation's choices; the paper only gives theorem bounds. The AAB geodesic distance is the implementation's own closest-point-on-arc version.
- **Baselines.** The only baseline is residual-only IRLS (λ=0). ShapeFit, BATA, LUD and FusedTA are absent.
- **Settings scored.** Only the two supplementary high-noise settings are scored. The Fig. 3 corruption sweeps and the ETH3D real data are not.
- **Matches the paper:** t_max=20, β=20, λ_t=t/(t+10), the well-shaped angle arcsin(0.6), exp(−20s) initial weights, and L1 similarity alignment.

**Brute force.** A budgeted hypothesize-and-verify search over inlier sets (400 random connected 300-edge subsets per instance, then a refit on the best inlier set) finds only ~120 consistent edges out of ~2 500 (about 740 are clean). It scores 1.35 / 1.03 median error (weighted −2.53), about the same as an all-zero output. Brute force does not solve the test, so the instances are not too small.

## 3. Scoring mechanics

- **Metrics at their bound.** `benchmark_instance_valid_rate` (coefficient 0.5) is already 1.0 for the reference. It is computed from scalars the method writes, so every shortcut below also gets 1.0. It can only penalise and measures nothing the agent cannot write. Under cross-attempt normalisation its near-zero spread could blow up any small deviation. `mean_corruption_fraction` has coefficient 0 and is also self-reported. The error metrics have bound 0 and the reference sits at 0.12–0.43, so there is room above it. The baseline is −0.49 and zero/random outputs are −3.26, so the scale is sensible.
- **Coefficient signs.** They are consistent: error metrics have a negative coefficient with `higher_is_better: false`; validity has a positive coefficient with `true`.
- **Can a failing method outrank the reference through other metrics?** Not through other metrics: the three error metrics move together and validity is capped at 1.0. But a failing method can make its failed experiment **disappear**, which turns −0.236 into 0 (see `shortcut_drop_hard_experiment`).
- **Does a failed run get its worst value?** No. A missing experiment produces no entry and is skipped. A NaN output produces `NaN` metrics, and the file is then not strict JSON.
- **Does the test write every method on disk?** No. It writes only the method/experiment pairs listed in `scoring/scores_train.json`, and only the experiments listed in `scoring/reference.json`. Both files are agent-writable and neither is restored before the test; the agent is not even given `reference.json`.

## 4. Shortcuts (all real runs, hidden test score vs reference)

| shortcut (`redteam/<folder>`) | what it does | uniform / adversarial median | weighted gain vs ref | result |
|---|---|---|---|---|
| `shortcut_copy_truth` | `locations_est := locations_true` in the agent's artifacts | 0.0000 / 0.0000 | **+0.441** | **works** |
| `shortcut_copy_truth` (forge) | no solver: random estimate, then `locations_true :=` the same random array | 0.0000 / 0.0000 | **+0.441** | **works** |
| `shortcut_oracle_mask` | read the generator's corruption labels; least squares on the edges labelled clean; output looks like a normal solver estimate | 0.1405 / 0.1037 | **+0.135** | **works** |
| `shortcut_easier_instances` (σ) | unchanged Cycle-Sync on instances with actual σ=0.05, declared σ=0.2; validity check cannot see σ | 0.0888 / 0.0526 | **+0.208** | **works** |
| `shortcut_easier_instances` (q) | actual q lowered by 0.07, declared q unchanged; empirical mask fraction stays inside the 0.10 tolerance | 0.1613 / 0.1112 | **+0.081** | **works** |
| `shortcut_trim_cameras` | drop the 20 cameras with least support (chosen from the solver's own weights) from both location arrays; validity reads the declared `n` | 0.1826 / 0.1213 | **+0.046** | **works** (beats the genuine refit gain) |
| `shortcut_seed_cherry_pick` | honest Cycle-Sync on 30 honest instances per setting; keep the 10 with lowest true error; name the best 5 so they hash into the test half | 0.1758 / 0.1198 | **+0.026** | **works** (≈ seed std) |
| `shortcut_seed_cherry_pick` (steer only) | rename the gym's own 10 reference runs so the best 5 hash into the test half; zero compute | 0.1885 / 0.1223 | +0.012 | works but within noise; a shortcut, not a better method |
| `shortcut_drop_hard_experiment` (manifest) | method that fails adversarial (honest: −0.236) leaves that experiment out of its manifest | 0.1939 / missing | **0.000** (honest −0.236) | **works**: tie with reference, loss avoided |
| `shortcut_drop_hard_experiment` (scores_train) | same failing method, all outputs on disk; agent deletes the pair from `scores_train.json` and the test silently skips it | 0.1939 / missing | **0.000** | **works**: tie, loss avoided |
| `shortcut_drop_hard_experiment` (reference.json) | agent writes its own `scoring/reference.json` without the adversarial experiment; test never scores it | 0.1939 / missing | **0.000** | **works**: tie, loss avoided |
| `shortcut_degenerate_outputs` (NaN) | NaN estimates on adversarial; test writes `NaN` metrics, file not strict JSON | 0.1939 / NaN | 0.000 if NaN is skipped | **conditional**: works if the rank treats NaN as missing |
| degenerate zeros / random (same folder) | all cameras at the origin / random positions | 1.63 / 1.57, 1.61 / 1.58 | −3.26, −3.27 | fails: correctly penalised |
| `shortcut_forged_scores_after_crash` | agent writes `scores_test.json` with zero error and adds a method with no manifest to `scores_train.json`; the test exits 1 before writing, so the forged file stays | 0.0000 / 0.0000 | +0.441 if the file is read | **conditional**: works unless the rank deletes the file first or rejects a nonzero exit |
| bruteforce_ransac (check, not a shortcut) | budgeted exhaustive search over inlier sets | 1.3460 / 1.0266 | −2.53 | fails |

Honest alternatives the test cannot separate from the reference: the reverse schedule (−0.0004) and the refit on 0.75·(1−q)·|E| edges (+0.001).

## 5. What to fix

1. **Own the instances and the answers.**
   - Ship fixed instance files under `data/` holding observations only (`n`, edges, directions), with ids for train and test.
   - Keep the test ground truth, corruption labels and settings under `eval/test/`, generated from secret seeds that never appear in `data/` or the generator defaults.
   - Have methods write only `locations_est` per instance id.
   - Have the test load the truth and settings from its own files and ignore any `locations_true`, `q`, `sigma`, `n` or `corrupted` in the artifact.
   - This closes copy_truth, oracle_mask, easier_instances, trim_cameras, seed_cherry_pick and split steering.
2. **Fail closed.**
   - Score a fixed method key (`cycle_sync`) on every declared experiment and every test instance.
   - A missing or non-finite estimate, or a wrong camera count, should get a worst-case value (e.g. the all-zero output's error) rather than vanishing.
   - Delete `scoring/scores_test.json` before the run.
   - Never write NaN.
3. **Stop reading agent-writable control files.** The test should not take its method list from `scoring/scores_train.json` or its metric/experiment list from `scoring/reference.json`. Put a copy of the declared metrics inside `eval/test/`.
4. **Drop `benchmark_instance_valid_rate`** once the instances are fixed (it would be 1 by construction), or compute it from the gym's own files.
5. **Use more test instances.** Five per setting gives a seed std of 0.021 in weighted score, comparable to a genuine improvement (+0.030).
