---
name: atmospheric-input-methods
description: Plan meteorology, initial and boundary conditions and diagnostic input contracts for version-specific GEOS-Chem workflows. No downloader.
---

# Atmospheric-model input preparation

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status:** documentation only; no execution adapter or tool ID for run-tool.

## Workflow

Choose Classic/GCHP and a version → list meteorology, emissions, initial/boundary conditions and diagnostics → check time, grid, species and unit contracts → scope and authorize acquisition separately.

See the [method and handoff guidance](../../../../methods/03_atmospheric_transport/README.md).

For meteorological covariates or atmospheric-composition data, read [ERA5](../../01_socioeconomic_natural_change/era5/SKILL.md) and [CAMS](../../01_socioeconomic_natural_change/cams/SKILL.md). Their manual acquisition guidance does not replace version-specific GEOS-Chem meteorology, species or boundary inputs; no automatic conversion or download tool is provided.

## Boundaries

Do not read original data or authentication directories or automatically download inputs. GEOS-Chem's own dry-run executes a program and writes logs. Emission inputs are interface requirements only, without concrete inventory data or implementation.

Documentation maintenance and routine validation use only documents, interfaces and synthetic inputs. Real-data work requires an explicit scope. Keep personal paths and non-secret settings in CONFIG_DIR, credentials in a credential manager, and sessions in AUTH_DIR; data, configuration and authentication roots must be separate and outside Git. Reference skills do not automatically enforce paths or create sanitized run receipts.
