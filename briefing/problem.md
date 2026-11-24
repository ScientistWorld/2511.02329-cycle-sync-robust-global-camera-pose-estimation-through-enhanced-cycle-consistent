# Problem Definition

## Research Question

Recover absolute 3D camera locations from a measurement graph whose edges contain pairwise unit direction observations between cameras. The recovered locations are identifiable only up to a global translation and scale, so the task is to estimate the relative camera configuration.

## Inputs and Outputs

Each problem instance provides:
- `n` cameras.
- An undirected viewing graph over the cameras.
- A unit direction vector for each graph edge.

A solver must output one 3D location per camera. It sees only these observations: no ground-truth locations, corruption labels, inter-camera distances or image measurements are available.

## Difficulty

The benchmark stresses high outlier rates, noisy clean directions, missing graph edges, and variable inter-camera distances. In one setting most directions are independent random outliers; in the other, almost half of the directions are outliers generated from an internally consistent but wrong camera configuration, which makes them hard to tell apart from the true structure. Even the clean directions carry angular noise.

## Success Criteria

A successful solution has low aligned camera-location error across many independent instances, in both the typical camera and the worst-placed cameras, and remains stable under severe corruption.
