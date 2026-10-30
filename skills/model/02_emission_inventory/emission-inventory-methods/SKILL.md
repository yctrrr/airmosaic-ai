---
name: emission-inventory-methods
description: Build explicit activity, technology and end-of-pipe-control emission accounts with a local numeric calculator; validate units, shares, coverage and pollutant-specific totals.
compatibility: "Python 3.10+ standard library; direct local script; no run-tool or MCP adapter"
metadata:
  version: "1.0.0"
  reviewed: "2026-10-30"
---

# Design emission accounting

**English** | [中文](SKILL_ZH.md)

Use the [method](../../../../methods/02_emission_inventory/emission_accounting.md) for scientific boundaries, activity/technology/control definitions, candidate data sources and uncertainty. This entry now provides a direct Python calculator validated with synthetic inputs. Its stable skill name is unchanged; it has **no registered tool ID, run-tool or MCP adapter**. Spatial allocation remains a separate conceptual/adaptation route.

## Use

1. Declare region/year, activity and material/energy basis, sector/process and pollutant conventions. Confirm approved sources and output scope before real-data preparation.
2. Prepare four normalized tables in an explicit JSON: activities, technology activity shares, **uncontrolled** factors and exclusive control routes. Distinguish installation coverage, effective activity-weighted operation, capture and pollutant removal.
3. Check complete shares, unique keys, unit/basis compatibility, complete factors/routes and provenance. Do not infer missing routes, renormalize shares or subtract controls already present in a factor.
4. Follow [configuration and calls](references/operations.md): use the direct script's own `--dry-run`, then execute into a fresh authorized external output directory. This is not a runner preflight or an OS sandbox.
5. Inspect detailed/route emissions, pollutant-specific aggregates, input/outputs hashes and mass balance. Report scientific limitations and any missing real-data adaptation before downstream use.

The [complete example](examples/inventory.synthetic.json) contains only invented activity, factors and control settings. Its expected remaining emissions are 24,664 kg SO₂ and 30,960 kg NOx; they are arithmetic checks, not observations or actual inventory estimates. The [operation reference](references/operations.md) supplies runnable commands and output checks. Twenty-one synthetic implementation tests passed on 2026-10-30, including numeric and unit checks, illegal shares/inputs, output non-overwrite, Git-boundary and linked-input refusals. No real data or credentials were read and no MEIC source was used.

The calculator reads only one explicitly named local JSON and never discovers data, downloads, installs packages or accesses credentials. Keep prepared real inputs and results in authorized external assets; personal path mappings and credentials stay separate. Source files are read-only, existing outputs are refused and logs omit personal absolute paths. Detailed outputs/models may still contain sensitive source labels and require review before sharing. Source interpretation and authorization are the caller's responsibilities; these checks do not provide complete runner isolation.

The initial path does not perform controlled-factor/CEMS accounting, derive joint serial-device operation, spatial/time/species disaggregation, factor retrieval or uncertainty propagation. [Spatial inventory methods](../../../../methods/02_emission_inventory/spatial_inventory.md) explain the next handoff. [External references](references/sources.md) record the reviewed skill patterns and primary scientific sources; no third-party code was copied or installed.
