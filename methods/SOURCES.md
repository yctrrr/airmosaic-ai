# 来源、证据与维护

2026-10-23 完成四步重排及 GEOS-Chem 资料核对；各次证据按下述范围分别记录，不能将接口审查当作数据验收。

2026-10-26 完善 ERA5/CAMS 获取参考：本次复核官方 API 指南和公开 catalogue/form，沿用此前旧本地脚本的请求字段及日期生成接口审查结论，不重新访问原始资料。来源链接集中在 [Copernicus 下载指南](../harness/usage/copernicus-downloads.md)。未保存旧脚本副本、私人路径、凭据或源码指纹，未登录、使用真实令牌或提交下载，也未验证账户权限、条款或下载结果；这两张方法卡不依赖个人来源映射，`source_projects` 与 `tool_ids` 均为空。与 PM2.5 站点的衔接仅规定元数据契约，没有执行时空匹配。

上述为初次文档核对范围。后续另获明确授权，于同日完成一个 ERA5 单层 API 小请求：16:17:09 被接受、16:18:32 下载、16:20:11 内容验收通过（北京时间）。官方客户端内部使用本人已准备的凭据，agent 未查看凭据内容；没有读取既有原始数据，也没有执行网页下载、CAMS 或模型计算。公开参数、版本、调用步骤和验收方法见[实测示例](../skills/data_acquisition/01_socioeconomic_natural_change/era5/references/api-download-example.md)。私有任务引用、原始文件和完整本地记录不随方法库发布。

2026-10-26 完成 EAC4 地表 PM2.5 API 验证：固定 ADS endpoint，由官方客户端内部使用本人授权的既有凭据文件，17:57:05 接受请求、17:57:58 下载、17:57:59 验收通过（北京时间）。参数、单位、网格及使用方法见 [EAC4 示例](../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/eac4-api-download-example.md)。

2026-10-26 完成 CAMS 全球 PM2.5 预报 API 验证：18:11:02 接受请求，18:12:23 下载并验收通过（北京时间）。检查同一次起报的 0/3/6 小时时效、有效时间、0.4° 网格和单位，使用步骤见[全球预报示例](../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/forecast-api-download-example.md)。

2026-10-26 增补 [PM2.5 站点方法](03_atmospheric_transport/pm25_stations.md)。其前期证据包含本地研究说明、有限文件清单及已授权远程计算端点上的 README/整理脚本接口审查；没有读取监测原始表。本次正式写入仅使用该草案和公开来源说明，没有重新登录服务器或执行数据任务。公开来源与限度见 [来源说明](03_atmospheric_transport/pm25_stations_sources.md)；不提交私人目录、连接映射、旧脚本副本或原始日志。该方法的 source_projects/tool_ids 为空。

2026-10-26 18:24:04–18:24:07（北京时间）完成 Quotsoft 2024-01-01 公开站点 CSV 的获取和小时 PM2.5 长表检查。仅使用本次新下载文件，未读取既有原始数据；历史站点表与时间语义仍待核实。[流程、来源和结果](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/single-day-example.md)保持 reference 状态，无注册执行器。公开逐小时采集参考另列 HeQinWill/CNEMC，仅审阅其说明。

阶段名称统一为 01 社会经济与自然变化、04 综合影响评估；ERA5、CAMS EAC4 与全球预报的技能和方法卡迁入 01，03/04 保留引用。既有工具和数据集 ID 不变。

2026-10-26 19:11:24–19:12:50（北京时间）完成 PANGAEA DOI 917557 均一化发布包的获取、ZIP CRC、表头/位置编号匹配和一个序列 7 天样例检查。仅使用本次新取得的发布包；产品说明与误差在 [均一化日值附页](03_atmospheric_transport/pm25_homogenized.md)，操作过程在 [获取示例](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/homogenized-download-example.md)。没有重跑均一化、全时段重算或原站号推断。

2026-10-26 19:30:16–19:31:15（北京时间）完成 WorldPop 当前 Hub 目录、Global2 `G2_CN_POP_R25A_1km` 的 LIE/2020 唯一元数据筛选及单个官方 GeoTIFF 获取与解码。产品说明见 [WorldPop](01_socioeconomic_natural_change/worldpop.md)，操作与结果见[小文件示例](../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/references/first-download-example.md)。仅访问官方公开来源和本次新文件；未做人口重采样、区域统计、独立人口总量复核或健康计算。run-tool 预检与本机实际状态单独记录，不将官方文件获取成功写成执行器验证通过。

## 证据范围

