# Exploration results (public seeds)

## eq9 / uniform_high_noise

| solver | median | mean | p90 | weighted cost | gain vs cs_authgeo | paired SE | wins |
|---|---|---|---|---|---|---|---|
| cs_gym | 0.1753 | 0.2032 | 0.3295 | 0.4543 | +0.0026 | 0.0027 | 9/16 |
| cs_authgeo | 0.1745 | 0.2085 | 0.3317 | 0.4569 | +0.0000 | 0.0000 | 0/16 |
| cs_authfull | 0.1743 | 0.2062 | 0.3308 | 0.4552 | +0.0017 | 0.0023 | 10/16 |
| lud | 0.5549 | 0.6276 | 1.1018 | 1.4670 | -1.0101 | 0.0305 | 0/16 |
| lam0_gym | 0.1825 | 0.2042 | 0.3293 | 0.4618 | -0.0049 | 0.0087 | 5/16 |
| lam0_authgeo | 0.1817 | 0.2175 | 0.3411 | 0.4733 | -0.0164 | 0.0093 | 5/16 |
| irls_uniform | 0.1818 | 0.2036 | 0.3261 | 0.4589 | -0.0020 | 0.0094 | 6/16 |
| ls_unweighted | 0.8071 | 0.8805 | 1.4567 | 2.0334 | -1.5764 | 0.0355 | 0/16 |
| reverse_authgeo | 0.1715 | 0.2012 | 0.3180 | 0.4427 | +0.0142 | 0.0062 | 12/16 |
| cycleonly_authgeo | 0.2143 | 0.2708 | 0.4443 | 0.5892 | -0.1323 | 0.0111 | 0/16 |
| fast_authgeo | 0.1834 | 0.2174 | 0.3480 | 0.4791 | -0.0222 | 0.0048 | 2/16 |
| uniforminit_authgeo | 0.1761 | 0.2028 | 0.3256 | 0.4526 | +0.0043 | 0.0029 | 7/16 |
| tmax3_authgeo | 0.2196 | 0.2709 | 0.4593 | 0.6035 | -0.1466 | 0.0169 | 0/16 |
| tmax40_authgeo | 0.1875 | 0.2229 | 0.3540 | 0.4890 | -0.0321 | 0.0046 | 0/16 |
| oracle_clean_ls | 0.1311 | 0.1425 | 0.2347 | 0.3289 | +0.1280 | 0.0091 | 16/16 |
| refit100_cs_authgeo | 0.1626 | 0.1971 | 0.3133 | 0.4294 | +0.0275 | 0.0046 | 15/16 |
| refit80_cs_authgeo | 0.1736 | 0.2088 | 0.3382 | 0.4601 | -0.0031 | 0.0061 | 8/16 |
| refit100_cs_gym | 0.1625 | 0.1899 | 0.3071 | 0.4227 | +0.0342 | 0.0045 | 16/16 |
| refit80_cs_gym | 0.1722 | 0.2036 | 0.3331 | 0.4536 | +0.0033 | 0.0059 | 9/16 |

diagnostics (mean over instances): final_precision_cs_authfull=0.902, final_precision_cs_authgeo=0.901, final_precision_cs_gym=0.903, final_precision_cycleonly_authgeo=0.860, final_precision_fast_authgeo=0.891, final_precision_irls_uniform=0.905, final_precision_lam0_authgeo=0.902, final_precision_lam0_gym=0.905, final_precision_lud=0.753, final_precision_reverse_authgeo=0.917, final_precision_tmax3_authgeo=0.887, final_precision_tmax40_authgeo=0.889, final_precision_uniforminit_authgeo=0.903, init_precision_authfull=0.644, init_precision_authgeo=0.665, init_precision_gym=0.653
seconds per instance: cs_authfull=0.26, cs_authgeo=0.29, cs_gym=0.29, cycleonly_authgeo=0.27, fast_authgeo=0.31, irls_uniform=0.18, lam0_authgeo=0.17, lam0_gym=0.18, ls_unweighted=0.00, lud=0.09, oracle_clean_ls=0.02, refit100_cs_authgeo=0.01, refit100_cs_gym=0.01, refit80_cs_authgeo=0.01, refit80_cs_gym=0.02, reverse_authgeo=0.27, taab_authfull=0.01, taab_authgeo=0.01, taab_gym=0.02, tmax3_authgeo=0.05, tmax40_authgeo=0.46, uniforminit_authgeo=0.32

## eq9 / adversarial_high_noise

