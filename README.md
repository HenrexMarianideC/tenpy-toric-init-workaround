# Topological State Initialization in TeNPy 1.1.0 (Without Symmetry Constraints)

## Overview
Standard iDMRG initialization for purely diagonal topological Hamiltonians (like the Toric Code) usually requires enforcing quantum number conservation (e.g., `conserve='parity'` in TeNPy). If you try to run iDMRG with `conserve=None` from a trivial product state, the algorithm will immediately collapse into a classical flux-free minimum due to the lack of energetic gradients.

This repository provides a simple, pragmatic 2-step workaround to bypass this "flat landscape" trap and successfully extract the topological ground state and its Schmidt values without using symmetries.

## The Heuristic (How it works)
1. **Adiabatic Symmetry Breaking:** We deform the Hamiltonian by adding small symmetry-breaking perturbations ($h_x \sum \sigma^x + h_z \sum \sigma^z$). This lifts the flat degeneracy, creating a unique gapped ground state that standard iDMRG can easily find.
2. **Strict Subspace Truncation:** We quench back to the pure topological Hamiltonian, turn off the DMRG mixer, and strictly enforce `trunc_params={'chi_max': d}`, where `d` is the analytically expected topological degeneracy of your geometry. The truncated SVD naturally discards the non-topological components.

**Important Limitation (The "Circular" Catch):** 
This method *requires* you to know the target degeneracy `d` beforehand to set the truncation limit. It cannot *discover* the topological order blindly; it acts as a validator/enforcer once the theoretical degeneracy is known.

## Analytical Note on Degeneracy
For a $\mathbb{Z}_2$ Toric Code on a cylinder of circumference $L_y$, the topological entanglement spectrum at a bipartition cut has a degeneracy of $d = 2^{L_y - 1}$. 
Therefore, if you use $L_y = 3$ (as in the provided script), you must set `chi_max = 4`.

## TeNPy 1.1.0 API "Gotchas" (Bugs we had to bypass)
If you are modifying these scripts, be aware of these undocumented breaking changes in TeNPy 1.1.0:
* **`trunc_params` Routing:** `chi_max` in the main DMRG options dict is **silently ignored** and defaults to 100. It *must* go inside `trunc_params={'chi_max': X}`.
* **`group_sites()` is In-Place:** It returns `None`. Doing `psi = psi.group_sites(n)` will destroy your MPS.
* **MPO Engine init:** `TwoSiteDMRGEngine` requires a `Model` object, never a raw `MPO`.
* **`DualSquare` Initialization:** `MPS.from_lat_product_state()` fails on tiling. Use `MPS.from_product_state(model.lat.mps_sites(), ...)`.

## Results
Running `qpip_z2_2d_toric_baseline.py` yields the raw Schmidt values at the entanglement cut:
```python
[0.5, 0.5, 0.5, 0.5]
```
Calculating the logarithmic singular values $\epsilon_i = -\ln(\lambda_i)$ gives the expected 4-fold degeneracy at $\ln(2) \approx 0.693$. 
*(Note: This differs by a factor of 2 from the standard Li-Haldane entanglement spectrum $\xi_i = -2\ln(\lambda_i)$, but directly reflects the singular value uniformity).*

## Repository Contents
* `qpip_z2_2d_toric_baseline.py`: Multi-step 2D DMRG baseline using bond dimension squeezing for topological alignment and heuristic spectrum extraction.
* `qpip_z2_2d_toric_baseline_clean.py`: Optimized 2D baseline using direct topological projection, strict TenPy API compliance, and deterministic spectrum extraction.
* `qpip_z3_3d_gauge_viability_probe_crash.py`: Failed 3D emulation via aggressive 2D site-grouping, resulting in catastrophic SVD collapse and memory crash.
* `qpip_z3_3d_gauge_viability_probe_concept.py`: Native 3D Z3 lattice proving iDMRG fails due to Area Law saturation, justifying the migration to NQS.
* `plotting_tools.py`: Script to generate the publication-quality PDF figures.
* `figures/`: The generated `.pdf` plots.

## Requirements
* Python 3.8+
* TenPy 1.1.0 (`pip install tensornetwork`)
* NumPy, SciPy, Matplotlib

## License
MIT
