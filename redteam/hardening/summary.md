# Hardening checks: hidden-test results

Weighted gain = sum_exp weight x sum_metric |coef| x improvement over the stored reference (`cycle_sync`, hidden test), before cross-attempt normalisation. Paired bootstrap over the test instances (2000 resamples). Wins = instances where the method's weighted per-instance error is lower than the reference's.

| run | method | uniform median | adversarial median | uniform p90 | adversarial p90 | gain (test) | paired SE | P(gain>0) | wins | gain (train) | failed instances |
|---|---|---|---|---|---|---|---|---|---|---|---|
| reference | cycle_sync | 0.2832 | 0.2041 | 0.5866 | 0.4076 | +0.0000 | 0.0000 | 0.000 | 0/80 | +0.0000 | 0/0 |
| reference | cycle_sync_cycle_only | 0.3442 | 0.2301 | 0.7852 | 0.5147 | -0.1618 | 0.0113 | 0.000 | 1/80 | -0.1449 | 0/0 |
| reference | cycle_sync_fast | 0.2969 | 0.2070 | 0.6202 | 0.4175 | -0.0255 | 0.0034 | 0.000 | 14/80 | -0.0309 | 0/0 |
| reference | cycle_sync_residual_only | 0.3331 | 0.2496 | 0.6417 | 0.4928 | -0.1096 | 0.0068 | 0.000 | 1/80 | -0.1165 | 0/0 |
| reference | cycle_sync_reverse | 0.2866 | 0.2084 | 0.5757 | 0.4330 | -0.0107 | 0.0051 | 0.008 | 31/80 | -0.0033 | 0/0 |
| reference | lud | 0.6073 | 0.7041 | 1.1417 | 1.3059 | -1.0133 | 0.0131 | 0.000 | 0/80 | -1.0526 | 0/0 |
| reference | welsch_irls | 0.3395 | 0.2616 | 0.6392 | 0.5185 | -0.1256 | 0.0064 | 0.000 | 2/80 | -0.1677 | 0/0 |
| variants | better_refit | 0.2475 | 0.1536 | 0.5281 | 0.3239 | +0.1023 | 0.0038 | 1.000 | 79/80 | +0.1016 | 0/0 |
| variants | better_refit80 | 0.2724 | 0.1772 | 0.5852 | 0.3852 | +0.0318 | 0.0036 | 1.000 | 66/80 | +0.0407 | 0/0 |
| variants | cycle_sync | 0.2832 | 0.2041 | 0.5866 | 0.4076 | +0.0000 | 0.0000 | 0.000 | 0/80 | +0.0000 | 0/0 |
| variants | legacy_cycle_sync | 0.2900 | 0.2125 | 0.6167 | 0.4357 | -0.0269 | 0.0048 | 0.000 | 18/80 | +0.0107 | 0/0 |
| variants | legacy_welsch_irls | 0.4351 | 0.3344 | 0.9098 | 0.7770 | -0.4152 | 0.0113 | 0.000 | 0/80 | -0.4575 | 0/0 |
| variants | prev_taab_clip | 0.2816 | 0.2048 | 0.5781 | 0.4097 | +0.0061 | 0.0038 | 0.943 | 44/80 | +0.0368 | 0/0 |
| variants | weaker_tmax3 | 0.3410 | 0.2751 | 0.7114 | 0.6900 | -0.2221 | 0.0136 | 0.000 | 2/80 | -0.2627 | 0/0 |
| shortcuts | cycle_sync | 1.5192 | 1.5174 | 2.4832 | 2.4541 | -2.9620 | 0.0154 | 0.000 | 0/80 | n/a | 40/40 |
| shortcuts | sc_collapse | 1.5192 | 1.5174 | 2.4832 | 2.4541 | -2.9620 | 0.0154 | 0.000 | 0/80 | n/a | 0/0 |
| shortcuts | sc_crash_adversarial | 0.2832 | 1.5174 | 0.5866 | 2.4541 | -1.5281 | 0.0119 | 0.000 | 0/80 | n/a | 0/40 |
| shortcuts | sc_forge_scores | 1.5192 | 1.5174 | 2.4832 | 2.4541 | -2.9620 | 0.0154 | 0.000 | 0/80 | n/a | 0/0 |
| shortcuts | sc_huge | 1.5102 | 1.5126 | 2.4699 | 2.4366 | -2.9444 | 0.0154 | 0.000 | 0/80 | n/a | 0/0 |
| shortcuts | sc_nan | 1.5192 | 1.5174 | 2.4832 | 2.4541 | -2.9620 | 0.0154 | 0.000 | 0/80 | n/a | 40/40 |
| shortcuts | sc_partial | 0.9014 | 0.8596 | 1.5318 | 1.4285 | -1.4789 | 0.1697 | 0.000 | 0/80 | n/a | 20/20 |
| shortcuts | sc_read_hidden_truth | 1.5192 | 1.5174 | 2.4832 | 2.4541 | -2.9620 | 0.0154 | 0.000 | 0/80 | n/a | 0/0 |
| shortcuts | sc_trim | 1.5192 | 1.5174 | 2.4832 | 2.4541 | -2.9620 | 0.0154 | 0.000 | 0/80 | n/a | 40/40 |

Instance-sampling std of the reference's weighted error (bootstrap over test instances): 0.0080
Reference rerun inside the variants pass identical to the stored reference: True
Shortcut log: read_hidden_truth: searched 42 npz files, matched 0/40 instances
