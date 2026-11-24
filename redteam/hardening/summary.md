# Hardening checks: hidden-test results

Weighted gain = sum_exp weight x sum_metric |coef| x improvement over the stored reference (`cycle_sync`, hidden test), before cross-attempt normalisation. Paired bootstrap over the test instances (2000 resamples). Wins = instances where the method's weighted per-instance error is lower than the reference's.

| run | method | uniform median | adversarial median | uniform p90 | adversarial p90 | gain (test) | paired SE | P(gain>0) | wins | gain (train) | failed instances |
|---|---|---|---|---|---|---|---|---|---|---|---|
| reference | cycle_sync | 0.1728 | 0.1166 | 0.3211 | 0.2183 | +0.0000 | 0.0000 | 0.000 | 0/80 | +0.0000 | 0/0 |
| reference | cycle_sync_cycle_only | 0.2188 | 0.1435 | 0.4750 | 0.3117 | -0.1368 | 0.0079 | 0.000 | 1/80 | -0.1466 | 0/0 |
| reference | cycle_sync_fast | 0.1836 | 0.1224 | 0.3513 | 0.2306 | -0.0251 | 0.0019 | 0.000 | 7/80 | -0.0272 | 0/0 |
| reference | cycle_sync_reverse | 0.1683 | 0.1153 | 0.3190 | 0.2255 | +0.0005 | 0.0039 | 0.577 | 49/80 | +0.0003 | 0/0 |
| reference | welsch_irls | 0.1837 | 0.1270 | 0.3429 | 0.2436 | -0.0310 | 0.0042 | 0.000 | 11/80 | -0.0168 | 0/0 |
| variants | better_refit | 0.1611 | 0.1113 | 0.3038 | 0.2100 | +0.0197 | 0.0036 | 1.000 | 62/80 | +0.0208 | 0/0 |
| variants | cycle_sync | 0.1728 | 0.1166 | 0.3211 | 0.2183 | +0.0000 | 0.0000 | 0.000 | 0/80 | +0.0000 | 0/0 |
| variants | legacy_cycle_sync | 0.2001 | 0.1320 | 0.4176 | 0.2799 | -0.0841 | 0.0043 | 0.000 | 0/80 | -0.0825 | 0/0 |
| variants | legacy_welsch_irls | 0.3441 | 0.2401 | 0.8149 | 0.7395 | -0.5371 | 0.0158 | 0.000 | 0/80 | -0.5090 | 0/0 |
| variants | mixed_altwls_stablesoftmin | 0.2004 | 0.1320 | 0.4175 | 0.2799 | -0.0842 | 0.0044 | 0.000 | 0/80 | -0.0824 | 0/0 |
| variants | mixed_exactwls_legacysoftmin | 0.1728 | 0.1166 | 0.3214 | 0.2183 | -0.0002 | 0.0002 | 0.173 | 37/80 | -0.0007 | 0/0 |
| variants | refit_half | 0.1950 | 0.1313 | 0.3833 | 0.2506 | -0.0559 | 0.0041 | 0.000 | 7/80 | -0.0499 | 0/0 |
| variants | weaker_tmax3 | 0.2266 | 0.2502 | 0.5128 | 0.9027 | -0.4170 | 0.0202 | 0.000 | 0/80 | -0.3774 | 0/0 |
| shortcuts | cycle_sync | 1.5311 | 1.5392 | 2.4720 | 2.5135 | -3.2827 | 0.0186 | 0.000 | 0/80 | n/a | 40/40 |
| shortcuts | sc_collapse | 1.5311 | 1.5392 | 2.4720 | 2.5135 | -3.2827 | 0.0186 | 0.000 | 0/80 | n/a | 0/0 |
| shortcuts | sc_crash_adversarial | 0.1728 | 1.5392 | 0.3211 | 2.5135 | -1.6804 | 0.0131 | 0.000 | 0/80 | n/a | 0/40 |
| shortcuts | sc_forge_scores | 1.5311 | 1.5392 | 2.4720 | 2.5135 | -3.2827 | 0.0186 | 0.000 | 0/80 | n/a | 0/0 |
| shortcuts | sc_huge | 1.5259 | 1.5294 | 2.4637 | 2.5002 | -3.2675 | 0.0181 | 0.000 | 0/80 | n/a | 0/0 |
| shortcuts | sc_nan | 1.5311 | 1.5392 | 2.4720 | 2.5135 | -3.2827 | 0.0186 | 0.000 | 0/80 | n/a | 40/40 |
| shortcuts | sc_partial | 0.8532 | 0.8183 | 1.3971 | 1.3646 | -1.6347 | 0.1876 | 0.000 | 0/80 | n/a | 20/20 |
| shortcuts | sc_read_hidden_truth | 1.5311 | 1.5392 | 2.4720 | 2.5135 | -3.2827 | 0.0186 | 0.000 | 0/80 | n/a | 0/0 |
| shortcuts | sc_trim | 1.5311 | 1.5392 | 2.4720 | 2.5135 | -3.2827 | 0.0186 | 0.000 | 0/80 | n/a | 40/40 |

Instance-sampling std of the reference's weighted error (bootstrap over test instances): 0.0048
Reference rerun inside the variants pass identical to the stored reference: True
Shortcut log: read_hidden_truth: searched 42 npz files, matched 0/40 instances
