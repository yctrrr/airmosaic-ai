# Troubleshooting the two maintained configurations

**English** | [中文](build-troubleshooting_ZH.md)

Keep the original failing case and diagnose the first useful error. A correction belongs in a fresh build/run with the source, settings and outcome recorded.

| Symptom | Check and correction |
|---|---|
| Missing submodule / native table | Verify the selected model version and recursive Classic submodules; v35l static tables must match that model version. Do not borrow another mechanism's files. |
| Missing compiler, NetCDF or runtime library | Use matching C/Fortran libraries and the same build/run environment. Check `nf-config`, `nc-config`, executable linking and CMake log. An unrelated conda runtime can interfere. |
| Legacy make module-order failure | Use the supplied dependency file and serial `-j1`; do not repair by linking stale objects from a different profile. |
| Old `-openmp` option rejected | The tested Intel environment uses explicit `-qopenmp`; retain the complete documented flags. |
| Native input parse failure | Preserve fixed label columns and all menu rows; use the templates. `ITER` needs two lines before every invocation. |
| Met read failure or wrong clock | Check actual I3 endpoints and mean intervals; the component requires the demonstrated complete three-hour interval. Keep CN/ApBp in their native constants directory. |
| UV/TOMS cannot open | Use the legacy BPCH layout and checked conversion, not only renamed NetCDF. Preserve UV values and TOMS remapping/metadata. |
| Segmentation fault / stack issue | Main-thread stack needs `ulimit -s unlimited`; workers use `OMP_STACKSIZE=256M`. Check the allocation and original error; a stack increase cannot fix an uninitialized physical array. |
| Excluded process enabled | The component profile intentionally refuses emissions, transport, mixing and deposition flags. Return to the documented component, or design a separately reviewed full-process run. |
| Zero exit but no result | Fortran STOP may exit zero. Require native finish, current cost, newly written end restart and independent content checks. |
| Prepared-input hash mismatch | Do not bypass the receipt. Prepare/review another configuration if native settings change. |
| Existing output / partial transfer / budget refusal | Preserve files, inspect jobs/processes/receipts and reuse healthy work. Do not reset the ledger, remove unknown locks or rerun fits/integrations blindly. |
| Gradient disagreement | Confirm tracer IDs, baseline/plus/minus ordering, units and support. Inspect all predeclared steps and local errors. Do not change tolerance or hide the smallest-step failure to obtain a pass. |
| Aerosol-feedback-adjoint warning | Remains an unresolved coverage boundary; the demonstrated global criterion does not repair the missing derivative. |

Start from the [Classic](usage.md) or [v35l](adjoint.md) tutorial. Historical failed versions remain recoverable outside the active skill; they are not extra maintained recipes. See the [14.8.0 debug guide](https://geos-chem.readthedocs.io/en/14.8.0/geos-chem-shared-docs/supplemental-guides/debug-guide.html).
