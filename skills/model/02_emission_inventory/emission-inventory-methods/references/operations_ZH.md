# 配置并运行活动—技术—治理核算

[English](operations.md) | **中文**

[方法](../../../../../methods/02_emission_inventory/emission_accounting_ZH.md)解释科学选择。直接[脚本](../scripts/calculate_inventory.py)仅依赖 Python 3.10+ 标准库，不是注册工具，不能调用 `run-tool emission-inventory-methods`。

## 准备一个显式输入

先使用完整[合成 JSON](../examples/inventory.synthetic.json)。根字段为 `schema_version=1`、`dataset_kind`（`synthetic` 或 `prepared_inventory`）、可公开的 `inventory_id`、污染物列表及下列四表。`dataset_kind` 只是调用者声明，不证明合成来源或访问授权；不会自动寻找或嵌入真实数据。

| 表 | 必填字段 |
|---|---|
| `activities` | `activity_id`、`region`、`year`、`sector`、`process`、`amount`、`unit`、`activity_basis`、`source_ref` |
| `technologies` | `activity_id`、`technology_id`、`activity_share`、`source_ref` |
| `factors` | `activity_id`、`technology_id`、`pollutant`、`value`、`mass_unit`、`activity_unit`、`activity_basis`、`control_basis`、`source_ref` |
| `control_routes` | `activity_id`、`technology_id`、`pollutant`、`route_id`、`route_share`、`operating_fraction`、`capture_fraction`、`removal_efficiency`、`source_ref` |

所有比例均为 `[0,1]` 小数，不是百分数。技术份额在同一活动内合计为一；治理路线在同一技术/污染物内合计为一，包含明确的未治理路线。不静默归一化。每项技术对每个声明污染物都需一个因子和完整路线。重复键、未知记录、缺失/非有限值、负活动/因子以及已含治理的因子均拒绝。

活动及因子分母单位支持 `kg`、`tonne`、`GJ`、`TJ`、`MWh`、`unit_product`，因子分子支持 `g`、`kg`、`tonne`。仅同维换算：`1 tonne=1000 kg`、`1 TJ=1000 GJ`、`1 MWh=3.6 GJ`。因子与活动的 `activity_basis` 必须一致，单位相同不证明物理口径相同；不推断热值、密度或化学组分转换。输出质量均为 kg。表字段严格匹配，真实数据映射及额外元数据归单独审查的准备步骤。

整理输入保留实际引用、产品/工艺定义和来源版本。自带例子的因子和占比全部声明合成，真实任务经批准后明确替换，不作为默认因子。输入 JSON 上限 1 MiB，每表最多 10,000 行；首版是有界核算助手，不是全国流式清单引擎。

## 计算前将通用源表映射到四表

在外部输入旁保留以 `source_ref` 为键的准备台账：原始生产者/出版物、版本、表页或记录编号、时空范围、原字段和单位、换算/加权、排除项及审核判断。JSON 用稳定短引用，不写个人路径或带签名下载链接。台账由调用者准备，不是第五张计算表，也不是自动来源核验。

1. 按互不重叠的地区/年份/部门/过程/物料口径建立 `activity_id`，将报告数量映射到 `amount`，只按有依据的单位换算，并与选定范围的来源总量核对。不同燃料/产品保留独立活动单元；不能将产品产量和燃料投入作为同一过程排放重复计算。
2. 用技术对应处理量除以相同口径活动总量得到 `activity_share`，以 `activity_id` 关联。只有产能或设备数时，暂停该映射，等待利用率/处理量证据；不将缺失技术填零。
3. 每个 `(activity_id, technology_id, pollutant)` 选择一个适用未治理因子，保留原分子/分母单位、物料基准和引用。台账记录污染物表达，如 NOx 的 NO2 当量或 PM 粒径/组分。脚本检查标签和维度，不核验化学含义，也不证明来源因子确实未含治理。
4. 按污染物分别将技术处理量分成互斥 `route_id` 状态。已知处理量覆盖率 `f` 可映射为 `route_share=f`，确认未治理的补集另设路线，份额为 `1-f`，并令 `operating_fraction=0`、`capture_fraction=0`、`removal_efficiency=0`。仅在已核实穷尽的两状态划分下才可取补集；未知覆盖不等于未治理。治理路线的活动量加权有效运行映射到 `operating_fraction`，运行时捕集比例映射到 `capture_fraction`，捕集流去除率映射到 `removal_efficiency`。代码不解释 `uncontrolled` 等路线标签，由数值字段决定排放。
5. 百分数除以 100，检查关联和完整污染物覆盖，再写严格四表 JSON。保留运行/捕集/去除的联合证据，分别无条件平均后相乘可能有偏；状态差异显著时，依据审核证据细分路线或活动，不编造单一有效率。

