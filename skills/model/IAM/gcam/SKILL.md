---
name: gcam
description: Explore GCAM output structure, understand configuration files, and extract scenario data from BaseX XML databases. Use when an agent needs to inspect scenario results, compare model outputs, trace input data chains, extract sector prices or technology components, understand CCS configuration, or navigate GCAM-China specifics. Three sub-layers handle output structure (01), configuration (02), and data extraction (03).
---

# GCAM Model Analysis

> Invocation status: named wrappers in Agent Contract sections are proposed, not registered APIs. Verify actual scripts and template requirements in the [tool catalog](../../../../harness/tool-catalog.md).

## Local paths and authentication

Follow the [shared storage contract](../../../../harness/storage-and-credentials.md): data and results use `AIRMOSAIC_LOCAL_WORKSPACE`, personal non-secret configuration uses `AIRMOSAIC_CONFIG_DIR`, and browser authentication state uses `AIRMOSAIC_AUTH_DIR`. Read only task-needed configuration; never inspect, print or copy credential values or browser state. Set module output arguments explicitly for each run. These conventions do not imply automatic config loading or runtime isolation.

## Layer Navigation

Choose the right layer based on the task:

| Task | Layer |
|------|-------|
| List scenarios, regions, sectors, subsectors, technologies | [01_output_structure](01_output_structure/SKILL.md) |
| Check price/quantity unit compatibility | [01_output_structure](01_output_structure/SKILL.md) |
| Map province codes to province names | [01_output_structure](01_output_structure/SKILL.md) |
| Understand configuration XML and scenario components | [02_configuration](02_configuration/SKILL.md) |
| Trace how input CSV becomes BaseX output | [02_configuration](02_configuration/SKILL.md) |
| Add or remove a scenario component safely | [02_configuration](02_configuration/SKILL.md) |
| Diagnose CCS configuration issues | [02_configuration](02_configuration/SKILL.md) |
| Look up sector naming conventions | [02_configuration](02_configuration/SKILL.md) |
| Extract market/sector price and quantity rows | [03_data_extraction](03_data_extraction/SKILL.md) |
| Decompose sector cost into technology components | [03_data_extraction](03_data_extraction/SKILL.md) |
| Aggregate province rows to national weighted values | [03_data_extraction](03_data_extraction/SKILL.md) |
| Plot sector price/quantity change over time | [03_data_extraction](03_data_extraction/SKILL.md) |
| Interpret price units and sector-specific quirks | [03_data_extraction](03_data_extraction/SKILL.md) |

## Prerequisites

Set environment variables before using any layer:

```powershell
$env:GCAM_RELEASE_DIR = "<path to gcam-china-v8-Windows-Release-Package>"
$env:UNIT_PRICE_OUT_DIR = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "output/example/gcam"
```

## Data Boundary

This skill stores reusable methods only. Do not copy GCAM model releases, BaseX databases, scenario outputs, or raw data into the skill directory. See `data_boundary.md`.

The skill does not store credentials, tokens, cookies, browser profiles, personal paths, or private download links.

## Cross-Cutting References

- `references/gcam-china-vs-official.md`: differences between GCAM-China and official GCAM-Core
- `references/input-data-architecture.md`: full pipeline from raw CSV to BaseX output
- `references/privacy-redaction-rules.md`: checklist for keeping derived methods clean
- `data_boundary.md`: what belongs in and out of the skill
