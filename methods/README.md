# Research methods and design

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

Methods explain the scientific question, source meaning, method choices, assumptions, uncertainty and interpretation. Configuration, commands and software checks belong in skills.

## Four research steps

| Step | Questions and coverage | Read |
|---|---|---|
| 01 Socioeconomic and Natural Change | What upstream activities, population and natural conditions change, and how can they be described consistently? | [Stage methods](01_socioeconomic_natural_change/README.md) |
| 02 Emission Inventory | How should accounting boundaries, emission methods and allocation be chosen? | [Conceptual methods](02_emission_inventory/README.md) |
| 03 Atmospheric Transport and Chemistry | How do atmospheric processes connect inputs with concentrations, and how should observations be used for evaluation? | [Stage methods](03_atmospheric_transport/README.md) |
| 04 Integrated Impacts | Which human or natural outcomes are affected, and how should exposure, baselines and response be aligned? | [Stage methods](04_integrated_impacts/README.md) |

[Shared methods](shared/README.md) cover cross-stage data quality, literature, modeling design and reproduction. Stages describe research responsibilities; a study can reference shared evidence without repeating every step. Stage 02 includes methods and the explicitly declared bounded synthetic inventory route; other entries remain at their stated implementation level.

## Reading a method

Start with its intended question and applicability, then examine sources/units, analysis choices, quality rules and uncertainty. Use those decisions to define the inputs and checks needed by the corresponding skill.

For current operations, follow [skill categories](../skills/README.md). Detailed document-to-skill relationships live in [index.yaml](index.yaml); executable tools and current prerequisites are found through [tool queries](../harness/usage/tool-registry.md). This overview stays focused on research coverage as individual capabilities change.

[Source-audit notes](SOURCES.md) preserve dated evidence. A historical operation or a method description does not establish that a current task is ready to run.
