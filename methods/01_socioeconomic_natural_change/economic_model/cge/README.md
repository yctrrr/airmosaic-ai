# Computable general equilibrium: accounts, behavior and closure

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

A CGE model starts from a balanced economic benchmark and adds explicit behavior and market-clearing equations. Its scenario result depends on production and demand functions, elasticities, closure and the shock. It does not become an observed causal effect merely because the benchmark is reproduced. For the fixed-coefficient accounting counterpart, see [IO](../io/README.md).

## CGE: from benchmark accounts to an equilibrium

A social accounting matrix (SAM) represents the benchmark economy. Each column records an account's spending and each row its receipts, so every account's total receipts equal total spending after balancing. An input-output table provides interindustry flows but must be completed with factor income, households, government, saving, investment and trade to form a full SAM. Specify the base year, region and sector classification, units and price basis before calibration.

The accounting logic is visible in two identities. For each SAM account, `total receipts = total spending`. For each good, `domestic output + imports = intermediate use + final use + exports`, after applying the model's treatment of inventories and trade. These identities constrain the answer; they do not determine how quantities respond when prices change.

The SAM supplies benchmark monetary flows and value shares; physical quantities require reference prices or separate data. Behavioral equations describe how agents respond away from that benchmark: producers choose inputs subject to a production function, households allocate their budgets across goods, and users may substitute between domestic and imported supply. Functional forms such as CES encode those substitution possibilities; their elasticities come from external evidence or explicit assumptions, not from one SAM alone. Prices adjust until goods and factor markets clear, institutional budgets balance, and production satisfies the model's pricing conditions. A **closure** states which variables are fixed and which adjust, such as labor supply, the trade balance, saving and investment. The closure is part of the experiment, not a technical afterthought.

Calibration chooses parameters so the observed benchmark satisfies the equations at reference prices. A comparative-static run solves a new equilibrium after a stated shock. A recursive-dynamic run links periods through explicit updates such as capital accumulation, population, labor supply and productivity; it does not make those paths endogenous unless their equations do so. The core comparison is the difference between a baseline and a scenario with the same accounting definitions and closure.

## Common terms

| Term | Meaning for model construction |
|---|---|
| Direct requirement and Leontief inverse | `A[i,j]` is input `i` per unit of output `j`; `(I − A)^−1` aggregates direct and indirect production requirements under the chosen coefficients. |
| Final demand | Household and government consumption, investment and exports in an IO table; in standard IO it is supplied to the calculation, while a CGE model may determine parts of it from incomes and prices. |
| Activity and commodity | An activity is a producer; a commodity is a good or service. Keeping them separate allows one activity to make several commodities or several activities to make one commodity. |
| Benchmark and calibration | The benchmark is the reference-year economy. Calibration sets share and scale parameters so the equations reproduce it; elasticities still need independent justification. |
| Endogenous and exogenous | Endogenous values are solved by equations; exogenous values are imposed. Changing an exogenous value defines a scenario only after the closure is specified. |
| CES, Leontief and nesting | CES allows substitution at a stated elasticity; Leontief fixes input proportions. A nest says which inputs may substitute at each level. |
| Armington and CET | Armington commonly distinguishes domestic and imported varieties in demand; CET can allocate domestic output between domestic sales and exports. Both are modeling assumptions. |
| Numeraire | A fixed reference price or price index sets the nominal scale. Interpret price changes relative to it. |
| Comparative static and recursive dynamic | Comparative static compares equilibria without an explicit transition path. Recursive dynamic solves successive periods with state updates, such as capital accumulation. |

