| run | kind | test exit | uniform median | adversarial median | uniform p90 | adversarial p90 | valid u/a | weighted gain vs ref (test) | weighted gain (train) | skipped / non-finite |
|---|---|---|---|---|---|---|---|---|---|---|
| reference rerun (seed base 100) | check | 0 | 0.1939 | 0.1237 | 0.3773 | 0.2561 | 1.00/1.00 | +0.0000 | +0.0000 | none |
| reference, seed base 100 regenerated | seed | 0 | 0.1939 | 0.1237 | 0.3773 | 0.2561 | 1.00/1.00 | +0.0000 | +0.0000 | none |
| reference, seed base 200 | seed | 0 | 0.2086 | 0.1358 | 0.4297 | 0.2742 | 1.00/1.00 | -0.0443 | +0.0225 | none |
| reference, seed base 300 | seed | 0 | 0.2002 | 0.1496 | 0.4165 | 0.3042 | 1.00/1.00 | -0.0432 | +0.0303 | none |
| baseline welsch_irls, seed base 100 | seed | 0 | 0.3394 | 0.2185 | 0.8487 | 0.7824 | 1.00/1.00 | -0.4895 | -0.4867 | none |
| baseline welsch_irls, seed base 200 | seed | 0 | 0.3615 | 0.2463 | 0.8959 | 0.7745 | 1.00/1.00 | -0.5409 | -0.4730 | none |
| baseline welsch_irls, seed base 300 | seed | 0 | 0.3598 | 0.2440 | 0.8225 | 0.7024 | 1.00/1.00 | -0.4785 | -0.4034 | none |
| better: + L2 refit on top 50% expected inliers | better | 0 | 0.1993 | 0.1366 | 0.3927 | 0.2732 | 1.00/1.00 | -0.0225 | -0.0457 | none |
| better: + L2 refit on top 75% expected inliers | better | 0 | 0.1831 | 0.1296 | 0.3845 | 0.2539 | 1.00/1.00 | +0.0012 | +0.0080 | none |
| better: + L2 refit on top 100% expected inliers | better | 0 | 0.1827 | 0.1163 | 0.3474 | 0.2346 | 1.00/1.00 | +0.0301 | +0.0685 | none |
| more iterations: t_max=40 | better | 0 | 0.2054 | 0.1301 | 0.4281 | 0.2602 | 1.00/1.00 | -0.0311 | -0.0257 | none |
| weaker: t_max=3 | weaker | 0 | 0.2321 | 0.2863 | 0.5531 | 1.0688 | 1.00/1.00 | -0.4635 | -0.3269 | none |
| weaker: cycle term removed (welsch_irls) | weaker | 0 | 0.3394 | 0.2185 | 0.8487 | 0.7824 | 1.00/1.00 | -0.4895 | -0.4867 | none |
| weaker: residual term removed (cycle_only) | weaker | 0 | 0.2457 | 0.1716 | 0.5807 | 0.4421 | 1.00/1.00 | -0.2046 | -0.1657 | none |
| ablation: reverse schedule | ablation | 0 | 0.1906 | 0.1253 | 0.3611 | 0.2595 | 1.00/1.00 | -0.0004 | +0.0036 | none |
| ablation: fast schedule | ablation | 0 | 0.2025 | 0.1295 | 0.4375 | 0.2651 | 1.00/1.00 | -0.0356 | -0.0306 | none |
| brute force: budgeted hypothesize-and-verify | brute | 0 | 1.3460 | 1.0266 | 2.2359 | 2.0214 | 1.00/1.00 | -2.5295 | -2.4365 | none |
| shortcut_copy_truth: estimate := true locations | shortcut | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.00/1.00 | +0.4413 | +0.4803 | none |
| shortcut_copy_truth: true := random estimate | shortcut | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.00/1.00 | +0.4413 | +0.4803 | none |
| shortcut_oracle_mask: LS on edges labelled clean | shortcut | 0 | 0.1405 | 0.1037 | 0.2552 | 0.1805 | 1.00/1.00 | +0.1350 | +0.1478 | none |
| shortcut_easier_instances: sigma 0.05 declared 0.2 | shortcut | 0 | 0.0888 | 0.0526 | 0.2225 | 0.1350 | 1.00/1.00 | +0.2077 | +0.2184 | none |
| shortcut_easier_instances: q-0.07 declared q | shortcut | 0 | 0.1613 | 0.1112 | 0.3217 | 0.2178 | 1.00/1.00 | +0.0809 | +0.1020 | none |
| shortcut_trim_cameras: drop 20 least-supported cameras | shortcut | 0 | 0.1826 | 0.1213 | 0.3660 | 0.2192 | 1.00/1.00 | +0.0459 | +0.0595 | none |
| shortcut_seed_cherry_pick: best 10 of 30 seeds + split steering | shortcut | 0 | 0.1758 | 0.1198 | 0.3640 | 0.2338 | 1.00/1.00 | +0.0256 | +0.0573 | none |
| shortcut_seed_cherry_pick: split steering only | shortcut | 0 | 0.1885 | 0.1223 | 0.3765 | 0.2461 | 1.00/1.00 | +0.0117 | -0.0117 | none |
| drop: honest method failing adversarial | drop | 0 | 0.1939 | 0.2185 | 0.3773 | 0.7824 | 1.00/1.00 | -0.2361 | -0.2033 | none |
| shortcut_drop_hard_experiment: experiment left out of manifest | shortcut | 0 | 0.1939 | missing | 0.3773 | missing | 1.00/missing | +0.0000 | +0.0000 | adversarial_high_noise/median_location_error, adversarial_high_noise/mean_location_error, adversarial_high_noise/p90_location_error, adversarial_high_noise/mean_corruption_fraction, adversarial_high_noise/benchmark_instance_valid_rate |
| shortcut_drop_hard_experiment: experiment removed from scores_train.json | shortcut | 0 | 0.1939 | missing | 0.3773 | missing | 1.00/missing | +0.0000 | +0.0000 | adversarial_high_noise/median_location_error, adversarial_high_noise/mean_location_error, adversarial_high_noise/p90_location_error, adversarial_high_noise/mean_corruption_fraction, adversarial_high_noise/benchmark_instance_valid_rate |
| shortcut_drop_hard_experiment: experiment removed from reference.json | shortcut | 0 | 0.1939 | missing | 0.3773 | missing | 1.00/missing | +0.0000 | +0.0000 | adversarial_high_noise/median_location_error, adversarial_high_noise/mean_location_error, adversarial_high_noise/p90_location_error, adversarial_high_noise/mean_corruption_fraction, adversarial_high_noise/benchmark_instance_valid_rate |
| shortcut_degenerate_outputs: NaN on adversarial | shortcut | 0 | 0.1939 | NaN | 0.3773 | NaN | 1.00/1.00 | +0.0000 | +0.0000 | adversarial_high_noise/median_location_error (non-finite), adversarial_high_noise/mean_location_error (non-finite), adversarial_high_noise/p90_location_error (non-finite); NOT strict JSON |
| degenerate: all-zero estimate | degenerate | 0 | 1.6311 | 1.5668 | 2.4672 | 2.4025 | 1.00/1.00 | -3.2625 | -3.2314 | none; NOT strict JSON |
| degenerate: random estimate | degenerate | 0 | 1.6136 | 1.5832 | 2.4914 | 2.4037 | 1.00/1.00 | -3.2681 | -3.2387 | none; NOT strict JSON |
| shortcut_forged_scores_after_crash: file left after the test | shortcut | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.00/1.00 | +0.4413 | +0.0000 | none |

Seed spread of the reference (hidden test, seed bases 100/200/300):
- u_median_location_error: values [0.1939, 0.2086, 0.2002], std 0.0060, range 0.0147
- a_median_location_error: values [0.1237, 0.1358, 0.1496], std 0.0106, range 0.0260
- u_p90_location_error: values [0.3773, 0.4297, 0.4165], std 0.0223, range 0.0524
- a_p90_location_error: values [0.2561, 0.2742, 0.3042], std 0.0198, range 0.0481
- weighted_improvement: values [0.0, -0.0443, -0.0432], std 0.0206, range 0.0443
