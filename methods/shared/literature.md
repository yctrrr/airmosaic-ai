# 文献发现、下载与归档

**状态**：已阅读本地文献管理项目的公开源码；AirMosaic 尚无该流程的 tool_id 或执行适配器。它整理研究证据，不等同于获得论文中的完整数据和模型。

## 输入、依赖与产物

- 输入：研究问题、关键词/来源范围，或给定 DOI/论文链接；已有文献库目录只从非秘密个人配置定位。
- 依赖：外部 Python 项目、其 requirements、按需浏览器；AI 分类/总结另需已配置服务及相应授权。
- 产物：论文与补充材料、来源元数据、待审核队列、摘要索引、导入审核清单。原文可能受访问或再分发限制，保持本地。
- 登录：仅在来源需要且用户已有权限时使用本人会话；可选 LLM 凭据由本地进程读取，不写进共享配置。

## 操作步骤

1. 先按 DOI、标题和已有附件查重，确认本次主题、时间范围和数量上限。
2. 核对原始来源和可访问全文；将主文、补充材料、数据链接分别识别，不把同名文件视为同一版本。
3. 先预览候选，再按授权下载；验证文件实际格式和可读性，记录失败与缺附件。
4. 文件先进入待审核队列；分类与总结作为独立步骤，保留来源及未解决问题。
5. 生成 Zotero/EndNote 导入清单；修改文献库需当前任务已授权，不能把生成清单当作已完成导入。

## 源码行为与适配

本次核对的入口包括 `run_weekly.py`、`run_summary.py`（说明中的独立总结入口）和 `prepare_zotero_import.py`。`run_weekly.py --dry-run` 仍会发现来源、使用浏览器并创建归档布局/运行日志；它不是 AirMosaic run-tool 的“无执行、无落盘”预检。不能因参数名称相同而继承另一套边界。

本次阅读的 `prepare_zotero_import.py` 生成 JSON/CSV 审核计划，并明确标记 Zotero 访问未运行。不要复制私人版本配置、浏览器 profile 或完整检索日志；先将外部项目的 archive/config/auth 路径映射到[方法库存储约定](../README.md)。

## 验收

检查 DOI/标题、附件配对、文件校验、重复项、下载失败与摘要来源。只报告本次实际归档/导入的范围。本次未启动收集器、LLM 或 Zotero 操作；代码存在不证明当前网络来源可用。

## 阶段与 Skill 映射

主目录：shared；适用阶段：01_socioeconomic_natural_change, 02_emission_inventory, 03_atmospheric_transport, 04_integrated_impacts。对应 [literature-workflow](../../skills/data_acquisition/shared/literature-workflow/SKILL.md)。执行状态以本文及真实工具 manifest 为准；没有 tool_id 的方法只供指导。