The [IFPRI standard CGE manual](https://cgspace.cgiar.org/server/api/core/bitstreams/a3854265-05a5-408f-9eb6-4c8583069553/content) develops the accounts and equations in detail; the [GAMS MPSGE introduction](https://www.gams.com/latest/docs/UG_MPSGE_Intro.html) explains preferences, production, prices and equilibrium from a small example.

## Building CGE variants in GAMS

GAMS is a language for declaring indexed data, variables and equations and calling a solver; it is not a single CGE model. A practical build starts with sets for accounts, sectors and regions; a balanced SAM and benchmark prices; behavioral forms and elasticities; equations and closure; then a baseline solve, shocks and reports. Keep data balancing and model equations separately auditable. The [GAMS SAM balancing example](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_sambal.html) illustrates one possible balancing method, not a universal preprocessing rule.

There are two common equation-writing routes. In **algebraic GAMS**, declare `Sets`, `Parameters`, `Variables` and `Equations` explicitly. The [static `stdcge` example](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_stdcge.html) formulates its specific equilibrium as an NLP with a utility objective; the [recursive `dyncge` example](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_dyncge.html) adds a period loop and updates factor endowments and capital. NLP welfare maximization is a property of those formulations, not a requirement of every CGE model. An algebraic **MCP** instead pairs equilibrium inequalities with variables, including zero-profit, market-clearing and income-balance conditions.

In **GAMS/MPSGE**, declare sectors, commodity prices and consumers, then describe production and demand using benchmark flows and elasticities. MPSGE generates the equilibrium equations for a competitive constant-returns structure; auxiliary constraints can add conditions that its tables do not express directly. A typical source contains `$MODEL`, `$SECTORS`, `$COMMODITIES`, `$CONSUMERS`, `$PROD` and `$DEMAND`, followed by `$sysinclude mpsgeset`, the generated-file include and `solve ... using mcp`. Check benchmark replication before changing a parameter. See the [official MPSGE syntax and algebraic MCP comparison](https://www.gams.com/latest/docs/UG_MPSGE_Intro.html).

To change a model type, change the economics and data rather than merely the `solve` keyword:

| Variant | Required structural change | Minimum additional check |
|---|---|---|
| Multi-region | Region-indexed accounts, interregional or international trade and region-level closures | Bilateral flows and each region's accounts reconcile |
| Recursive dynamic | Period-specific baselines and state transitions for capital or other stocks | Updated stocks and flows agree between periods |
| Multiple households | Distinct factor ownership, transfers, consumption and saving by household | Household incomes and expenditures reconcile |
| Environmental | Physical activity and coefficients, plus an explicit satellite or feedback mechanism | Physical units and environmental identities reconcile |

The [World Bank's MANAGE-WB and CGEBox descriptions](https://www.worldbank.org/en/programs/economicpolicy-macro-modeling/cge) illustrate single-country and multi-country modular designs. Their modules and data are separate from CHEER.

## Choosing and linking the methods

| Question | Direct starting point | What must be added for a stronger claim |
|---|---|---|
| Which upstream sectors support a specified final demand, or where is its embodied impact? | IO/MRIO with documented coefficients and physical intensities | Test the assumed final demand, trade mapping and coefficient stability. |
| How does a shock change prices, input choices, incomes, trade and demand together? | CGE with an explicit SAM, behavior, closure and elasticities | Justify and test those assumptions; the answer is conditional on them. |
| How do supply-chain impacts change after an economy-wide adjustment? | CGE outputs followed by an IO or physical-account calculation | Reconcile sector mappings and avoid applying the same direct or indirect effect twice. |

An IO table can supply much of a CGE model's benchmark SAM, while IO remains useful for detailed supply-chain attribution after a CGE scenario. CGE can also retain Leontief nests where substitution is not assumed. Thus the distinction is the equations and what they hold fixed, not a claim that one method replaces the other. The [CEEEA2.0 authors' model](https://github.com/Zhijie-Jia/CEEEA2.0-CGE) illustrates the combination: it solves equilibrium outcomes and uses IO calculations for embodied emissions.

## Environmental applications

For a CGE application, map economic accounts to physical processes by sector, region, fuel or material, year and unit. An environmental **satellite account** can calculate indicators from IO output or CGE activity; it requires physical quantities or a defensible conversion from monetary results. A satellite indicator alone does not change an economic solution. Feedback requires an equation or constraint that connects the physical quantity to production, consumption, resources, policy, or productivity.

For example, with physical fuel quantity `Q[r,s,f,t]` and an emission coefficient `EF[r,s,f,p,t]`, a satellite calculation is `E[r,p,t] = sum(s,f) Q[r,s,f,t] × EF[r,s,f,p,t]`. The model must represent or derive `Q` with a documented physical unit; the coefficient and its interpretation require separate evidence. If `E` enters a limit or another equilibrium equation, changing that limit can alter `Q`, prices and income. If it is only reported afterward, it cannot do so. The [World Bank CGE documentation](https://www.worldbank.org/en/programs/economicpolicy-macro-modeling/cge) describes calibrating emissions coefficients to external inventories.

Choose the connection before coding. A one-way calculation applies physical intensities to CGE activity or energy outputs. An endogenous extension can represent an emissions limit, resource constraint, environmental tax, technology change, or climate-related productivity change in the equilibrium equations. A two-way link with an external energy, land, atmosphere or health model additionally needs a defined exchange of variables, units, spatial and temporal aggregation, and an iteration or one-pass rule. Do not interpret a one-way indicator as feedback, or add the same shock in both linked models.

For each scenario, specify the changed parameter or constraint, its baseline value, timing and coverage. Check the benchmark replication first; then inspect solver/model status, account and market balances, physical identities, and the direction and size of quantity and price responses. Report sensitivity to elasticities, closures and environmental coefficients. Export economic and physical outputs with model version, scenario, year, region, sector, units and a crosswalk; external models must retain their own definitions and validation. A successful solve alone does not validate an environmental result.

## Runnable model versus the external CHEER example

The [CGE skill](../../../../skills/model/01_socioeconomic_natural_change/cge/SKILL.md) includes an independently authored, synthetic, closed-economy numerical tutorial. It starts with a balanced SAM, calibrates production and household budget shares, fixes a wage numeraire, reproduces a zero-shock benchmark and solves a productivity scenario. Its intermediate inputs are fixed; labor and capital substitute through Cobb-Douglas value added, and household consumption responds to income and prices. A one-way emission coefficient produces a satellite indicator after equilibrium. This establishes the calculation sequence, not a calibrated China model or CHEER reproduction. The toy has no trade, government, investment, multiple households or dynamics; those require new accounts and equations, not only more SAM rows.

## CHEER as the first operational example

CHEER is a model family; GAMS is its modeling platform, MPSGE is a GAMS equilibrium-modeling subsystem, and MCP is a solve type. The public CHEER and CHEER-P packages are demos, so distinguish the files actually supplied from later model descriptions. The reviewed CHEER-P demo declares a 2012 base year, 30 region labels and 11 sectors, while the [CHEER-P website](https://cheer.org.cn/model-structure/extension/) describes a later 2017-base, 31-province version. Environmental variables and equations vary by release; inspect the active source before attributing a module to a particular demo.

Read the [CGE skill](../../../../skills/model/01_socioeconomic_natural_change/cge/SKILL.md) for model design, source mapping, optional manual reproduction and environmental scenario checks. [CGE Model Extensions](../../../../skills/model/01_socioeconomic_natural_change/cge/references/model-extension-cases.md) maps these concepts to the reviewed demo's classification, calibration, behavior, equilibrium, dynamic, environmental and reporting modules. CHEER is its currently reviewed example. Primary references: [CHEER releases](https://cheer.org.cn/downloads/), [CHEER model variants](https://cheer.org.cn/model-structure/extension/), [GAMS MPSGE](https://www.gams.com/latest/docs/UG_MPSGE_Intro.html), and [GAMS model/solve semantics](https://www.gams.com/latest/docs/UG_ModelSolve.html).

The published [general-equilibrium model-builder skill](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/main/skills/31-thalysandratos-claude-code-skills/_skills/theory/general-equilibrium-model-builder/SKILL.md) informed the sequence of defining agents, endowments and market clearing before computation. That skill currently implements pure exchange in Julia; CHEER's production, SAM calibration and GAMS solution are separate and require their own source review.
