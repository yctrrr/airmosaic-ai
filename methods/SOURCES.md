# 来源、证据与维护

2026-10-23 完成四步重排及 GEOS-Chem 资料核对；各次证据按下述范围分别记录，不能将接口审查当作数据验收。

2026-10-26 完善 ERA5/CAMS 获取参考：本次复核官方 API 指南和公开 catalogue/form，沿用此前旧本地脚本的请求字段及日期生成接口审查结论，不重新访问原始资料。来源链接集中在 [Copernicus 下载指南](../harness/usage/copernicus-downloads.md)。未保存旧脚本副本、私人路径、凭据或源码指纹，未登录、使用真实令牌或提交下载，也未验证账户权限、条款或下载结果；这两张方法卡不依赖个人来源映射，`source_projects` 与 `tool_ids` 均为空。与 PM2.5 站点的衔接仅规定元数据契约，没有执行时空匹配。

2026-10-26 增补 [PM2.5 站点方法](03_atmospheric_transport/pm25_stations.md)。其前期证据包含本地研究说明、有限文件清单及已授权远程计算端点上的 README/整理脚本接口审查；没有读取监测原始表。本次正式写入仅使用该草案和公开来源说明，没有重新登录服务器或执行数据任务。公开来源与限度见 [来源说明](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/sources-and-formats.md)；不提交私人目录、连接映射、旧脚本副本或原始日志。该方法的 source_projects/tool_ids 为空。

## 证据范围

- 01：保留来源类别、去重/映射/换算方法及已有工具边界，不复制数据。
- 02：根据本次要求收敛为方法目录；删除初稿的具体项目脚本、实现字段、公式代码与源码指纹，不读取其原始数据或重新查看实现。
- 03：提炼 GEOS-Chem.docx、Interpretable_air_pollution.docx 中相关技术段落；版本和旧操作差异见 [GEOS-Chem 来源说明](../skills/model/03_atmospheric_transport/geos-chem/SOURCES.md)。不保留本机云配置、服务器、认证或私人路径。
- 04 与共享：区分已有工具、模板和外部方法。GCAM 编译参考仅核对本地使用指南的编译相关段落及官方构建资料；不等于已复现编译或运行。

[source-snapshots.yaml](source-snapshots.yaml)只保存允许公开的逻辑项目、项目内相对文件名、阅读范围与 SHA-256；不是数据快照或执行回执。排放层没有具体源码锚点。存在性核对不等于完整源码审查；历史记录不证明当前库存、登录或科学验收。

## 维护顺序

1. 选择研究阶段，核对方法与真实 SKILL.md，跨阶段内容仅维护共享入口。
2. 只查看本次授权说明或接口；不因定位项目而扫描原始数据或认证目录。
3. 按需用[空值映射示例](examples/local-sources.example.yaml)在个人 CONFIG_DIR 配置来源根；示例不自动加载，不含真实路径。
4. 更新 index.yaml 的阶段、skills 与现有 tool_ids；新增文档不会注册执行器。
5. 检查引用、状态与隐私，按任务授权提交。外部原件、个人配置、模型和原始日志保留本地。
