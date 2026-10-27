# Cross-stage modeling methods

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->


- [Cost/distribution](cost-scenarios/SKILL.md): methods across activity, control and impact.
- [GCAM](../IAM/gcam/SKILL.md): existing-output tools; [build troubleshooting](../IAM/gcam/references/build-troubleshooting.md) is a reference without a simulation adapter.
- [Machine learning](../machine_learning/README.md): shared mlr3/TimeXer references, not copied per stage.

GEOS-Chem belongs in [03](../03_atmospheric_transport/geos-chem/SKILL.md), not as a substitute GCAM or ML entry. Shared navigation in 02 supplies methods only, without concrete inventory data or implementation.

Follow the [asset contract](../../../harness/assets.md): share data by stage, actual name and version; group results by project and run, referencing the same data across stages. Registration uses compute/check, human review and a fresh data version.
