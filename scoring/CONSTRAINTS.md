# Scientist Constraints

## Data and Problem Instances
Use the synthetic camera-location generator in `data/synthetic.py` with the same experiment settings named in `scoring/reference.json`: Erdos-Renyi graph probability `p=0.5`, Gaussian 3D camera locations, and the specified corruption type, corruption probability, and noise level for each experiment. Do not replace these with easier synthetic patterns, real SfM scenes, or additional external data when reporting the benchmark score.

## Evaluation
Evaluate only saved output artifacts through `scripts/evaluate.sh`. Do not alter `eval/` to import the submitted method, regenerate outputs, change the alignment metric, or filter failed trials after the fact.

## Resource Scale
Use the same number of cameras and trials as the benchmark script for comparable scores. Increasing graph density, reducing corruption, reducing noise, or cherry-picking seeds is not a valid improvement.

## Compliance Checklist
- [ ] Experiments use the named settings from `scoring/reference.json`
- [ ] Evaluation reads saved artifacts and does not call method code
- [ ] No external data, pretrained models, or easier generated data are used
- [ ] Camera count, graph density, corruption probability, noise level, and trial count are unchanged
