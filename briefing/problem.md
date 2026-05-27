# Problem Definition

## Research Question

Recover absolute 3D camera locations from a measurement graph whose edges contain pairwise unit direction observations between cameras. The recovered locations are identifiable only up to a global translation and scale, so the task is to estimate the relative camera configuration.

## Inputs and Outputs

Each problem instance provides:
- `n` cameras.
- An undirected viewing graph over the cameras.
- A unit direction vector for each graph edge.

A solver must output one 3D location per camera. It must not use ground-truth locations, hidden corruption labels, inter-camera distances, image measurements, or any information not present in the benchmark artifact.

## Difficulty

The benchmark stresses high outlier rates, noisy clean directions, missing graph edges, and variable inter-camera distances. Some outliers are independent random directions, while others are generated from an internally consistent but wrong camera configuration.

## Success Criteria

A successful solution has low aligned camera-location error across multiple trials, remains stable under severe corruption, and preserves the benchmark settings for camera count, graph density, noise level, corruption model, and corruption rate.