| solver | median | mean | p90 | weighted cost | gain vs cs_authgeo | paired SE | wins |
|---|---|---|---|---|---|---|---|
| cs_gym | 0.1150 | 0.1891 | 0.2236 | 0.3248 | -0.0004 | 0.0037 | 9/16 |
| cs_authgeo | 0.1161 | 0.1858 | 0.2233 | 0.3244 | +0.0000 | 0.0000 | 0/16 |
| cs_authfull | 0.1169 | 0.1860 | 0.2241 | 0.3257 | -0.0013 | 0.0020 | 8/16 |
| lud | 0.6707 | 0.7574 | 1.2871 | 1.7460 | -1.4215 | 0.0229 | 0/16 |
| lam0_gym | 0.1233 | 0.2051 | 0.3137 | 0.3936 | -0.0692 | 0.0391 | 2/16 |
| lam0_authgeo | 0.1227 | 0.2089 | 0.2955 | 0.3836 | -0.0592 | 0.0265 | 2/16 |
| irls_uniform | 0.1234 | 0.1846 | 0.2322 | 0.3366 | -0.0121 | 0.0111 | 3/16 |
| ls_unweighted | 0.9526 | 1.0574 | 1.7230 | 2.4094 | -2.0850 | 0.0238 | 0/16 |
| reverse_authgeo | 0.1146 | 0.1895 | 0.2212 | 0.3231 | +0.0013 | 0.0039 | 8/16 |
| cycleonly_authgeo | 0.1406 | 0.2270 | 0.2816 | 0.4003 | -0.0759 | 0.0070 | 0/16 |
| fast_authgeo | 0.1218 | 0.1923 | 0.2343 | 0.3393 | -0.0149 | 0.0027 | 1/16 |
| uniforminit_authgeo | 0.1158 | 0.1810 | 0.2102 | 0.3143 | +0.0101 | 0.0087 | 11/16 |
| tmax3_authgeo | 0.1565 | 0.2828 | 0.5229 | 0.5833 | -0.2589 | 0.0578 | 0/16 |
| tmax40_authgeo | 0.1231 | 0.1912 | 0.2257 | 0.3350 | -0.0106 | 0.0083 | 2/16 |
| oracle_clean_ls | 0.0976 | 0.1031 | 0.1647 | 0.2377 | +0.0867 | 0.0188 | 16/16 |
| refit100_cs_authgeo | 0.1103 | 0.1771 | 0.2102 | 0.3073 | +0.0172 | 0.0078 | 15/16 |
| refit80_cs_authgeo | 0.1151 | 0.1849 | 0.2285 | 0.3261 | -0.0017 | 0.0043 | 7/16 |
| refit100_cs_gym | 0.1101 | 0.1810 | 0.2110 | 0.3091 | +0.0154 | 0.0085 | 14/16 |
| refit80_cs_gym | 0.1148 | 0.1885 | 0.2257 | 0.3256 | -0.0012 | 0.0066 | 7/16 |

diagnostics (mean over instances): final_precision_cs_authfull=0.954, final_precision_cs_authgeo=0.955, final_precision_cs_gym=0.952, final_precision_cycleonly_authgeo=0.941, final_precision_fast_authgeo=0.952, final_precision_irls_uniform=0.935, final_precision_lam0_authgeo=0.927, final_precision_lam0_gym=0.929, final_precision_lud=0.767, final_precision_reverse_authgeo=0.948, final_precision_tmax3_authgeo=0.905, final_precision_tmax40_authgeo=0.953, final_precision_uniforminit_authgeo=0.956, init_precision_authfull=0.738, init_precision_authgeo=0.749, init_precision_gym=0.632
seconds per instance: cs_authfull=0.28, cs_authgeo=0.28, cs_gym=0.30, cycleonly_authgeo=0.24, fast_authgeo=0.26, irls_uniform=0.27, lam0_authgeo=0.20, lam0_gym=0.19, ls_unweighted=0.01, lud=0.13, oracle_clean_ls=0.02, refit100_cs_authgeo=0.01, refit100_cs_gym=0.01, refit80_cs_authgeo=0.01, refit80_cs_gym=0.01, reverse_authgeo=0.27, taab_authfull=0.01, taab_authgeo=0.02, taab_gym=0.02, tmax3_authgeo=0.05, tmax40_authgeo=0.57, uniforminit_authgeo=0.27

## authors / uniform_high_noise

