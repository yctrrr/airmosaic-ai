# CGE 模型拓展

[English](model-extension-cases.md) | **中文**

本页用于**构建或扩展模型**；运行外部压缩包和记录求解证据见 [CHEER GAMS 操作指南](cheer-gams-operations_ZH.md)。以下 CHEER 文件映射来自对下载演示包的源码检查，不能代替实际 GAMS 求解。取得另一版本时，先沿 `run.gms` 重新追踪生效的 `$include`、数据文件和情景开关。

## 从哪一个公开案例开始

| 案例 | 能学到的构建步骤 | 边界 |
|---|---|---|
| [公开的 general-equilibrium-model-builder skill](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/main/skills/31-thalysandratos-claude-code-skills/_skills/theory/general-equilibrium-model-builder/SKILL.md) | 两种商品、两位消费者的 Julia 纯交换例子：禀赋与偏好 → 需求 → 选计价基准 → 求超额需求为零 → 验证市场出清。它在 skill 文本里给出代码。 | 只实现 Cobb-Douglas 纯交换；生产、SAM、贸易和动态列为未来扩展。不要把它当作可运行的 CHEER 技能。 |
| [GAMS/MPSGE 两商品两要素教学例子](https://www.gams.com/latest/docs/UG_MPSGE_Intro.html) | 从生产和消费者账户走到 `$SECTORS`、`$COMMODITIES`、`$CONSUMERS`、`$PROD`、`$DEMAND`，并对照代数式 MCP。 | 小型教学经济；需要自己准备研究所需的 SAM 与参数。 |
| [GAMS `stdcge`](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_stdcge.html) → [`dyncge`](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_dyncge.html) | 静态例子展示 SAM、贸易、税、校准和情景；动态例子展示时间集合、折旧、资本与劳动路径。安装 GAMS 后可在仓库外运行 `gamslib stdcge`／`gamslib dyncge` 复制官方例子，再运行相应 `.gms`。 | 这是**公开模型库案例**，不是 agent skill；其方程、求解类型和数据与 CHEER 不同。命令格式见 [GAMS 模型库指南](https://www.gams.com/latest/docs/UG_ModelLibraries.html)。 |
| [本仓库的合成 CGE 教学脚本](../SKILL_ZH.md#运行合成数值模型) | 平衡 SAM → 校准 → 零冲击复现 → 生产率情景 → 一方向环境卫星账户；有实际 Python 输入、脚本和检查输出。 | 简化封闭经济，不含 CHEER 的地区间贸易、政府或动态。 |

因此学习路径是：先理解纯交换的均衡检查，再用 `stdcge` 理解 SAM 与生产贸易，用 `dyncge` 理解跨期更新，最后对照 CHEER 实际启用的 MPSGE 代码。各案例不能共用一套参数或直接互相替换源码。

## 哪些数据可以借鉴

| 数据 | 可用于什么 | 使用前要核对什么 |
|---|---|---|
| [GAMS `stdcge`](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_stdcge.html) 和 [`dyncge`](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_dyncge.html) 源码内嵌 SAM | 最适合学习账户到基准变量的映射、校准和动态更新；不依赖外部中国数据即可检查教学模型。 | `stdcge` 为两商品例子，`dyncge` 为四商品例子；均不能当成中国经济参数。使用官方模型库命令在仓库外取得原件。 |
| `CHEER-P_demo` 发布包中的 `data.gdx`、`emission_r11.gdx`、趋势 GDX 和工作簿 | 学习 2012 基年、30 地区、11 部门的地区间流量、CO₂ 基准映射和 SSP 动态路径；追踪 `cal.gms` 加载的 `int_ag`、`va_ag`、`fd_ag`、`imp_ag`、`exp_ag`。 | 实际运行读的是 GDX；Excel 工作簿不应未经核对就当作对应 GDX 的原始输入。完整演示包在技能外取得和运行。 |
| 技能内[电力拆分工作簿](../assets/cheer_clean_electricity_example/v1/benchmark.xlsx) | 核对总部门电力账户到技术活动的映射。 | 使用内置工作簿和[来源元信息](../assets/cheer_clean_electricity_example/v1/source.json)；该文件是教学摘录，不是完整 SAM。 |
| [CEADs 2012／2015／2017 省级 MRIO](https://zenodo.org/records/4569117)；[2018／2020 MRIO](https://pmc.ncbi.nlm.nih.gov/articles/PMC12890965/) | 构建新的中国多地区 CGE 的部门间交易、最终需求和部分增加值基底；后者还公开了[构表代码](https://github.com/LiJie20230/China_MRIO)。 | 与演示包的 30 地区／11 部门分类不同，必须建立地区及行业映射，补齐居民收入、税收转移、储蓄投资、要素所有权和闭合规则，并校核／平衡 SAM。2018／2020 论文报告的部门总产出核算误差并非严格为零，不能原样当作已平衡的 CGE 基年。 |

首个可复核案例可用仓库现有的**合成 SAM 和 Python 脚本**检验输入格式及基准复现；技能自带的 CHEER-Clean 工作簿用于检查技术账户如何形成；要学习较完整的公开账户，使用 `stdcge`；要搭建新的中国基年，再选定一个来源明确的 MRIO 年份并单独完成 SAM 构建。不要把不同来源的数据直接合并成一个已校准模型。

## CHEER 演示包的实际模块图

源码检查显示，`CHEER-P_demo` 的 `run.gms` 依次启用 `sets.gms`、`cal.gms`、`elasticities.gms`、`emission.gms`、`parshock.gms`、`partrend.gms`、`core.gms`、`dyncal_CER.gms`、`dyn_CER.gms`；静态和 BAU 行在该入口中被注释。该包的源码标注 2012 基年，定义 30 个地区标签、11 个商品部门。这与[官网介绍的较新 CHEER-P 结构](https://cheer.org.cn/model-structure/extension/)所述 2017 基年和 31 省不同。要复现哪个版本，就使用该版本的数据和代码。

| 模块 | 此演示包中的位置 | 扩展时要一起检查的内容 |
|---|---|---|
| 分类与地区 | `sets.gms` | `i`、`r`、能源／资源子集、要素和时间索引；全部输入符号的维度与名称。 |
| 基准数据与校准 | `cal.gms`、`data.gdx` | `int_ag`、`va_ag`、`fd_ag`、进口与出口；构造的 `int0`、`fact0`、`cons0`、`inv0`、`output0` 与地区间贸易。核对货币单位转换、账户与贸易平衡。 |
| 行为参数 | `elasticities.gms` | 每层生产／消费替代弹性及来源、未赋值项、零流量分支；做弹性敏感性分析。 |
| 均衡与闭合 | `core.gms` | 实际启用的 MPSGE 生产、Armington 供给、消费、投资、代表性主体、商品／要素价格、碳价和约束；核对参考价格和出清。 |
| 环境核算 | `emission.gms`、`emission_r11.gdx`、`core.gms` | 原始 CO₂ 到地区—部门—燃料基准量的映射及 `check0`；判断排放量是报告值，还是进入 `pco2` 和碳约束。 |
| 情景与递归动态 | `parshock.gms`、`partrend.gms`、`dyncal_CER.gms`、`dyn_CER.gms` | 哪个开关或路径在运行入口中生效；劳动、TFP、能效和碳目标；每期求解后投资与资本存量的连接。 |
| 报告 | `report_dynamic.gms` | 地区／部门／年份输出、价格、劳动、贸易、CO₂ 和模型状态；确保新变量带单位和覆盖范围。 |

`CHEER_demo` 中的 CHEER-Clean 给出一个**确实写在演示源码里的技术拆分案例**：`Code/Sets.gms` 定义 `sub_elec` 发电和输配电子类，`Code/electricity.gms` 读取分技术投入、发电量、补贴及电价并校准，`Model/core_Developing_Arminton.gms` 定义分技术生产活动 `yelec(sub_elec)` 及其投入嵌套，`Report/report_dynamic.gms` 报出技术产量与价格。`run.gms` 中这些文件处于启用的 include 路径。这里确认的是**代码结构**；压缩包中的历史输出文件和静态预检不能证明当前环境已重新求解。官网也介绍了[CHEER-CLEAN 的电力技术细分](https://cheer.org.cn/model-structure/extension/)。

### 复核技能内的 CHEER-Clean 电力工作簿

[内置工作簿](../assets/cheer_clean_electricity_example/v1/benchmark.xlsx)包含 [source.json](../assets/cheer_clean_electricity_example/v1/source.json) 所述的教学摘录，由脚本自动读取。结构为：`IO` 含 `Elec`、`SUM_INPUT` 和 `SUM_OUTPUT`，`ELEC` 含技术列及商品、`labor`、`capital`、`tax` 行。货币单位沿用工作簿；该示例不提供实物发电量或完整 SAM。

准备 [requirements.txt](../requirements.txt) 中的依赖后，在仓库根目录运行[核算脚本](../scripts/audit_cheer_electricity_split.py)：

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/cge-cheer-electricity-accounting'
python skills/model/01_socioeconomic_natural_change/cge/scripts/audit_cheer_electricity_split.py --out-dir $out
```

`$out` 须是新目录且在所有 Git 仓库外。检查 `electricity_technologies.csv`、`input_reconciliation.csv` 和 `validation.json`：各技术投入须与父电力账户一致，控制总量须闭合，货币价值份额不能当成发电量份额。脚本支持的两组标签重分类为 `AgriPr`/`FrsPr` 和 `Biofuel`/`OthMfg`。保留脚本记录的输入标识。这是基年账户核算，不是完整 CHEER 求解。

## 一次扩展应如何落地

**例 1：把一个部门拆为若干技术活动。** 先决定是否需要新的*商品*：多种技术可生产同一商品，通常先增加活动索引和分技术生产结构，而不必把每项技术都变成独立的最终商品。收集分技术基年产出、投入、要素、税／补贴和实物量，核对加总回原部门。仿照 CHEER-Clean 上述四个文件，在集合、技术校准、生产／供给嵌套和报告中同步增加索引；如有技术容量、固定要素或替代弹性，还需说明其数据来源及对应约束。重校准后检查基年每种技术的成本与收入、合计部门产量和商品／要素市场出清，然后才施加技术冲击。**仅在 `sets.gms` 增一个名称不会产生新的经济技术。**

**例 2：增加多个居民类型。** 先把基年居民消费、劳动与资本所有权、税收、转移和储蓄按类型分配，使每类预算及合计 SAM 平衡。然后在 `core.gms` 中把单一 `ra`、`consum(r)` 相关需求和禀赋映射改成带居民索引的表达，选择工资、就业、转移及消费规则；再扩展报告，检查各类预算平衡和总量回加。仅把消费列拆开，不能得到收入分配效应。[CHEER-HI 与 CHEER-PPS 的官网结构](https://cheer.org.cn/model-structure/extension/)可作研究设计参照，不意味着当前 CHEER-P 演示包已含这些细分。

**例 3：新增环境模块。** 第一阶段是单向核算：将基准活动或燃料实物量映射到地区、部门和污染物，用有来源的排放系数形成 `E = Σ(Q × EF)`，核对清单总量并在报告中输出。第二阶段若要让环境改变经济均衡，应明确一种机制及其数据：排放约束及配额价格、排放税与收入去向、技术投入与资源占用，或环境影响劳动／生产率。将相应价格、投入或约束写入 `core.gms`，在 `parshock.gms`／`partrend.gms` 指定情景；有跨期反馈再核对 `dyn_CER.gms` 的时序。CHEER-P 演示包已经有 **CO₂ 价格和碳约束** 的 MPSGE 连接；不能据此声称其含空气污染物、空气质量或健康反馈。官网 [CHEER-HE](https://cheer.org.cn/model-structure/extension/)所述空气质量—健康—劳动链路属于另一模型配置。

**例 4：扩展地区与动态。** 新地区要求完整的双边中间投入、居民／投资需求、要素禀赋和跨境贸易核算；逐地区 SAM 与双边贸易两边应一致。新增年份或改变时间步长时，应同步调整 `sets.gms` 时间集合、`partrend.gms` 外生路径和 `dyn_CER.gms` 的资本折旧／劳动更新指数。不能只延长年份标签，因为原代码首期用 3 年、其后用 5 年的更新跨度。

每次只增加一个可核对的结构变化：保存原版与修改版的输入和代码差异，先跑零冲击基准，再核对价格、活动、预算和市场残差，最后跑情景并检查方向、单位及敏感性。报告应区分源码映射、合成教学运行、CHEER 原版数值复现和扩展版数值验证。
