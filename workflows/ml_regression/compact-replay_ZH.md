# 小型空间回归复现

[English](compact-replay.md) | **中文**

本组合衔接[小时站点整理](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/hourly-preparation_ZH.md)、[网格日均和双线性提取](../../skills/model/shared/spatial_analysis/references/python-path_ZH.md)以及[分组调参](../../skills/model/shared/machine_learning_model/references/automatic-tuning_ZH.md)。数值运算保留在相应技能。[示例程序](examples/compact_spatial_regression.py)负责生成合成输入和检查交接；它们是直接运行的程序，没有新增工具 ID、执行器适配器或 MCP 权限。

## 控制示例体量

先选择有历史位置依据的少量站点及小范围，再请求网格产品。季节变化是关键环节时保留完整研究日历。合成示例使用 8 站和 2024 年全部 366 天，以检查闰日和跨年对齐；这些数量不是模型默认条件，也不说明具有全国代表性。

| 只保存一份 | 作用 |
|---|---|
| 所选站点的原小时标签和数值 | 重算实测小时数与日均目标 |
| 必需的原生网格节点、时间、轴、单位及缺失标记 | 重算完整采样日均与双线性特征 |
| 站点及来源元数据、权重、日表、分组与折分 | 核对身份及各环节交接 |
| 审核计划、实际代码、技能哈希、环境、搜索设置及种子 | 无须凭记忆重设方案即可重新拟合 |
| 搜索摘要、冻结后的测试/网格预测及指标 | 独立核对选型和评估 |

所有模型共用一份整理表，不按模型重复保存输入，不保存每折拟合模型。保留来源精度：示例明确生成 float32 字段，不意味着可以降低真实产品精度。哈希用于确认身份，不能恢复已省略的数据。保存的节点是合成输入的无损子集，不能替代上游完整归档。Quotsoft 的日文件覆盖全国，选列减少的是本地保存和重复复现的体量，不一定减少首次传输量。

批准预算除调参和最终拟合外，还需计入验证时重新训练的次数。没有剩余重拟合预算时，可重建输入和指标，并用已有冻结模型核对预测，不隐式重复搜索。

## 不下载数据的运行方式

任务环境需要 NumPy、pandas、SciPy 和 scikit-learn 1.4+，不要隐式向共享环境安装依赖。程序记录精确版本，复算检查要求版本和技能哈希保持一致。从仓库根目录运行，并指定新的外部结果位置：

```powershell
$compactRoot = Join-Path $env:TEMP "airmosaic-compact-check"
$compactStamp = Get-Date -Format "yyyyMMddHHmm"
$compactRun = Join-Path $compactRoot ($compactStamp + "_spatial_regression")
$compactReplay = Join-Path $compactRoot ($compactStamp + "_frozen_replay")
python workflows/ml_regression/examples/compact_spatial_regression.py --repo . --out "$compactRun"
python workflows/ml_regression/examples/check_compact_spatial_replay.py --repo . --source "$compactRun" --out "$compactReplay"
```

已有结果或任何 Git 祖先之下的输出均拒绝。`gen_script/` 保存实际程序与生成依据，`events.jsonl` 记录实际执行，成对回顾性摘要说明结果。输入明确为合成。固定模型列表和小搜索范围用于验证软件，真实研究另需审核计划。程序汇报所有预先声明模型的测试指标，不用这些分数选择模型家族。

复算检查不重新生成输入：先核对文件、技能哈希和版本，从保存的网格节点重建日特征，重新检查小时完整性和既定分组/折分，重新拟合并比较参数、测试和网格预测，再独立计算 RMSE、MAE、R²。单元检查另行覆盖非法坐标系、外推、缺失支撑、重复小时和折分泄露；一次小模型成功不能替代这些检查。

## 扩展研究时保留小示例

保留逐小时小案例用于准备环节复核。经审核的逐日研究可在固定的逐小时对照通过后，采用 [ERA5 当地日交付](../../skills/data_acquisition/01_socioeconomic_natural_change/era5/references/daily-statistics_ZH.md)，同时保留 EAC4 三小时样本的当地日聚合。各模型共享逐月缓存和同一张准备表，不将提供方日统计描述为已逐一检查的逐小时档案。

使用空间剔除折及真实数值表格神经网络时，[固定折接口](../../skills/model/shared/machine_learning_model/references/fixed-fold-tabular_ZH.md)将数值操作保留在技能中。具体站点角色、获取路线、候选参数、预算和结果由项目管理。保留共同测试键与各随机种子的预测，使用冻结的最终模型重载完成零拟合评估复核。这不扩大或替换原有合成示例。

## 转入真实研究

生成真实实验代码前，让代理提出目标、来源版本、历史站点/坐标系依据、时间语义、变量及其来源、预处理、空间验证、参数范围、预算和保存位置。默认人工审核；用户明确委托后才由代理审定。产品同化或融合的依赖风险需要科学判断，不能由样本划分检查替代。

预测未布站位置，需要与推断范围相适应的空间隔离。邻近站点共用粗网格或空间结构时，只留出站号并不充分；应依据审核后的地理信息设置空间块或缓冲，并报告有效独立组数。小示例检验操作流程，不能证明全国预测精度。未核实坐标和时间映射不能改标为已核实；采用暂定解释的工程试验须明确审核并保留来源状态，不能作为严格科学验收。

项目结果保留在所属项目。人类科学审核后再决定是否将选定产品纳入 `assets/`；本组合不规定其内部结构，也不自动入库。