| solver | median | mean | p90 | weighted cost | gain vs cs_authgeo | paired SE | wins |
|---|---|---|---|---|---|---|---|
| cs_gym | 0.2729 | 0.3287 | 0.5549 | 0.7374 | +0.0065 | 0.0101 | 8/16 |
| cs_authgeo | 0.2753 | 0.3389 | 0.5551 | 0.7439 | +0.0000 | 0.0000 | 0/16 |
| cs_authfull | 0.2761 | 0.3487 | 0.5814 | 0.7644 | -0.0205 | 0.0079 | 3/16 |
| lud | 0.6132 | 0.6881 | 1.1815 | 1.5973 | -0.8534 | 0.0266 | 0/16 |
| lam0_gym | 0.3337 | 0.3775 | 0.6069 | 0.8488 | -0.1049 | 0.0111 | 0/16 |
| lam0_authgeo | 0.3348 | 0.3976 | 0.6429 | 0.8796 | -0.1358 | 0.0114 | 0/16 |
| irls_uniform | 0.3369 | 0.3830 | 0.6223 | 0.8635 | -0.1197 | 0.0121 | 0/16 |
| ls_unweighted | 0.8453 | 0.9062 | 1.5148 | 2.1166 | -1.3727 | 0.0274 | 0/16 |
| reverse_authgeo | 0.2858 | 0.3518 | 0.5717 | 0.7695 | -0.0256 | 0.0089 | 4/16 |
| cycleonly_authgeo | 0.3305 | 0.4305 | 0.7986 | 0.9818 | -0.2380 | 0.0208 | 0/16 |
| fast_authgeo | 0.2848 | 0.3561 | 0.6072 | 0.7915 | -0.0476 | 0.0092 | 2/16 |
| uniforminit_authgeo | 0.2754 | 0.3330 | 0.5616 | 0.7456 | -0.0017 | 0.0096 | 9/16 |
| tmax3_authgeo | 0.3292 | 0.4164 | 0.7211 | 0.9284 | -0.1845 | 0.0200 | 0/16 |
| tmax40_authgeo | 0.2904 | 0.3581 | 0.6125 | 0.8011 | -0.0573 | 0.0103 | 2/16 |
| oracle_clean_ls | 0.1707 | 0.1922 | 0.3146 | 0.4364 | +0.3075 | 0.0140 | 16/16 |
| refit100_cs_authgeo | 0.2392 | 0.3017 | 0.4986 | 0.6590 | +0.0848 | 0.0084 | 16/16 |
| refit80_cs_authgeo | 0.2527 | 0.3233 | 0.5578 | 0.7167 | +0.0272 | 0.0081 | 12/16 |
| refit100_cs_gym | 0.2392 | 0.2920 | 0.4912 | 0.6507 | +0.0931 | 0.0122 | 16/16 |
| refit80_cs_gym | 0.2552 | 0.3141 | 0.5542 | 0.7133 | +0.0305 | 0.0101 | 13/16 |

diagnostics (mean over instances): final_precision_cs_authfull=0.842, final_precision_cs_authgeo=0.844, final_precision_cs_gym=0.847, final_precision_cycleonly_authgeo=0.784, final_precision_fast_authgeo=0.825, final_precision_irls_uniform=0.863, final_precision_lam0_authgeo=0.857, final_precision_lam0_gym=0.864, final_precision_lud=0.731, final_precision_reverse_authgeo=0.870, final_precision_tmax3_authgeo=0.847, final_precision_tmax40_authgeo=0.824, final_precision_uniforminit_authgeo=0.846, init_precision_authfull=0.610, init_precision_authgeo=0.632, init_precision_gym=0.630
seconds per instance: cs_authfull=0.28, cs_authgeo=0.33, cs_gym=0.27, cycleonly_authgeo=0.25, fast_authgeo=0.25, irls_uniform=0.18, lam0_authgeo=0.16, lam0_gym=0.19, ls_unweighted=0.00, lud=0.07, oracle_clean_ls=0.02, refit100_cs_authgeo=0.01, refit100_cs_gym=0.01, refit80_cs_authgeo=0.01, refit80_cs_gym=0.01, reverse_authgeo=0.26, taab_authfull=0.01, taab_authgeo=0.01, taab_gym=0.02, tmax3_authgeo=0.05, tmax40_authgeo=0.47, uniforminit_authgeo=0.29

## authors / adversarial_high_noise

