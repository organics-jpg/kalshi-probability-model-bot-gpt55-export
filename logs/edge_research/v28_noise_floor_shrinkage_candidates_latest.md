# v28 Noise-Floor Shrinkage Candidates

Research-only FV candidates. The model keeps raw v28 direction but shrinks confidence toward 50 in noisy physical states.

| rank | policy | entries | settled | W/L | coverage | net c | avg c | brier | boot p10 | boot p>0 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | noise_shrink_rmt_recency_p50_edge0 | 147 | 147 | 88/59 | 81.21546961325967 | 1233.0 | 8.387755102040817 | 0.23150507721482877 | -289.0 | 0.8505 |
| 2 | noise_shrink_rmt_recency_p50_edge1 | 136 | 136 | 78/58 | 75.13812154696133 | 832.0 | 6.117647058823529 | 0.23947440792589234 | -527.0 | 0.7845 |
| 3 | noise_shrink_light_p50_edge1 | 168 | 168 | 106/62 | 92.81767955801105 | 812.0 | 4.833333333333333 | 0.20926054614098494 | -634.0 | 0.7665 |
| 4 | noise_shrink_full_p50_edge0 | 136 | 136 | 77/59 | 75.13812154696133 | 786.0 | 5.779411764705882 | 0.2369739343349383 | -650.0 | 0.7525 |
| 5 | noise_shrink_rmt_recency_p52_edge0 | 132 | 132 | 81/51 | 72.92817679558011 | 781.0 | 5.916666666666667 | 0.2217768094262941 | -582.0 | 0.7585 |
| 6 | noise_shrink_weakraw_rmt_memory_p50_edge1 | 170 | 170 | 109/61 | 93.92265193370166 | 725.0 | 4.264705882352941 | 0.20134718376916153 | -817.0 | 0.7275 |
| 7 | noise_shrink_weakraw_rmt_repetition_p50_edge1 | 170 | 170 | 108/62 | 93.92265193370166 | 553.0 | 3.2529411764705882 | 0.20251471555196182 | -949.0 | 0.6765 |
| 8 | noise_shrink_light_p50_edge0 | 171 | 171 | 106/65 | 94.47513812154696 | 465.0 | 2.719298245614035 | 0.21299888825713856 | -1062.0 | 0.655 |
| 9 | v28_raw_p50_edge1 | 172 | 172 | 105/67 | 95.02762430939227 | 455.0 | 2.645348837209302 | 0.21982865631358722 | -1108.0 | 0.64 |
| 10 | noise_shrink_full_p50_edge1 | 122 | 122 | 66/56 | 67.40331491712708 | 371.0 | 3.040983606557377 | 0.23766259110872867 | -1019.0 | 0.6365 |
| 11 | noise_shrink_weakraw_rmt_repetition_p50_edge0 | 171 | 171 | 105/66 | 94.47513812154696 | 237.0 | 1.3859649122807018 | 0.21293982686476756 | -1308.0 | 0.587 |
| 12 | noise_shrink_weakraw_rmt_memory_p50_edge0 | 171 | 171 | 105/66 | 94.47513812154696 | 215.0 | 1.2573099415204678 | 0.21263517686368566 | -1332.0 | 0.5745 |

## Penalty Attribution

### noise_shrink_rmt_recency_p50_edge0
- `near_strike`: count `124`, settled `124`, W/L `68/56`, net `901.0c`, avg raw/p `0.5680886774193548/0.5544489918571579`
- `recross`: count `147`, settled `147`, W/L `88/59`, net `1233.0c`, avg raw/p `0.6066162653061224/0.585140749107198`
- `stale`: count `51`, settled `51`, W/L `31/20`, net `484.0c`, avg raw/p `0.602362705882353/0.5772826203938525`
- `rmt_noise`: count `143`, settled `143`, W/L `86/57`, net `1406.0c`, avg raw/p `0.6041795244755245/0.58210329453677`
- `repetition`: count `71`, settled `71`, W/L `49/22`, net `1509.0c`, avg raw/p `0.6290193098591549/0.5981366339524344`

### noise_shrink_rmt_recency_p50_edge1
- `near_strike`: count `118`, settled `118`, W/L `63/55`, net `699.0c`, avg raw/p `0.5678329237288136/0.5535500400621134`
- `recross`: count `136`, settled `136`, W/L `78/58`, net `832.0c`, avg raw/p `0.6010013823529412/0.5802858778669108`
- `stale`: count `50`, settled `50`, W/L `29/21`, net `365.0c`, avg raw/p `0.5933231800000001/0.5695989890002935`
- `rmt_noise`: count `132`, settled `132`, W/L `76/56`, net `1005.0c`, avg raw/p `0.5981914318181818/0.5768481847719686`
- `repetition`: count `71`, settled `71`, W/L `46/25`, net `1178.0c`, avg raw/p `0.6185685774647887/0.5896013683404883`
- `late`: count `1`, settled `1`, W/L `0/1`, net `-106.0c`, avg raw/p `0.532243/0.5213044894067687`

### noise_shrink_light_p50_edge1
- `near_strike`: count `112`, settled `112`, W/L `57/55`, net `42.0c`, avg raw/p `0.5749031517857143/0.5598216120257731`
- `recross`: count `168`, settled `168`, W/L `106/62`, net `810.0c`, avg raw/p `0.6582045595238095/0.6433432375552848`
- `stale`: count `66`, settled `66`, W/L `45/21`, net `640.0c`, avg raw/p `0.662659409090909/0.6453337852253093`
- `rmt_noise`: count `164`, settled `164`, W/L `104/60`, net `989.0c`, avg raw/p `0.6568048353658537/0.6417638034527618`
- `repetition`: count `100`, settled `100`, W/L `70/30`, net `1086.0c`, avg raw/p `0.68785712/0.6729439301128621`

### noise_shrink_full_p50_edge0
- `near_strike`: count `118`, settled `118`, W/L `61/57`, net `466.0c`, avg raw/p `0.5619070762711865/0.5364560190203218`
- `recross`: count `136`, settled `136`, W/L `77/59`, net `786.0c`, avg raw/p `0.5971420147058824/0.5648399381327218`
- `stale`: count `50`, settled `50`, W/L `29/21`, net `430.0c`, avg raw/p `0.58613244/0.5520583619855773`
- `rmt_noise`: count `132`, settled `132`, W/L `75/57`, net `959.0c`, avg raw/p `0.5942151136363637/0.5611026646214968`
- `repetition`: count `73`, settled `73`, W/L `46/27`, net `998.0c`, avg raw/p `0.6162050136986301/0.5762342415078987`
- `late`: count `1`, settled `1`, W/L `0/1`, net `-106.0c`, avg raw/p `0.532243/0.5123805846032222`

## Interpretation

- This is a discovery diagnostic, not a promotion gate.
- A useful candidate must keep roughly 75-80% coverage, improve Brier or net against raw v28, and then survive frozen forward validation.
