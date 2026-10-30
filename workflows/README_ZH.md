# 可复用的数据与技能组合

[English](README.md) | **中文**

工作流说明可复用的数据与技能组合，包括用途、输入契约、操作交接、可选分支、检查和复核。代码及具体软件操作归技能，科学依据归方法，具体科学问题和实验归项目。

参见含目标设定、变量角色和 DAG 设计的[回归组合](ml_regression/README_ZH.md)。其中引用的已注册能力可执行，组合 YAML 本身只作说明。当前没有通用 YAML 执行器、项目加载器、自动实验编排或科学审批服务。

[模型复现组合](model_reproduction/README_ZH.md)增加来源审计、冻结候选/参考快照、可比视图和项目新比较批次。`compare_existing` 使用默认预检的已审查直接脚本；`reproduce_and_compare` 由 Agent 引导，需明确选择技能。[提示词](model_reproduction/prompt_ZH.md)说明交接与复核分支。来源收集通过授权方式单独审查，不提供通用远程执行或已注册比较适配器。

通用演示使用适配器支持且被忽略的结果目录，科学实验产物归属对应项目。当前执行器保留已有外部兼容位置，尚未实现直接写入项目目录。是否纳入 `assets/` 须经人类审核，历史结果保留。见[项目说明](../projects/README_ZH.md)和[结果与审核约定](../harness/assets_ZH.md)。


## 工作流合成检查

已审查的回归适配器额外支持显式 `result_scope=workflow`（CLI 为 `--result-scope workflow`）。仅允许清单登记且哈希一致的仓库合成 CSV，输出固定在被 Git 忽略的 `workflows/ml_regression/results/<timestamp>_<task>/`，记录和临时文件位于该结果根的 `.airmosaic/<run_id>/`。拒绝项目编号、真实或外部数据、越界目录及嵌套仓库；不改变 `auto` 的默认行为。正式研究仍使用外部项目结果根。工作流中经审查的编排示例可供复用；本次生成代码与依据放对应结果的 `gen_script/`，具体过程记录见统一交接规范。该检查不提供科学批准，也不构成操作系统沙箱。
