# 四步导航、使用流程与交接

研究流程：社会经济与自然变化 → 排放清单 → 大气输送与化学 → 综合影响评估。数据获取和模型使用在每一步各有入口；共享方法只维护一份。编号不表示已实现自动流水线。

01 描述上游条件与驱动，包括经济、人口、能源、技术、土地利用、气象和自然过程；04 评估变化对人类社会、健康、生态、农业和气候等受体的影响。同一变量按研究角色区分驱动与响应。ERA5、CAMS EAC4 和 CAMS 全球预报统一在 01 获取，03/04 引用，不复制技能。生态、农业与气候影响目前仅界定范围，没有新增计算工具。

## 入口与状态

| 步骤 | 数据获取 | 模型使用 | 当前可执行范围 |
|---|---|---|---|
| 01 社会经济与自然变化 | [01_socioeconomic_natural_change](../skills/data_acquisition/01_socioeconomic_natural_change/README.md) | [01_socioeconomic_natural_change](../skills/model/01_socioeconomic_natural_change/README.md) | WorldPop、企业基础 ZIP 处理支持 run-tool；ERA5、EAC4、CAMS 预报有已验证 API 示例，未接入 run-tool；其他方法需适配 |
| 02 排放清单 | [02_emission_inventory](../skills/data_acquisition/02_emission_inventory/README.md) | [02_emission_inventory](../skills/model/02_emission_inventory/README.md) | 方法及已声明的有界合成清单计算；无该阶段的 run-tool 适配器 |
| 03 大气输送与化学 | [03_atmospheric_transport](../skills/data_acquisition/03_atmospheric_transport/README.md) | [03_atmospheric_transport](../skills/model/03_atmospheric_transport/README.md) | PM2.5 站点获取/整理及 GEOS-Chem 输入、编译、配置与排错参考；引用 01 气象和成分资料；没有下载、编译、调度或模拟适配器 |
| 04 综合影响评估 | [04_integrated_impacts](../skills/data_acquisition/04_integrated_impacts/README.md) | [04_integrated_impacts](../skills/model/04_integrated_impacts/README.md) | GBD 获取支持 run-tool；健康模板和完整成本/分配方法需人工适配 |

03 还提供 [PM2.5 站点获取与整理参考](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md)，用于浓度比较与观测交接；04 引用同一方法。该能力没有下载/整理适配器，不改变本表的执行范围。

[methods 方法库](../methods/README.md)按相同四步维护方法；[index.yaml](../methods/index.yaml)逐项映射真实 SKILL.md、适用阶段及已有 tool_id。方法索引不是运行器注册表。

## 01 社会经济与自然变化

1. 明确实体或自然系统、地区、时间、行业/变量、单位和驱动条件，列出输入与缺口。
2. 选择企业、年鉴、能源、人口、ERA5 或 CAMS 方法；先读获取 skill，再查询已有工具的 schema、依赖和认证边界。EAC4 是历史再分析，CAMS 全球预报保留起报和时效。
3. 获取与处理分开设计，说明去重、行业映射、单位换算、缺失语义和来源版本。
4. 预测任务引用共享 mlr3/TimeXer，预先确定时间/实体划分和特征可用性；GCAM 用于已有情景输出分析。
5. 用合成输入验证接口，交接活动、能源、技术及自然条件的字段说明、覆盖与来源清单。自然资料可直接交接 03/04，不必经过排放核算；真实获取和建模须限定任务范围。

## 02 排放清单：方法与已声明的合成计算

1. 确定核算边界、活动与技术类别、物种和单位。
2. 选择排放因子、技术份额、治理效率、过程排放和变化分解方法。
3. 设计缺失处理、避免重复计量、汇总守恒和空间分配检查。
4. 形成供下一步讨论的排放、时间分配和物种映射契约。

本步提供方法选择顺序，并仅在已明确声明且经审查的清单技能内提供有界合成计算。其他概念条目不代表已有实现；真实数据处理需要限定任务。直接脚本示例不启用第二步的 run-tool 适配器，执行器仍拒绝该阶段。

## 03 大气输送与化学

1. 确定 Classic 或 GCHP、固定版本、模拟类型及全局/嵌套网格，不混用运行目录与配置。
2. 按[输入准备 skill](../skills/data_acquisition/03_atmospheric_transport/atmospheric-inputs/SKILL.md)列出气象、排放、初始/边界条件和诊断的接口需求。
   如需气象协变量或大气成分资料，参考 [ERA5/CAMS 下载指南](usage/copernicus-downloads.md)；获取这些数据不等于完成 GEOS-Chem 驱动或边界条件转换。
