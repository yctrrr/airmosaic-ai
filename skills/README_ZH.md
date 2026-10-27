# 技能：四步与共享能力

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->

技能说明具体电脑操作：软件准备、输入准备、调用和操作检查。科学解释放[方法库](../methods/README_ZH.md)，人类路径叙述放[完整路径说明](../methods/pathways/README_ZH.md)，公共运行代码放[核心程序](../harness/usage/runtime_ZH.md)。




数据获取和模型使用均采用 01 社会经济与自然变化、02 排放清单、03 大气输送与化学、04 综合影响评估四步。逐步流程和状态见[四步导航](../harness/four-step-workflow.md)。

- [数据获取](data_acquisition/README_ZH.md)：来源、输入与处理边界。
- [模型使用](model/README_ZH.md)：方法、模型配置与验收。
- [方法库](../methods/README_ZH.md)：逐项链接真实 SKILL.md；不替代技能或工具注册。
- [新增与维护技能](../harness/skill-authoring_ZH.md)：双语文件、最小内容、注册边界和交付检查。

跨阶段保留共享目录与已有 IAM、machine_learning 入口。新增 SKILL.md 只表示有指导文档；是否登记、是否可执行分别以 catalog/tools 和运行器允许清单为准。

英文入口保留默认文件名，中文使用 `_ZH.md`。本轮仅整理入口与分类导航，历史长篇参考资料保留当前语言。

## 数据与项目结果

数据和项目结果按[资产规范](../harness/assets_ZH.md)管理。Git 外共享 `assets/data/<stage>/<dataset-name>/<version>/`，数据目录使用实际名称；项目按配置引用固定版本，跨阶段不复制。新结果保存到 `assets/results/<project_id>/<run_id>/<stage>/<tool_id>/`，运行记录和临时文件留在该批次内。新调用同时提供项目和阶段。计算与检查 → 人工复核 → 将选定数据登记到新版本；不覆盖原始数据或既有版本。个人配置、认证及凭据继续独立管理。旧文件不迁移，自动审批和入库服务尚未实现。
