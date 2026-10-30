# 预测贡献

[English](contribution.md) | **中文**

先按[解释方法](../../../../../methods/shared/machine_learning_model/contribution_ZH.md)明确解释代表的人群、比较条件及不确定性。贡献描述已拟合预测模型，不能识别因果效应。

已实现的 R 模块 [`contribution/explain.R`](../scripts/r/contribution/explain.R)执行验证集置换重要性、训练背景 PDP/ICE 及可选经验背景 Shapley 估计。它共享拟合模型包与通用预处理，不是独立 CLI 或另一套拟合流水线。在既有 R 任务的 `explanation` 中配置。[R设置](operations_ZH.md#8-支持的设置)保留准确样本、特征、网格及计算预算范围。

按[R操作](operations_ZH.md)执行，通过 `artifacts.json` 检查请求的解释角色、背景/抽样、单位、类别水平、依赖关系及不确定性。可选文件的缺失应符合请求设置。Python 预测可用不意味着 Python 解释已实现，见[Python路径](python-path_ZH.md)。
