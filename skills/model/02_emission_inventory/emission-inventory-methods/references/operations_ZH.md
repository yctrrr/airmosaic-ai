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

## 从仓库根运行

选择已获授权的外部结果父目录。例如，已有 ASSETS 根配置好后，创建独立项目目录：

```powershell
$inventoryOutputRoot = Join-Path $env:AIRMOSAIC_ASSETS_DIR "results/inventory_example"
New-Item -ItemType Directory -Path $inventoryOutputRoot -Force | Out-Null
python skills/model/02_emission_inventory/emission-inventory-methods/scripts/calculate_inventory.py --input-root skills/model/02_emission_inventory/emission-inventory-methods/examples --input-json inventory.synthetic.json --output-root "$inventoryOutputRoot" --dry-run
python skills/model/02_emission_inventory/emission-inventory-methods/scripts/calculate_inventory.py --input-root skills/model/02_emission_inventory/emission-inventory-methods/examples --input-json inventory.synthetic.json --output-root "$inventoryOutputRoot"
```

`--input-json` 为明确 `--input-root` 内的相对 JSON 名，绝对路径和父级跳转拒绝。脚本拒绝链接/reparse 祖先、常见凭据目录名和任何 Git 仓库内的输出根。这是局部检查，不是完整授权或操作系统隔离机制；不检查个人配置、认证文件或环境秘密。

Dry-run 读取并验证所选完整输入，在内存计算数值，同时检查拟输出位置，不创建产物。成功返回 `status=validated`、`output_created=false`。实际执行新建 `<UTC YYYYMMDDHHmm>_<inventory_id>` 子目录，也可传新的可公开 `--run-name` 标识独立试验。同分钟同名已存在就失败，不覆盖；重试前检查原结果。`status=succeeded` 仅表示工程核算完成，不代表科学验收。

## 检查产物

| 文件 | 检查内容 |
|---|---|
| `emissions.csv` | 活动/技术/污染物分配活动及治理前、排放、去除 kg |
| `route_emissions.csv` | 路线份额、运行/捕集/去除参数与路线质量贡献 |
| `totals.csv` | 地区/年份/部门/污染物汇总，不跨污染物生成没有定义的总质量 |
| `quality.json` | 份额、单位/基准、质量平衡和汇总检查；科学验收仍为 `not_assessed` |
| `record.json` | 输入 SHA-256、方法、UTC 时间、Python 版本及无联网/凭据动作，不含绝对路径 |
| `artifacts.json` | 最终成功标记及其余五个文件的哈希 |

核对全部产物哈希，独立按污染物求和明细。合成输入预期 SO₂ 排放 24,664 kg、NOx 30,960 kg；SO₂ 治理前 92,000 kg，去除 67,336 kg。准确输入保留原授权位置并核对哈希不变。失败可能留下没有最终成功索引的本地部分文件，应保留调查，不能因 CSV 存在就验收。

实际 21 项合成测试覆盖预期数值、路线/明细/汇总一致、零运行/捕集/去除、全去除、零活动、同维质量/能源单位、错误份额/单位/基准/因子覆盖、非有限值、不覆盖、Git 输出、重复 JSON 键及链接输入。使用项目测试环境运行：

```sh
python -m pytest harness/checks/test_emission_inventory.py -q
```

真实输入和结果归获准外部资产，私人路径映射归 CONFIG_DIR，凭据归受保护机制。详细结果标识仍可能敏感，共享或登记新资产版本前需审核。本路径没有下载器、空间分配、串联联合状态推导、不确定性传播或 runner/MCP 适配器。
