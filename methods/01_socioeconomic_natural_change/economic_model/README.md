# Economic models and linked physical accounting

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

`economic_model` is this project's navigation group for methods that describe the economy and its resource or environmental links. It is not a claim that every method here is an economics model: input-output (IO) analysis is an accounting model, computable general equilibrium (CGE) solves a specified economic equilibrium, econometrics estimates relationships from data, material flow analysis (MFA) tracks physical flows and stocks, and life cycle assessment (LCA) evaluates a product system's potential environmental impacts.

| Method | Main question | Read |
|---|---|---|
| IO | Which upstream production and physical footprints correspond to stated final demand? | [Input-output analysis](io/README.md) |
| CGE | How might prices, quantities, incomes and trade adjust to a specified shock? | [Computable general equilibrium](cge/README.md) |
| Econometrics | Which associations, predictions or identified effects are supported by observed variation? | [Econometric analysis](econometrics/README.md) |
| MFA | Where do materials enter, move through, accumulate in, and leave a defined system? | [Material flow analysis](material_flow_analysis.md) |
| LCA | What potential impacts are associated with a stated product function and life-cycle boundary? | [Life cycle assessment](life_cycle_assessment.md) |

The methods can share sector and region mappings, but their monetary and physical accounts, system boundaries, and assumptions need separate checks. A link between two methods does not itself create an economic or environmental feedback. See the [stage 01 methods](../README.md) and [methods index](../../index.yaml) for their project roles. [SEEA](https://seea.un.org/en/methodology/seea-central-framework) provides the broader environmental-economic accounting context; [ISO 14040](https://www.iso.org/standard/37456.html) describes the LCA framework.

Related public skills include the [K-Dense industrial-ecologist agent skill](https://github.com/K-Dense-AI/scientific-agents), which organizes MFA, IO and LCA around system boundaries and mass balance, [Tiangong LCA skills](https://github.com/tiangong-lca/agent-skills), [EconAgentSkills](https://github.com/JonasWeinert/EconAgentSkills), and a [general-equilibrium model-builder skill](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/main/skills/31-thalysandratos-claude-code-skills/_skills/theory/general-equilibrium-model-builder/SKILL.md) whose pure-exchange scope is narrower than CGE. The open-source calculation projects [pymrio](https://pymrio.readthedocs.io/en/stable/), [flodym](https://flodym.readthedocs.io/en/latest/) and [Brightway](https://docs.brightway.dev/en/latest/) provide method-specific software. The small scripts linked by local skills are independent demonstrations; they do not bundle those packages or their databases.