3. 按 [GEOS-Chem skill](../skills/model/03_atmospheric_transport/geos-chem/SKILL.md)核对编译器、库、CMake、并行模式及独立运行目录，参考编译排错说明。
4. 模型自身 dry-run 会执行程序并可能写日志；后续下载又有网络和落盘副作用。它不同于 run-tool 的无执行预检。
5. 后续获授权运行时，先短时测试，再核对退出码、时间终点、诊断、restart、单位和边界。浓度校正消费已有浓度，不能替代模拟。
6. 交接浓度契约、覆盖与验证摘要。当前没有本阶段的 run-tool 模拟入口，不使用虚构工具 ID。

站点观测支线：明确网络与时间范围 → 核对来源和站点表 → 分开制定获取/整理计划 → 按授权读取与质控 → 交接浓度和元数据。具体步骤及人工适配见 [PM2.5 方法卡](../methods/03_atmospheric_transport/pm25_stations.md)；不必为站点资料任务启动 GEOS-Chem，也不把站点记录直接当作模型驱动。

## 04 综合影响评估

1. 接收浓度及相关环境条件，明确基准/干预情景、受体、评价指标、共同空间/时间范围和归因口径。健康、经济、生态、农业及气候分别选择方法。
2. 通过共享人口方法和 GBD skill 确认维度、单位及许可；获取不自动启动健康计算。
3. 阅读健康模板，适配年龄、病因、死亡率、风险函数、网格与时间，以合成输入核对接口。
4. 成本分析引用共享方法，区分资源成本、价格基准、转移支付、承担主体和物理约束。
5. 自然系统评估先定义生态/作物响应、沉降/暴露或辐射相关指标及所需输入；当前没有这些分支的执行适配器，需人工补齐方法和验证。
6. 交付配对差值、有效范围、缺失及不确定性。成功退出或单个汇总闭合不代表全部科学验收。

## 阶段命名与迁移

01 目录和阶段筛选值统一为 `01_socioeconomic_natural_change`，04 为 `04_integrated_impacts`。skills、methods、阶段参考、数据声明与工具入口路径同步更新；已有 tool_id、dataset_id、skill frontmatter 名称和缓存目录保持稳定。个人脚本若保存过旧目录或 `list-datasets --layer` 值，需改用当前值。

## 共享目录与执行边界

文献在 [data_acquisition/shared](../skills/data_acquisition/shared/README.md)；通用模型任务与框架说明在 [model/shared](../skills/model/shared/README_ZH.md)，GCAM 与治理成本、分配情景归[第四步](../skills/model/04_integrated_impacts/README_ZH.md)。各技能保持唯一位置，由相应方法卡和阶段入口引用。WorldPop/GBD 保留所属阶段，由共享人口方法卡关联。

调用顺序：阶段入口 → SKILL.md → describe-tool/check-tool → 非秘密参数 JSON → run-tool dry-run → 授权执行 → 验收交接。模板、参考和未登记说明不能执行；不因不可执行而绕过运行器。

本轮及常规方法维护只使用说明、接口定义和合成输入，不读取、复制或运行原始数据。真实数据任务须另有明确范围。数据、非秘密个人配置、认证分别位于 Git 外的 AIRMOSAIC_ASSETS_DIR、CONFIG_DIR、AUTH_DIR；模型源码/发行包也在 Git 外。详见[存储约定](storage-and-credentials.md)和 [agent 边界](agent-boundaries.md)。

通用研究设计见[共享方法](../methods/shared/requirements_driven_model_building_ZH.md)，人工交接见[交接指南](usage/workflow-handoff_ZH.md)。`workflows/` 提供数据与技能组合说明，可执行操作由已登记技能承担，尚无通用工作流执行引擎；早期阶段 YAML 不再作为现行说明或执行配置。

## 数据与结果位置

各研究环节引用经核对的输入，项目保存实验结果、实际代码、配置与评价。人类科学审核后决定是否将选定成果纳入 `assets/`，本轮不规定其内部组织。项目目录约定与现有执行器兼容位置的区别见[项目说明](../projects/README_ZH.md)和[结果与审核约定](assets_ZH.md)。不迁移历史结果。排放清单仅在已明确声明的能力内提供有界合成示例，其他条目及空目录不代表已有数据或计算能力。