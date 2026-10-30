# Stage data navigation

**English** | [中文](README_ZH.md)

Keep one primary location per dataset and reference its fixed version across stages. Public inputs must be declared synthetic fixtures or explicitly authorized licensed snapshots. Private data remain at the configured external asset root.

The [toy manifest](../../toy-manifest.json) records the read-only `SyntheticIO/v1`, `SyntheticMFA/v1`, `SyntheticLCA/v1`, `SyntheticEconometrics/v1` and `SyntheticCGE/v1` CSV inputs for the corresponding stage 01 direct-script skills. Their numbers are illustrative, not observations or calibrated research parameters. `SyntheticCGE/v1` supplies a balanced social accounting matrix, a productivity scenario and a one-way environmental satellite coefficient for the [CGE tutorial](../../../skills/model/01_socioeconomic_natural_change/cge/SKILL.md).

See the [asset entry](../../README.md).
