# Enterprise panels and statistical constraints

**English** | [中文](enterprise_panels_ZH.md)

## Research question

Build a comparable enterprise–year panel for activity, energy or financial analysis. Decide whether the observation is a legal entity, consolidated group or production facility; changes in ownership and reporting scope can otherwise look like economic change.

## Sources and definitions

Combine reviewed identity evidence, financial tables, production evidence and statistical benchmarks with explicit source mappings. Preserve original identifiers and text codes. Financial variable names must be mapped to the source's actual definition, currency, price basis and consolidation scope.

## Organization and estimation

1. Deduplicate entity–year–version records and resolve parent/subsidiary overlap before aggregation. Keep proposed identities separate from confirmed ones.
2. Retain reported, derived and filled values in distinct fields with their rule and source. For example, revenue minus pre-tax profit is a derived residual; it is not automatically the same concept as reported operating cost.
3. Accept physical quantities only with period, unit, quantity type and original evidence. Capacity, production, sales and financial revenue measure different things.
4. Map industry/region versions explicitly. If filling from sector growth or calibrating to yearbook totals, state the grouping, denominator, weights, treatment of zeros and minimum supporting observations.
5. Compare original and adjusted distributions as well as province–sector–year totals. Test applicable enterprise-row identities separately from aggregate agreement.

## Error and quality

Entity merges, duplicated group accounts and mismatched sector versions can dominate apparent trends. Missingness may depend on firm size, survival or disclosure obligations. Independent scaling of revenue, cost and profit can satisfy each aggregate target while breaking row-level accounting identities; report both diagnostics and resolve the chosen accounting convention. Validate calibration on the population it represents rather than treating a benchmark as universal ground truth.

## Interpretation

A calibrated panel is a model-assisted estimate, not a new set of enterprise disclosures. Report the observed share, imputed share and affected groups, and retain an unadjusted comparison. Entity identity, production eligibility and economic incidence are separate conclusions. Source selection is described in [enterprise sources](enterprise_sources.md). Operational panel assembly requires reviewed task-specific adaptation; no dedicated assembly skill is currently provided.
