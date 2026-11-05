# GEOS-Chem: processes, interventions and local sensitivities

**English** | [中文](geos_chem_ZH.md)

## Scientific role

GEOS-Chem represents atmospheric composition as the result of emissions, chemical production/loss, transport/mixing and deposition, conditional on meteorology and initial/boundary conditions. A concentration scenario asks how the modeled trajectory changes under an intervention. An adjoint asks how a defined scalar response changes locally with many controls. Neither operation identifies a causal policy effect without a suitable research design. [Model foundation](https://doi.org/10.1029/2001JD000807).

This method maintains two demonstrated routes. [Classic 14.8.0](https://github.com/geoschem/GCClassic/releases/tag/14.8.0) supplies a TransportTracers/MERRA-2/global 4×5/47-layer forward example. The [public v35l fork](https://github.com/stevezhang1990/GEOS-Chem-adjoint-v35) supplies its own paired forward/adjoint chemistry component. The latter is not an adjoint switch for Classic 14.8.0 and has not been authenticated as official v36.

## Design the comparison

State species/families, receptor cells, levels, period, units, averaging and the control before execution. Separate an emission intervention from initial-state sensitivity and meteorological variation. Hold other inputs fixed, or use an explicit factorial design when studying interactions. Match meteorology, inventories, restart and auxiliary data by product, grid, vertical definition and actual time coverage. A 4×5 grid cell represents an atmospheric volume rather than a roadside monitor; increasing output frequency cannot repair inadequate spatial support.

Initialization and spin-up depend on species lifetimes and the target statistic. A one-hour transport demonstration does not establish a chemically equilibrated atmosphere. Scientific applications require sensitivity to initialization, adequate meteorological/emission coverage and independent observational evaluation. Concentration, inventory, meteorological and numerical uncertainties should remain distinguishable.

## Forward fields and units

Preserve native concentration fields and end restart with scenario, source/binary identity, configuration and input provenance. `SpeciesConcVV_*` is dry-air volume mixing ratio; an end restart is instantaneous, while a diagnostic may be an interval average. Conversion to ambient mass concentration needs molecular mass, air density, temperature/pressure and dry/moist conventions. PM2.5 additionally needs a justified composition, size fraction and aerosol-water convention. This TransportTracers case does not establish PM2.5 chemistry.

Check the actual time interval and averaging convention, coordinates, hybrid pressure levels, species, dimensions, units and finite values. Match observations by local/UTC time semantics, vertical definition and common valid support. Separate instrumental and representation errors from model bias, and keep evaluation independent of calibration. Pass [impact assessment](../04_integrated_impacts/health_impacts.md) the original concentration scenario, derived exposure definition and uncertainty; calibration transfer to intervention scenarios requires its own justification.

## Adjoint controls and response

Let x(T;p) be the selected branch's terminal state and J(p)=Σ wᵣ xᵣ(T;p) a declared scalar response. Specify receptor/temporal/vertical weights and units. The derivative dJ/dp is local to the selected trajectory, with units of response per control; it differs from a finite nonlinear intervention, tagged contribution or optimized posterior emission. An inversion also needs priors, observation errors and regularization.

The demonstrated v35l control is dimensionless initial NOx scale s(i,j,level=1), baseline 1. NOx and Ox retain the native chemical-family definitions. The response is terminal surface Ox mass in kg/box; a global objective sums the selected surface masses. The native `FD_GLOB` test simultaneously perturbs the selected initial scale at every horizontal cell of the surface layer. It is designed for the no-transport component: its cellwise comparison must not be transferred to a coupled transport model or interpreted as a general full Jacobian test.

For each predeclared h=0.1,0.03,0.01, retain baseline/plus/minus forward states and the baseline adjoint. The independent checker computes the centered difference [x(T;s+h)−x(T;s−h)]/(2h) at the common surface cells and compares it with the matching baseline adjoint. It reports ||g_adj−g_FD||₂/||g_FD||₂, finite nonzero norms and local exceptions. The criterion is ≤5% at two neighboring h values; it is a numerical criterion, not scientific acceptance. Interpret cancellation and truncation across h without changing thresholds after inspecting results.

## Demonstrated boundary and remaining uncertainty

| Route | Evidence and limit |
|---|---|
| Classic 14.8.0 | 2019-01-01 00–01 UTC completed with exit zero; 21 concentration and 21 restart fields passed time/grid/levels/species/units/averaging/finite-content checks. Demonstrates the bounded transport operation chain. |
| Public v35l | 2026-10-26 03–06 UTC, GEOS-FP, 43 tracers; nine final native calls completed. Relative L2 errors 1.4639%, 2.6269%, 6.2708%; two larger steps met the criterion, the smallest failed. Local exception counts 829/830/895 of 3,312 surface cells (|FD|>1 and relative error>5%). |

The v35l profile excludes emissions, transport, convection, PBL mixing, dry/wet deposition and acetone ocean exchange, with paired dust-settling exclusion. A native warning about missing aerosol-feedback adjoint remains. Its initial field is a legacy 2005 payload with time metadata adapted to an explicitly artificial operating point; its 43 species names are not embedded independently in BPCH. UV is a legacy climatology and native TOMS is fixed to 2010 for later years. Modern meteorology does not turn these inputs into a realistic 2026 atmosphere. These constraints require separate resolution before real emission sensitivity, inversion, pollution reconstruction or policy inference.

## Reproducibility and acceptance

Keep the two successful configurations, their immutable input references, source changes, binaries, outputs and independent checks accessible. Consolidate unused versions and failure evidence into a recoverable history index. Preserve failures needed to explain the final scientific boundary without making them the beginner's main path.

The [skill](../../skills/model/03_atmospheric_transport/geos-chem/SKILL.md) contains compilation, complete templates, input layout, parameter meanings, changes and output checks. Direct helpers have no registered run-tool/MCP simulation or scheduler adapter. A zero exit, marker, source build or passing numerical criterion cannot replace physical evaluation and human scientific acceptance.
