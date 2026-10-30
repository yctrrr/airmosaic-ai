---
name: atmospheric-input-methods
description: Specify version-specific GEOS-Chem meteorology, initial and boundary conditions and diagnostic input contracts. Reference guidance without a downloader.
---

# Atmospheric-model input contracts

**English** | [中文](SKILL_ZH.md)

Use this reference to prepare an input checklist for a selected GEOS-Chem Classic or GCHP version. It has no downloader, execution adapter or run-tool ID.

## Specify a configuration

Record the exact model release, Classic/GCHP variant, simulation type, time range, horizontal/vertical grid and restart time. Use the selected release's own configuration and input documentation; do not infer compatibility from filenames.

| Input | Contract to record | Check before handoff |
|---|---|---|
| Meteorology | Product/release, frequency, grid, vertical coordinates and required variables | Full time coverage, units, calendar and level ordering |
| Initial/restart state | Model/species version, initialization time, units and grid | Species mapping and exact start-time compatibility |
| Nested boundaries | Parent source, boundary schedule, species and vertical/horizontal mapping | Domain coverage, time interpolation and edge/level consistency |
| Diagnostics | Selected fields, frequency, averaging and output coordinates | Definitions sufficient for evaluation and mass-budget interpretation |
| Emission interface | Required species, units, time support and spatial support | Conceptual compatibility only; inventory construction is a separate method |

Deliver the checklist, unresolved compatibility decisions and a scoped acquisition plan with source versions and expected files. A model-generated dry-run is an actual program execution that writes logs; it requires its own run scope.

For general meteorological covariates or composition fields, use [ERA5](../../01_socioeconomic_natural_change/era5/SKILL.md) or [CAMS](../../01_socioeconomic_natural_change/cams/SKILL.md). Their files need separate conversion to a GEOS-Chem contract. See [transport methods](../../../../methods/03_atmospheric_transport/README.md) for scientific context.

Keep non-secret task settings in CONFIG_DIR, data/results in ASSETS_DIR and sessions in AUTH_DIR, separately outside Git. This skill prepares contracts; it does not acquire or inspect original inputs automatically.