真实清单运行前，必须在授权范围内用台账解决缺失、边界不兼容和因子治理状态问题。合成示例仅提供虚构证据，不替代真实来源映射。

## 从仓库根运行

选择已获授权的外部项目结果父目录。在调用会话中将非秘密变量 `INVENTORY_PROJECT_RESULTS` 设为该位置；脚本不会自动加载这个变量：

```powershell
$inventoryOutputRoot = $env:INVENTORY_PROJECT_RESULTS
if (-not $inventoryOutputRoot) { throw "Set INVENTORY_PROJECT_RESULTS to an authorized external project result parent" }
New-Item -ItemType Directory -Path $inventoryOutputRoot -Force | Out-Null
python skills/model/02_emission_inventory/emission-inventory-methods/scripts/calculate_inventory.py --input-root skills/model/02_emission_inventory/emission-inventory-methods/examples --input-json inventory.synthetic.json --output-root "$inventoryOutputRoot" --dry-run
python skills/model/02_emission_inventory/emission-inventory-methods/scripts/calculate_inventory.py --input-root skills/model/02_emission_inventory/emission-inventory-methods/examples --input-json inventory.synthetic.json --output-root "$inventoryOutputRoot"
```

`--input-json` 为明确 `--input-root` 内的相对 JSON 名，绝对路径和父级跳转拒绝。脚本拒绝链接/reparse 祖先、常见凭据目录名和任何 Git 仓库内的输出根。这是局部检查，不是完整授权或操作系统隔离机制；不检查个人配置、认证文件或环境秘密。

Dry-run 读取并验证所选完整输入，在内存计算数值，同时检查拟输出位置，不创建产物。成功返回 `status=validated`、`output_created=false`。实际执行新建 `<UTC YYYYMMDDHHmm>_<inventory_id>` 子目录，也可传新的可公开 `--run-name` 标识独立试验。同分钟同名已存在就失败，不覆盖；重试前检查原结果。`status=succeeded` 仅表示工程核算完成，不代表科学验收。

## 检查产物

| 文件 | 检查内容 |
|---|---|
| `emissions.csv` | 分配活动、技术份额、因子及换算后分母、活动基准、来源引用与治理前、排放、去除 kg |
| `route_emissions.csv` | 路线份额、运行/捕集/去除参数、来源引用与路线质量贡献 |
| `totals.csv` | 地区/年份/部门/污染物汇总，不跨污染物生成没有定义的总质量 |
| `quality.json` | 份额、单位/基准、质量平衡和汇总检查；科学验收仍为 `not_assessed` |
| `record.json` | 输入及脚本 SHA-256、方法、UTC 时间、Python 版本及无联网/凭据动作，不含绝对路径 |
| `artifacts.json` | 最终成功标记及其余五个文件的哈希 |

核对全部产物哈希，独立按污染物求和明细。合成输入预期 SO₂ 排放 24,664 kg、NOx 30,960 kg；SO₂ 治理前 92,000 kg，去除 67,336 kg。准确输入保留原授权位置并核对哈希不变。失败可能留下没有最终成功索引的本地部分文件，应保留调查，不能因 CSV 存在就验收。

实际 22 项合成测试覆盖预期数值、可复算因子/来源审计列、路线/明细/汇总一致、零运行/捕集/去除、全去除、零活动、同维质量/能源单位、错误份额/单位/基准/因子覆盖、非有限值、不覆盖、Git 输出、重复 JSON 键及链接输入。使用项目测试环境运行：

```sh
python -m pytest harness/checks/test_emission_inventory.py -q
```

任务输入和结果归获准的外部项目，私人路径映射归 CONFIG_DIR，凭据归受保护机制。详细结果标识仍可能敏感，人类科学审核后再决定是否纳入资产；本例不规定资产内部结构。本路径没有下载器、空间分配、串联联合状态推导、不确定性传播或 runner/MCP 适配器。
