# 模型族与拟合

[English](models.md) | **中文**

进入[模型分类目录](../models/README_ZH.md)，选择线性模型、树模型或仅参考的序列模型。决策树与随机森林归同一模型族；[基线归公共评估](../evaluation/README_ZH.md)。已实现模型链接各语言完整任务与 runner 示例。本页保留共同拟合接口说明。

先按[模型比较方法](../../../../../methods/shared/machine_learning_model/models/README_ZH.md)选择科学模型族。R 路径目前支持均值基线及声明的 `regr.rpart`、`regr.ranger` 候选。学习器和有界参数写入既有任务 JSON，不为每个模型复制流水线。[R支持设置](operations_ZH.md#8-支持的设置)记载准确范围、默认值、验证集选型以及尚未提供的调参/交叉验证/重拟合。Python 模型族及依赖验证见独立[Python路径](python-path_ZH.md)。

通用准备位于 `scripts/r/common/`。R 拟合模块为 [`scripts/r/models/fit.R`](../scripts/r/models/fit.R)，随后调用留出评估 [`evaluate.R`](../scripts/r/common/evaluate.R)。[`reproduction.R`](../scripts/r/models/reproduction.R) 是独立的开发集固定折森林函数库，注册预测入口不调用它。使用 `reproduction_forest()` 或 `reproduction_search_forest()` 前加载 [`io.R`](../scripts/r/common/io.R)。保留外部固定折号，测试数据不得参与搜索。科学依据见独立[复现方法](../../../../../methods/shared/model_reproduction_ZH.md)。

按[完整R调用及结果检查](operations_ZH.md)核查候选指标、实际队列、预处理、冻结预测、独立重算指标及重载一致性。模型成功拟合不构成科学有效性证明。

仅在开发数据内由包自动搜索参数时，使用独立[自动调参助手](automatic-tuning_ZH.md)。它接收审核后的分组折与有界范围，上述注册拟合模块不会调用它或接收其设置。完整依赖环境中的执行另行记录。