2026-10-27 按授权委派子 agent 完成空气质量可解释建模项目的服务器只读核对。先复核两份 SSH 技能与助手已同步并支持专用配置，再复用已有授权成功组合，于北京时间 15:42:06 验证到计算节点；不将其写成原默认别名已修复。只读取相关源码及说明，检查数据与产物目录元信息，没有读取原始数据正文、模型内容、凭据或真实 SSH 配置正文，没有修改远程文件或运行训练。

`script/AQ_Bench.r` 的相对入口、数据字段、训练调参与解释职责、输出和适配项见[臭氧参考案例](pathways/references/air_quality_o3_reference_ZH.md)，能力与任务设计见[需求驱动建模](pathways/requirements_driven_model_building_ZH.md)。未修改源码快照及与服务器一致的 SHA256 只留仓库外审计目录。原始代码是复现参考，不是已通过数值验证的标准答案；缺失过滤与索引、划分标签、解释模型来源及背景等需正式适配。

2026-10-26 核对 IHME GBD 官方页面、GBD 2023 原始方法论文及明确标注版本的 IHME 工具指南，补齐[来源与规范化](04_integrated_impacts/ihme_gbd.md)、[数据范围与下载计划](04_integrated_impacts/ihme_gbd_availability.md)和[首次获取向导](../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/references/first-download-guide.md)。本人完成页面前置操作后，通过 GBD 2023 / Global / All causes / All ages / Both / Deaths / Number / 2023 的单条网页查询及导出；北京时间 21:00 核对新结果，21:02 提交导出，21:05 确认取得 717 字节 ZIP，21:05:42 完成 1 条、18 列 CSV 内容检查。

旧版工具指南只用于产品范围说明，不用于确认当前 ID 或下载成功。核对现有 manifest 与脚本后，明确独立风险及其他专题参数仍需适配；网页获取不等于 run-tool 已验证。未修改执行代码、绕过访问验证或读取既有原始数据与认证内容。原导出和任务引用保留成员工作区。

2026-10-26 WorldPop 脚本按授权修复为严格匹配 popyear，并直接使用官方 Hub 目录地址；17 个合成回归及全套 144 项测试通过，受限网络/凭据环境策略未修改。20:13:18–20:13:20（北京时间）的 run-tool 元数据查询仍返回 failed、退出码 1；没有重复下载已取得的 Global2 样例。当前接口与运行状态见 [WorldPop 入口说明](../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/references/worldpop-api.md)。

2026-10-26 数据质量说明补充：公开核对 GB 3095—2012 表 4、2018 修改单、GB 3095—2026 表 4、HJ 663—2026、HJ 817—2018 及 Bai 等（2020）原文；区分 20 小时日均要求、特定文献样本门槛和浓度状态变化。ERA5/EAC4/预报按 ECMWF/Copernicus 原始产品与不确定度说明分别补齐。来源集中在对应阶段的方法主文、附页及[共同规范](shared/data_quality.md)。本次仅维护说明，不读取监测/气象原始数据、不新增下载或处理运行。

- 01：保留来源类别、去重/映射/换算方法及已有工具边界，不复制数据。
- 02：根据本次要求收敛为方法目录；删除初稿的具体项目脚本、实现字段、公式代码与源码指纹，不读取其原始数据或重新查看实现。
- 03：提炼 GEOS-Chem.docx、Interpretable_air_pollution.docx 中相关技术段落；版本和旧操作差异见 [GEOS-Chem 来源说明](../skills/model/03_atmospheric_transport/geos-chem/SOURCES.md)。不保留本机云配置、服务器、认证或私人路径。
- 04 与共享：区分已有工具、模板和外部方法。GCAM 编译参考仅核对本地使用指南的编译相关段落及官方构建资料；不等于已复现编译或运行。

[source-snapshots.yaml](source-snapshots.yaml)只保存允许公开的逻辑项目、项目内相对文件名、阅读范围与 SHA-256；不是数据快照或执行回执。排放层没有具体源码锚点。存在性核对不等于完整源码审查；历史记录不证明当前库存、登录或科学验收。

数据说明统一约定：领域来源、误差、规范化与质量规则由各阶段方法正文和附页维护；共同原则在 shared/data_quality.md，SKILL.md 与 harness 链接唯一正文。接口、API 调用及运行验证示例继续放在技能 references。

## 维护顺序

1. 选择研究阶段，核对方法与真实 SKILL.md，跨阶段内容仅维护共享入口。
2. 只查看本次授权说明或接口；不因定位项目而扫描原始数据或认证目录。
3. 按需用[空值映射示例](examples/local-sources.example.yaml)在个人 CONFIG_DIR 配置来源根；示例不自动加载，不含真实路径。
4. 更新 index.yaml 的阶段、skills 与现有 tool_ids；新增文档不会注册执行器。
5. 检查引用、状态与隐私，按任务授权提交。外部原件、个人配置、模型和原始日志保留本地。
