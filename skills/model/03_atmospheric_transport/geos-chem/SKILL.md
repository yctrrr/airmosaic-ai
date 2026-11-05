---
name: geos-chem-workflow
description: Build, configure and check the tested Classic 14.8.0 transport and public v35l chemistry-component adjoint routes, with native templates and parameter guides.
compatibility: "POSIX; Python>=3.10; Git; CMake>=3.13; Intel Fortran; NetCDF-C/Fortran; NumPy and netCDF4 for v35l conversions."
metadata:
  version: "0.3.1"
---

# GEOS-Chem: choose one successful route

**English** | [中文](SKILL_ZH.md)

**Stage:** 03, atmospheric transport and chemistry. Read the [method](../../../../methods/03_atmospheric_transport/geos_chem.md) for scientific interpretation.

| Your task | Start here | Tested configuration |
|---|---|---|
| Build a forward model and produce concentration/restart files | [Classic beginner guide](references/usage.md) | Classic 14.8.0, TransportTracers, MERRA-2, global 4×5, 47 levels, one hour |
| Run chemical forward/adjoint calculations and check derivatives | [Adjoint beginner guide](references/adjoint.md) | Public v35l fork, GEOS-FP, chemistry component, three hours, NOx initial scale → surface Ox mass |

Follow one guide from source → build → input configuration → execution → output checks. Both guides include native templates, parameter meanings, examples of changing inputs and expected outputs. [Sources and tested coverage](SOURCES.md) records the exact versions and the public skill review. [Troubleshooting](references/build-troubleshooting.md) covers common failures.

## Files supplied with this skill

- `templates/classic_14.8.0/`: complete `geoschem_config.yml`, HEMCO and HISTORY templates plus `settings.json`.
- `templates/adjoint_v35l/`: complete `input.geos`, `input.gcadj`, `ITER`, settings, a hash-checked chemistry-component patch and module dependencies.
- [configure_run.py](scripts/configure_run.py): render either set into a fresh external directory; plan by default.
- [build_classic.py](scripts/build_classic.py), [prepare_v35l.py](scripts/prepare_v35l.py): Classic build planning/execution and v35l source-profile preparation.
- [bounded_inputs.py](scripts/bounded_inputs.py), [prepare_v35l_inputs.py](scripts/prepare_v35l_inputs.py): bounded Classic acquisition and the tested v35l input-format conversions.
- [run_v35l.py](scripts/run_v35l.py), [check_outputs.py](scripts/check_outputs.py), [check_v35l_gradients.py](scripts/check_v35l_gradients.py): bounded native adjoint execution, fixed Classic output checks and independent global gradient checks.
- [prepare_classic.py](scripts/prepare_classic.py): alternative preparation from the selected Classic source's native run-directory templates.
- [gc_paths.py](scripts/gc_paths.py), [v35l_bpch.py](scripts/v35l_bpch.py): shared path/receipt and native BPCH utilities used by the helpers.

Scripts are in `scripts/`. They are direct helpers, with no registered run-tool/MCP simulation or scheduler adapter. Template rendering does not download or validate physical data. Newly generalized helpers have synthetic checks and saved-output regression checks; the original model tests establish the configuration's bounded runtime evidence, not a new execution of every helper.

## Operating boundaries

Keep source, inputs, fresh runs and checks outside Git. Use the caller's explicit compiler/library environment and authorized compute allocation. Keep credentials, site paths and raw logs out of shared files. Preserve successful inputs/results; inactive history may be consolidated into a verified archive with a short recovery index.

Select source by model version and match its configuration and inputs. Recheck interfaces and outputs when upgrading; keep chemistry/process choices and objective/control definitions explicit. Changes prepare a new experiment and need renewed input/output and derivative checks. The v35l patch defines a chemistry component; it does not enable complete atmospheric transport, emissions or inversion. Its two larger perturbations met the predeclared global tolerance, while the smallest step and many local cells did not. Scientific acceptance remains separate from technical execution.
