# Sources and verification coverage

**English** | [中文](SOURCES_ZH.md)

Reviewed 2026-11-05. Shared assets contain reusable instructions/templates, not private execution records. Earlier technical-note provenance remains in [source snapshots](../../../../methods/source-snapshots.yaml).

## Primary sources

| Source | Used for |
|---|---|
| [Classic 14.8.0 release](https://github.com/geoschem/GCClassic/releases/tag/14.8.0) | Release version and recursive submodules |
| [14.8.0 runtime configuration](https://geos-chem.readthedocs.io/en/14.8.0/geos-chem-shared-docs/doc/geoschem-config.html), [CMake build](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/compile-cmake.html) | Native files, compiler/library setup; templates read from the successful Classic 14.8.0 run |
| [Dry-run](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/dry-run-run.html), [download inputs](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/download-data.html), [History](https://geos-chem.readthedocs.io/en/14.8.0/geos-chem-shared-docs/supplemental-guides/history-diag-guide.html) | Required-file inventory, diagnostics, averaging and time semantics |
| [Public v35l source](https://github.com/stevezhang1990/GEOS-Chem-adjoint-v35) | `code/Makefile`, `define.h`, `adjoint/define_adj.h`, `inverse_mod.f`, input readers and complete `runs/v8-02-01/geos5` tables; matched forward/adjoint profile |
| [Historical adjoint manual](https://spot.colorado.edu/~henzed/GC_adj/GC_adj_man.pdf) | Background on menus/controls, interpreted against this branch's actual source |
| [Official public input bucket](https://geos-chem.s3-us-west-2.amazonaws.com/), [input layout and keys](references/adjoint.md) | GEOS-FP, backward-compatible UV albedo and TOMS inputs; source/converted hashes remain with the experiment |
| [Zenodo legacy input archive](https://zenodo.org/records/7517355) | Verified `gcadj_std.zip` restart member; input provenance only, not authority to relabel the public source as official v36 |

The Classic checker uses the Classic 14.8.0 example's 47-layer Ap/Bp definition and the 21 transported species, dry-air units and interval-start History timestamp. In the single-record case, coverage is checked using start/end attributes, averaging metadata and the matching one-hour HISTORY configuration; it does not assume a CF time-bounds variable exists.

## Public skill reference

[earth-space-ai/geos-chem-skill](https://github.com/earth-space-ai/geos-chem-skill), scaffold version `0.1.0`, was reviewed for task routing and the multi-file configuration checklist. It identifies itself as `0.1.0-scaffold` and lists eight detailed references that were absent when reviewed. No files were copied or installed. Its nested HEMCO/Cloud-J path claim was not adopted: in tested Classic 14.8.0, GEOS-Chem, HEMCO, Cloud-J and HETP are direct children of `src/`. Model source and actual successful configurations remain the operational authority.

## Checked coverage

| Check | Outcome / boundary |
|---|---|
| Classic model | Classic 14.8.0 and its matching submodules, Intel/NetCDF build, native dry-run, 16 physical input files (498,084,688 bytes), one-hour TransportTracers run with exit zero |
| Classic outputs | 21 concentration +21 restart fields checked for grid, hybrid levels, dimensions, species, units, time, averaging and finite values |
| v35l native model | Chemistry component, GEOS-FP, 2026-10-26 03–06 UTC, 43 tracers; nine final invocations exited zero; executable identity retained in the experiment record |
| Independent gradient check | h=.1/.03/.01: relative L2 1.4639%/2.6269%/6.2708%; two neighboring steps passed the predeclared 5% criterion; smallest step and numerous local cells failed |
| New preparation helper | Original v35l profile replay matched all 11 reference files; version selection now uses model numbers and patch applicability, with actual source identities recorded |
| Generalized helper checks | Synthetic config/path/source, derivative/support, native-call protocol/failure, spherical conservation and BPCH roundtrip checks; saved 3,312-cell ×3-step comparison reproduced the earlier independent metrics |
| New native runner/converter | Synthetic checks and original successful implementation experience; not a fresh end-to-end physical rerun of every generalized CLI |
| Full atmosphere / inversion | Not established by these tests; artificial legacy initial state, climatological radiation and missing aerosol-feedback adjoint remain limitations |
| Execution registration | Direct scripts only; no registered run-tool/MCP simulation, scheduler adapter or automatic host installation |

Source/profile checks, operational completion, numerical checks and scientific acceptance are separate. Full private evidence and recoverable inactive history stay with the external project. Scientific acceptance requires human review.
