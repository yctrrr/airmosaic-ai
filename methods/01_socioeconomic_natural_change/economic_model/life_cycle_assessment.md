# Life cycle assessment: inventory and potential impacts

<!-- README-I18N:START -->

**English** | [中文](life_cycle_assessment_ZH.md)

<!-- README-I18N:END -->

Life cycle assessment (LCA) relates the inputs and outputs of a product system to potential environmental impacts across a defined life cycle. State the decision question and **functional unit** before comparing systems. The ISO 14040 framework separates goal and scope, life cycle inventory (LCI), life cycle impact assessment (LCIA), and interpretation. A climate indicator alone is one impact category, not a complete LCA. See [ISO 14040](https://www.iso.org/standard/37456.html) and the [UNEP Life Cycle Initiative](https://wedocs.unep.org/items/fcb30686-689c-49fd-afb3-48cf7868cfef).

## Specify the product system

Define the reference flow needed to deliver the functional unit, geographic and temporal coverage, technology, foreground and background processes, cutoffs, treatment of imports and end of life, and any allocation or system expansion for co-products. Record data sources and units for every process exchange. Comparing two products requires equivalent functions and compatible boundaries; a different inventory dataset or allocation rule can change the result without any physical change in the products.

In a simple linear, single-output foreground model, let the technosphere matrix `T` have products in rows and processes in columns, with positive production and negative consumed inputs. For demand vector `d`, process scales satisfy `T s = d`. If `B` contains elementary flows per process, the inventory is `g = B s`; characterization factors `c` for a defined impact category give `impact = cᵀ g`. These equations illustrate LCI and one LCIA category. Real assessments also require justified datasets, characterization methods, allocation and interpretation. [Brightway's matrix documentation](https://docs.brightway.dev/en/latest/content/overview/matrix.html) describes the corresponding technosphere, biosphere and characterization matrices.

## Connect to MFA, IO and CGE

MFA tracks physical flows and stocks through a stated system; its process quantities can inform an LCI after reconciling product and system boundaries. Environmentally extended IO can estimate upstream requirements when a monetary final-demand account is the starting point, while process LCA uses process exchanges and a functional unit; hybrid approaches require an explicit mapping and double-counting check. CGE may supply scenario-specific activity, prices or technologies, but a scenario output is not itself an LCA impact or a causal effect. See [MFA](material_flow_analysis.md), [IO](io/README.md) and [CGE](cge/README.md).

## Check and interpret

Check product and flow units, mass and energy plausibility where applicable, completeness, matrix balance, coverage of each elementary flow by the chosen characterization method, and sensitivity to uncertain inventory and allocation choices. Report impacts per functional unit and category with units, not as an unlabeled total. Do not interpret potential impact indicators as observed health outcomes or monetary costs. The [LCA skill](../../../skills/model/01_socioeconomic_natural_change/life-cycle-assessment/SKILL.md) demonstrates a limited synthetic linear calculation; full studies need their own data and review.

Public workflow precedents include [Tiangong LCA skills](https://github.com/tiangong-lca/agent-skills), which distinguish inventory review and model building, and the [K-Dense industrial-ecologist agent skill](https://github.com/K-Dense-AI/scientific-agents). Neither supplies data or impact factors to the local toy calculation.
