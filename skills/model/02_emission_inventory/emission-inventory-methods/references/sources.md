# Reviewed sources and external skill patterns

**English** | [中文](sources_ZH.md)

Checked on 2026-10-30. Scientific equations and factor applicability use primary inventory guidance, not the popularity of an agent repository. No MEIC data/code was read, copied or used. All bundled numeric inputs are synthetic and contain no actual country or enterprise estimates.

| Source | Use in this skill | Limit |
|---|---|---|
| [US EPA: emission-factor basics](https://www.epa.gov/air-emissions-factors-and-quantification/basic-information-air-emissions-factors-and-quantification) | Activity × factor × remaining fraction and factor interpretation | Average factors are not source-specific limits or proof of compliance |
| [EPA 2017 inventory guidance](https://www.epa.gov/sites/production/files/2017-07/documents/ei_guidance_may_2017_final_rev.pdf) | Separate capture, pollutant removal, operating effectiveness and penetration | The implemented activity-weighted operational field needs task evidence; regulatory terms are not universally interchangeable |
| [EMEP/EEA Guidebook 2023](https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2023), [factor viewer](https://efdb.apps.eea.europa.eu/) | Source-category/technology applicability, factor discovery and inventory quality | No numeric factor copied into the toy input; consult official chapter/version for a real use case |
| [IPCC 2006 Energy](https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol2.html) | Scope-aware greenhouse-gas activity/factor guidance | Not a criteria-pollutant factor replacement |
| [K-Dense exploratory-data-analysis skill](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/exploratory-data-analysis/SKILL.md) | Explicit local input root, bounded schema, missing/zero distinction and scoped checks | Organization/validation ideas only; no copied script or installation |
| [K-Dense scientific-critical-thinking skill](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-critical-thinking/SKILL.md) | Separate observations, assumptions, applicability and unsupported conclusions | Not a scientific certification |

The two reviewed external skills identify MIT licensing; the repository's [license](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/LICENSE.md) was inspected. AirMosaic's calculator, inputs, tests and prose were independently authored. No third-party source code, repository or dependent package was vendored or installed. Future copying of substantial material would require its applicable notice and a fresh review.

The National Data and permit portals listed in the method are candidate data-preparation channels. Their complete contents, record permissions, exports and historical coverage were not verified; no real data were acquired from them. No automated factor selection or source download is implied.
