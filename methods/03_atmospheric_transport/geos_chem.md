# GEOS-Chem transport and concentration scenarios

**English** | [中文](geos_chem_ZH.md)

GEOS-Chem represents atmospheric transport, chemistry and removal to translate source and meteorological assumptions into concentrations and deposition. Define the research contrast before selecting a simulation: baseline/intervention, source sensitivity or process diagnosis answer different questions. Model scenario differences are conditional responses, not automatically observed policy effects.

## Design the comparison

Select Classic or GCHP, a pinned model version, chemical mechanism, horizontal/vertical grid, domain and simulation period. Match meteorology, initial and boundary conditions, chemical species definitions and diagnostics to that design. Emission interfaces remain conceptual here: specify temporal/spatial support, species and unit compatibility without inventory data or implementation.

Use a justified initialization and spin-up assessment. Nested regions require adequate boundary coverage; a restart file must match the declared grid, species and initialization purpose. Different versions, transport configurations and mechanisms can change the scientific comparison and must not be silently pooled.

## Validate concentrations

Separate technical completion from scientific adequacy. Process success and an end marker do not prove the intended period, species or domain was simulated. Check time coverage, units, surface/vertical definition, missingness, diagnostics and restart consistency. Compare observations with matched time and spatial support, state measurement/model representativeness and report remaining bias.

When concentration calibration is used, preserve the original field, calibration design and independent evaluation. Avoid validation leakage, and justify whether the same correction can be applied to intervention scenarios. A corrected exposure field is distinct from a new chemistry simulation.

## Handoff to impacts

Supply scenario identifiers, model/source versions, averaging period, coordinate/grid information, species, units and surface definition. Fix common valid population support for [health comparisons](../04_integrated_impacts/health_impacts.md), documenting excluded grid cells and periods. Sensitivity, adjoint and forward scenario contrasts have different interpretations; the availability of a forward binary does not establish adjoint capability.

The [GEOS-Chem skill](../../skills/model/03_atmospheric_transport/geos-chem/SKILL.md) owns version-specific setup and retained compilation tricks. Its [sources](../../skills/model/03_atmospheric_transport/geos-chem/SOURCES.md) link official Classic/GCHP documents and date the historical review. There is no reviewed build, download, scheduler or simulation adapter; operational success and scientific validation require separate evidence.
