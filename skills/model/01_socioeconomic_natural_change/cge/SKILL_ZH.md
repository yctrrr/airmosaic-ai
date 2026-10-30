---
name: cge
description: 运行内置合成 CGE 教学模型，设计或审阅一般均衡模型，并在运行环境齐备时复现已提供的模型；CHEER 是外部 GAMS 实例。
compatibility: "Python 3.10+ with NumPy/SciPy for the synthetic tutorial; external GAMS, solver, license and model data for CHEER; no registered AirMosaic tool"
metadata:
  version: "0.2.0"
---

# 设计、审阅和复现 CGE 模型

[English](SKILL.md) | **中文**

运行合成 CGE 教学模型、设计 CGE 模型、审阅已提供的源码，或复现基准与情景时使用。底层原理先看 [CGE 方法](../../../../methods/01_socioeconomic_natural_change/economic_model/cge/README_ZH.md)。CHEER 与 CHEER-P 是仓库外的 GAMS 源码实例。本技能有直接 Python 脚本，但没有注册 AirMosaic tool ID；不内置 CHEER 源码、GAMS、求解器许可证或真实 SAM。

## 运行合成数值模型

已审阅的 [Python 脚本](scripts/run_toy_cge.py)读取[清单登记的合成 SAM](../../../../assets/data/01_socioeconomic_natural_change/SyntheticCGE/v1/sam.csv)、情景表和环境卫星系数。它校准含对应活动/商品账户、两种要素和一个家庭的封闭经济模型；中间投入比例固定，增加值与家庭需求使用 Cobb-Douglas 形式，其替代弹性 1 是**预设假设**，不是从 SAM 估计出来的。以工资为计价基准。脚本检查 SAM 平衡，复现零冲击基准，再求解价格、产量和要素需求会变化的生产率情景。排放卫星账户仅在求解后计算，不反馈均衡。

在仓库根目录使用 Python 3.10+ 环境和 [requirements.txt](requirements.txt) 中的依赖，将 `AIRMOSAIC_ASSETS_DIR` 指向**仓库外**已存在的目录，并选择新输出目录：

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/cge-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/cge/scripts/run_toy_cge.py --input-dir assets/data/01_socioeconomic_natural_change/SyntheticCGE/v1 --out-dir $out
```

检查 `calibration.csv`、`equilibrium.csv`、`summary.csv` 和 `validation.json`。基准必须复现两个部门各 100 单位的产出与 1 的价格；合成排放总量为 50 kg。`food_productivity_reduction` 情景中，食品生产率乘数为 0.9，食品产出约 92.77，价格指数约 1.08485。脚本在写入结果前拒绝不平衡或超出支持范围的 SAM、缺失情景、非正生产率和已存在或位于 Git 内的输出目录。用 [toy-manifest.json](../../../../assets/toy-manifest.json)核对输入哈希。这是**该教学模型**的数值运行，不是 CHEER 或真实经济的复现。

[电力技术拆分工作簿](assets/cheer_clean_electricity_example/v1/benchmark.xlsx)已包含在本技能中，由[核算脚本](scripts/audit_cheer_electricity_split.py)直接读取。命令、输入结构及产物检查见 [CGE 模型拓展](references/model-extension-cases_ZH.md)。该示例复核基年技术账户，不求解完整 CHEER 模型。工作簿来源及独立的数据许可状态记录在 [source.json](assets/cheer_clean_electricity_example/v1/source.json)中。

## 搭建新模型

先明确问题、地区和部门尺度、基年、主体、商品、要素、贸易及时间结构。取得来源明确的社会核算矩阵（SAM），校准前检查行列平衡。写明行为嵌套、税收与转移、市场出清、价格归一化、宏观闭合和弹性来源；再用合适的建模语言实现、校准基准，并要求零冲击求解复现 SAM，之后才解释政策冲击。逐项标注观测数据、校准值、外部估计参数和情景假设。完成模型设计不等于完成数值运行。

## 确认实际取得的模型

1. 在 Git 仓库外对任务提供的模型源码建立隔离工作副本。记录来源网址或出处、压缩包标识、声明的版本、文件清单及基年。不要用官网当前介绍代替实际取得的版本。完整第三方源码、原始输入数据库和运行结果留在仓库外；技术账户示例使用技能自带工作簿。
2. 找到实际运行入口，沿建模语言中启用的包含语句和数据引用追踪代码。已审阅的 CHEER-P 演示包可从 `run.gms`、`sets.gms`、`cal.gms`、`elasticities.gms`、`emission.gms`、`core.gms`、动态文件及报告文件入手；其他 CGE 项目的名称和语言会不同。区分执行语句、注释和未调用文件。
3. 绘制源码映射：地区、部门、居民、要素、资源和年份集合；基年 SAM／IO 输入；校准与弹性来源；生产和消费嵌套；市场出清与定价方程；闭合规则；动态更新；情景冲击和报告变量。保留单位与定义。SAM 记录货币流量，须核对转成实物量的依据。单独追踪环境变量，判定其属于输出指标、均衡方程输入，还是与外部模型交换的变量。

## 依赖齐备后再复现

4. 运行前检查该模型所需的运行时、求解器、许可证、引用数据和隔离输出目录。对 GAMS/MPSGE 模型，还要核对版本、相对路径及文件名大小写；已审阅 CHEER 演示包的部分小写默认路径与压缩包中的目录名大小写不完全一致。只通过已确认的入口在隔离副本中运行。`gams run.gms lo=2` 只是 GAMS 项目确以 `run.gms` 为入口时的示例，不是通用 CGE 命令。保留原始文件并记录准确命令、日志及报告。
5. 检查求解器和模型状态、列表文件或等价诊断，再与来源基准核对 SAM 平衡、市场与预算残差、部门和地区总量、价格、数量及单位。求解成功而基年不符，不能称为复现完成。缺少依赖或基年差异尚未解释时，停在源码审阅并报告缺口。

## 设计并检查环境应用

6. 选择明确的连接方式：根据均衡活动量计算环境指标的卫星账户；写入 CGE 方程的内生约束或反应；或与外部物理模型交换变量。声称某个版本已有该功能前，须追踪实际启用的源码方程与数据。扩展模型时说明物理与经济部门的映射、单位、基年系数、改变的参数或约束、时间和覆盖范围。可研究能源或资源约束、环境税、技术变化、气候影响下的生产率变化等情景。
7. 在相同核算定义和闭合规则下求解配对的基准与情景。检查账户和市场平衡及相关环境恒等式，再按版本、情景、年份、地区和部门报告活动量、能源或资源使用、价格、收入等所需结果。区分单向环境指标与反馈。接入外部模型时说明交换变量、分类映射，以及单次传递或迭代方式。检查关键弹性、闭合规则和环境系数的敏感性。

报告工作达到**模型设计**、**源码审阅**、**数值复现成功**还是**科学检查过的情景分析**，并附相应证据。[CHEER 下载页](https://cheer.org.cn/downloads/)与 [GAMS MPSGE 文档](https://www.gams.com/latest/docs/UG_MPSGE_Intro.html)是上游依据，不能替代本地运行验证。

公开的[一般均衡模型构建技能](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/main/skills/31-thalysandratos-claude-code-skills/_skills/theory/general-equilibrium-model-builder/SKILL.md)为主体、禀赋和市场出清的推理顺序提供参照。其 Julia 代码只实现 Cobb-Douglas 纯交换经济。涉及生产、SAM、动态和 CHEER 文件修改时，按[案例与扩展指南](references/model-extension-cases_ZH.md)定位对应模块，不把纯交换求解当作 CHEER 复现。
