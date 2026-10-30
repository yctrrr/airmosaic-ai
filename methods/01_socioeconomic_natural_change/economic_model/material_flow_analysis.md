# Material flow analysis: physical flows and stocks

<!-- README-I18N:START -->

**English** | [中文](material_flow_analysis_ZH.md)

<!-- README-I18N:END -->

Material flow analysis (MFA) follows materials across a stated system boundary in physical units. Choose the object first: an economy-wide material account, a sector or product chain, or a specified substance or element. These scopes need different data and should not be combined as if they covered the same flows. Economy-wide material flow accounts (EW-MFA) record material exchanges between the national economy, nature and the rest of the world; a detailed process or substance flow study can also represent transfers within the economy. [SEEA material flow accounts](https://seea.un.org/en/methodology/other-accounts/material-flow-accounts) and the [Eurostat handbook](https://ec.europa.eu/eurostat/web/products-manuals-and-guidelines/-/ks-gq-18-006) describe the economy-wide framework.

## Define and balance the system

Record the material definition, physical unit, geography, accounting period, system boundary, processes and stock types before drawing flows. Distinguish extraction, imports, intermediate transfers, consumption or use, recycling, exports, releases and additions to stock. Internal transfers cancel at the system-wide boundary but matter when locating a sector or process. Record an origin and destination for each flow to avoid counting the same movement twice.

For a consistently defined material and boundary, the balance is `inputs + balancing inputs = outputs + net additions to stock + balancing outputs`. At a process level, changes in chemical composition or the choice of an element rather than a compound affect what counts as input or output. For example, economy-wide material accounts commonly need balancing items associated with oxygen and water; a residual discrepancy is a quality diagnostic, not an automatic flow to assign. The [SEEA technical note](https://seea.un.org/sites/seea.un.org/files/mfa_final_draft.pdf) distinguishes the economy boundary from within-economy flows, and [Eurostat's MFA metadata](https://ec.europa.eu/eurostat/cache/metadata/EN/env_ac_mfa_simsmf_ba.htm) states the material and residence boundaries of its official dataset.

An EW-MFA indicator such as domestic material consumption is `DMC = domestic extraction + physical imports − physical exports` under its defined coverage. It measures direct material use, not a full supply-chain material footprint or the annual change in material stock. A stock estimate requires further information on additions, lifetimes and removals. The [Eurostat material-flow overview](https://ec.europa.eu/eurostat/en/web/environment/information-data/material-flows-resource-productivity) explains the reported flows and indicators.

## Connect to other methods

MFA supplies physical accounts and coefficients. A physical supply-use or IO extension can allocate material requirements along production and final demand, provided material-to-sector mappings and double counting are checked. A CGE model can use material coefficients, resource constraints or state variables, but MFA data alone do not determine price, substitution or income responses. LCA can use process flows as an inventory for impact assessment per functional unit; it adds an impact model and a different product-system boundary. Do not equate mass, an emission inventory, environmental impact and monetary cost. See [IO](io/README.md), [CGE](cge/README.md), the [SEEA Central Framework](https://seea.un.org/en/methodology/seea-central-framework), and [ISO 14040](https://www.iso.org/standard/37456.html).

## Minimum checks and reporting

Check units and material composition; territorial versus residence accounting; imports and exports; recycling loops; missing or estimated flows; stock changes; and balance discrepancies by year and region. Report the source, boundary, direct versus indirect coverage and uncertainty for each indicator. If a model uses MFA results, preserve the material-sector crosswalk and state whether physical values constrain the model, calibrate it, or are only reported afterward. The [MFA skill](../../../skills/model/01_socioeconomic_natural_change/material-flow-analysis/SKILL.md) provides a small direct-script calculation; it is not a registered tool.

The published [K-Dense industrial-ecologist agent skill](https://github.com/K-Dense-AI/scientific-agents) informed the boundary and mass-balance-first workflow. The local method keeps its narrower, explicit accounting equations.
