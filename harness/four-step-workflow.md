# 四步导航、使用流程与交接

研究流程：社会经济驱动 → 排放清单 → 大气输送与化学 → 社会经济影响。数据获取和模型使用在每一步各有入口；共享方法只维护一份。编号不表示已实现自动流水线。

## 入口与状态

| 步骤 | 数据获取 | 模型使用 | 当前可执行范围 |
|---|---|---|---|
| 01 社会经济驱动 | [01_socioeconomic](../skills/data_acquisition/01_socioeconomic/README.md) | [01_socioeconomic](../skills/model/01_socioeconomic/README.md) | WorldPop、企业基础 ZIP 处理支持 run-tool；年鉴为模板，其他方法需适配 |
| 02 排放清单 | [02_emission_inventory](../skills/data_acquisition/02_emission_inventory/README.md) | [02_emission_inventory](../skills/model/02_emission_inventory/README.md) | 只列方法，无具体数据、实现代码或执行适配器 |
| 03 大气输送与化学 | [03_atmospheric_transport](../skills/data_acquisition/03_atmospheric_transport/README.md) | [03_atmospheric_transport](../skills/model/03_atmospheric_transport/README.md) | ERA5/CAMS 人工下载及 GEOS-Chem 输入、编译、配置与排错参考；没有下载、编译、调度或模拟适配器 |
| 04 社会经济影响 | [04_impact](../skills/data_acquisition/04_impact/README.md) | [04_impact](../skills/model/04_impact/README.md) | GBD 获取支持 run-tool；健康模板和完整成本/分配方法需人工适配 |

03 还提供 [PM2.5 站点获取与整理参考](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md)，用于浓度比较与观测交接；04 引用同一方法。该能力没有下载/整理适配器，不改变本表的执行范围。

[methods 方法库](../methods/README.md)按相同四步维护方法；[index.yaml](../methods/index.yaml)逐项映射真实 SKILL.md、适用阶段及已有 tool_id。方法索引不是运行器注册表。

## 01 社会经济驱动

1. 明确实体、地区、时间、行业、单位和待解释变量，列出输入与缺口。
2. 选择企业、年鉴、能源或人口方法；先读获取 skill，再查询已有工具的 schema、依赖和认证边界。
3. 获取与处理分开设计，说明去重、行业映射、单位换算、缺失语义和来源版本。
4. 预测任务引用共享 mlr3/TimeXer，预先确定时间/实体划分和特征可用性；GCAM 用于已有情景输出分析。
5. 用合成输入验证接口，交接活动、能源、技术信息的字段说明、覆盖与来源清单。真实数据获取和建模须另有明确任务范围。

## 02 排放清单：仅方法

1. 确定核算边界、活动与技术类别、物种和单位。
2. 选择排放因子、技术份额、治理效率、过程排放和变化分解方法。
3. 设计缺失处理、避免重复计量、汇总守恒和空间分配检查。
4. 形成供下一步讨论的排放、时间分配和物种映射契约。

本步只列方法及选择顺序。不提供具体数据、参数值、实现代码、项目脚本名、源码指纹或执行命令；关联共享能力也不引入排放实现。

## 03 大气输送与化学

1. 确定 Classic 或 GCHP、固定版本、模拟类型及全局/嵌套网格，不混用运行目录与配置。
2. 按[输入准备 skill](../skills/data_acquisition/03_atmospheric_transport/atmospheric-inputs/SKILL.md)列出气象、排放、初始/边界条件和诊断的接口需求。
   如需气象协变量或大气成分资料，参考 [ERA5/CAMS 下载指南](usage/copernicus-downloads.md)；获取这些数据不等于完成 GEOS-Chem 驱动或边界条件转换。
3. 按 [GEOS-Chem skill](../skills/model/03_atmospheric_transport/geos-chem/SKILL.md)核对编译器、库、CMake、并行模式及独立运行目录，参考编译排错说明。
4. 模型自身 dry-run 会执行程序并可能写日志；后续下载又有网络和落盘副作用。它不同于 run-tool 的无执行预检。
5. 后续获授权运行时，先短时测试，再核对退出码、时间终点、诊断、restart、单位和边界。浓度校正消费已有浓度，不能替代模拟。
6. 交接浓度契约、覆盖与验证摘要。当前没有本阶段的 run-tool 模拟入口，不使用虚构工具 ID。

站点观测支线：明确网络与时间范围 → 核对来源和站点表 → 分开制定获取/整理计划 → 按授权读取与质控 → 交接浓度和元数据。具体步骤及人工适配见 [PM2.5 方法卡](../methods/03_atmospheric_transport/pm25_stations.md)；不必为站点资料任务启动 GEOS-Chem，也不把站点记录直接当作模型驱动。

## 04 社会经济影响

1. 接收浓度契约，明确基准/干预情景、共同人口范围与风险及经济口径。
2. 通过共享人口方法和 GBD skill 确认维度、单位及许可；获取不自动启动健康计算。
3. 阅读健康模板，适配年龄、病因、死亡率、风险函数、网格与时间，以合成输入核对接口。
4. 成本分析引用共享方法，区分资源成本、价格基准、转移支付、承担主体和物理约束。
5. 交付配对差值、有效范围、缺失及不确定性。成功退出或单个汇总闭合不代表全部科学验收。

## 共享目录与执行边界

文献在 [data_acquisition/shared](../skills/data_acquisition/shared/README.md)；成本在 [model/shared](../skills/model/shared/README.md)。GCAM 保留 [IAM/gcam](../skills/model/IAM/gcam/SKILL.md)，机器学习保留 [machine_learning](../skills/model/machine_learning/README.md)，以免改变现有入口。WorldPop/GBD 保留所属阶段，由共享人口方法卡关联。

调用顺序：阶段入口 → SKILL.md → describe-tool/check-tool → 非秘密参数 JSON → run-tool dry-run → 授权执行 → 验收交接。模板、参考和未登记说明不能执行；不因不可执行而绕过运行器。

本轮及常规方法维护只使用说明、接口定义和合成输入，不读取、复制或运行原始数据。真实数据任务须另有明确范围。数据、非秘密个人配置、认证分别位于 Git 外的 LOCAL_WORKSPACE、CONFIG_DIR、AUTH_DIR；模型源码/发行包也在 Git 外。详见[存储约定](storage-and-credentials.md)和 [agent 边界](agent-boundaries.md)。
