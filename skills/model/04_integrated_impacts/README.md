# 04: Integrated Impacts

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->


Health, economic, distributional, ecological, agricultural and climate impacts. GBD has a controlled adapter and a verified one-record website download; real run-tool acquisition remains unverified. Health calculations/plots are templates, while full cost/distribution workflows require adaptation.

## Entry points

- [Health-risk methods, response data and templates](health_impact_analysis/SKILL.md): baseline rates and exposure-response functions are separate inputs; calculation and plotting templates remain disabled in run-tool.
- [GCAM output analysis](gcam/SKILL.md): registered inspection, extraction, aggregation and plotting; compilation and simulation remain unsupported.

## Workflow and handoff

Follow the [four-step workflow](../../../harness/four-step-workflow.md): confirm scope, choose methods, check prerequisites and hand off validated artifacts. See the [stage methods](../../../methods/04_integrated_impacts/README.md) and [shared methods](../../../methods/shared/README.md).

Documentation maintenance reads descriptions and interfaces only, not original data. Actual execution depends on tool manifests; directories and SKILL.md do not register tools.

Ecology, agriculture and climate impacts are scope navigation, requiring manual receptor, indicator, method and evidence selection. No dedicated executor exists. Natural conditions are upstream drivers in 01 and evaluated responses here.

Follow the [asset contract](../../../harness/assets.md): share data by stage, actual name and version; group results by project and run, referencing the same data across stages. Registration uses compute/check, human review and a fresh data version.

This directory is the primary home for these capabilities. Other research stages reference them as needed without copying skills; cross-stage use does not change their stage-04 ownership.