| solver | median | mean | p90 | weighted cost | gain vs cs_authgeo | paired SE | wins |
|---|---|---|---|---|---|---|---|
| cs_gym | 0.2152 | 0.2703 | 0.4137 | 0.5715 | +0.0165 | 0.0166 | 11/16 |
| cs_authgeo | 0.2154 | 0.2886 | 0.4286 | 0.5880 | +0.0000 | 0.0000 | 0/16 |
| cs_authfull | 0.2142 | 0.2923 | 0.4332 | 0.5911 | -0.0030 | 0.0074 | 6/16 |
| lud | 0.7049 | 0.7865 | 1.3214 | 1.8123 | -1.2243 | 0.0355 | 0/16 |
| lam0_gym | 0.2664 | 0.3417 | 0.5182 | 0.7140 | -0.1259 | 0.0248 | 1/16 |
| lam0_authgeo | 0.2566 | 0.3391 | 0.4884 | 0.6853 | -0.0973 | 0.0099 | 0/16 |
| irls_uniform | 0.2704 | 0.3480 | 0.5287 | 0.7268 | -0.1387 | 0.0270 | 1/16 |
| ls_unweighted | 0.9663 | 1.0460 | 1.7188 | 2.4160 | -1.8279 | 0.0273 | 0/16 |
| reverse_authgeo | 0.2188 | 0.2902 | 0.4233 | 0.5888 | -0.0008 | 0.0053 | 9/16 |
| cycleonly_authgeo | 0.2335 | 0.3135 | 0.4882 | 0.6519 | -0.0639 | 0.0138 | 1/16 |
| fast_authgeo | 0.2177 | 0.2941 | 0.4401 | 0.5994 | -0.0114 | 0.0064 | 3/16 |
| uniforminit_authgeo | 0.2134 | 0.2643 | 0.4141 | 0.5676 | +0.0205 | 0.0168 | 11/16 |
| tmax3_authgeo | 0.2879 | 0.3937 | 0.6721 | 0.8487 | -0.2606 | 0.0421 | 0/16 |
| tmax40_authgeo | 0.2179 | 0.2959 | 0.4386 | 0.5995 | -0.0114 | 0.0062 | 6/16 |
| oracle_clean_ls | 0.1342 | 0.1569 | 0.2601 | 0.3530 | +0.2350 | 0.0143 | 16/16 |
| refit100_cs_authgeo | 0.1622 | 0.2370 | 0.3268 | 0.4531 | +0.1349 | 0.0049 | 16/16 |
| refit80_cs_authgeo | 0.1867 | 0.2672 | 0.4040 | 0.5359 | +0.0521 | 0.0063 | 16/16 |
| refit100_cs_gym | 0.1595 | 0.2172 | 0.3243 | 0.4410 | +0.1471 | 0.0160 | 16/16 |
| refit80_cs_gym | 0.1902 | 0.2500 | 0.3952 | 0.5273 | +0.0607 | 0.0165 | 13/16 |

diagnostics (mean over instances): final_precision_cs_authfull=0.937, final_precision_cs_authgeo=0.939, final_precision_cs_gym=0.943, final_precision_cycleonly_authgeo=0.923, final_precision_fast_authgeo=0.932, final_precision_irls_uniform=0.921, final_precision_lam0_authgeo=0.926, final_precision_lam0_gym=0.925, final_precision_lud=0.762, final_precision_reverse_authgeo=0.947, final_precision_tmax3_authgeo=0.901, final_precision_tmax40_authgeo=0.932, final_precision_uniforminit_authgeo=0.943, init_precision_authfull=0.741, init_precision_authgeo=0.760, init_precision_gym=0.648
seconds per instance: cs_authfull=0.23, cs_authgeo=0.23, cs_gym=0.23, cycleonly_authgeo=0.22, fast_authgeo=0.22, irls_uniform=0.17, lam0_authgeo=0.15, lam0_gym=0.16, ls_unweighted=0.01, lud=0.10, oracle_clean_ls=0.02, refit100_cs_authgeo=0.01, refit100_cs_gym=0.01, refit80_cs_authgeo=0.01, refit80_cs_gym=0.01, reverse_authgeo=0.21, taab_authfull=0.01, taab_authgeo=0.01, taab_gym=0.01, tmax3_authgeo=0.04, tmax40_authgeo=0.42, uniforminit_authgeo=0.24

## noiseless uniform_q08_noiseless (exact recovery = median < 1e-4)

- cs_gym: median errors 1.22e-09, 3.04e-08, 1.59e-09, 4.15e-09, 4.10e-09; exact 5/5
- cs_authgeo: median errors 1.74e-09, 1.83e-08, 2.44e-09, 5.03e-09, 4.44e-09; exact 5/5
- cs_authfull: median errors 5.50e-09, 9.91e-09, 2.45e-09, 6.29e-09, 6.80e-09; exact 5/5
- lud: median errors 8.65e-01, 8.09e-01, 7.64e-01, 7.86e-01, 8.77e-01; exact 0/5

## noiseless adversarial_q04_noiseless (exact recovery = median < 1e-4)

- cs_gym: median errors 1.36e-12, 1.80e-12, 1.05e-12, 5.64e-13, 4.73e-13; exact 5/5
- cs_authgeo: median errors 3.05e-11, 3.55e-12, 1.96e-12, 1.15e-12, 9.25e-13; exact 5/5
- cs_authfull: median errors 2.75e-12, 3.55e-12, 1.96e-12, 1.15e-12, 9.25e-13; exact 5/5
- lud: median errors 2.69e-01, 3.39e-01, 2.93e-01, 3.31e-01, 2.92e-01; exact 0/5

total time 223s
