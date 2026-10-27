# 机器学习模型使用

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->


本目录保存机器学习框架的使用方法、模型训练与预测流程、验证要求和上游项目跟踪记录。机器学习可用于排放、浓度、暴露等任务的预测或代理模型；预测表现本身不证明因果关系，也不替代原模型的科学验收。

| 框架 | 使用入口 | 当前状态 | 参考项目 |
|---|---|---|---|
| mlr3 / mlr3verse（R） | [mlr3 使用方法](mlr3/SKILL_ZH.md) | 已有方法说明和合成代码示例；尚无 run-tool 训练/预测适配器 | [zhjx19/ml-mlr3](https://github.com/zhjx19/ml-mlr3)；[版本跟踪](mlr3/UPSTREAM.md) |
| TimeXer（Python/PyTorch） | [TimeXer 方法与使用](timexer/SKILL_ZH.md) | 已有方法、参数和推理适配说明；尚无 run-tool 执行适配器 | [thuml/TimeXer](https://github.com/thuml/TimeXer)；[版本跟踪](timexer/UPSTREAM.md) |

`machine_learning` 是模型层下的分类目录。每个框架单独维护 SKILL.md、参考资料与示例；不要把具体研究项目的训练数据、模型对象或个人环境复制到此目录。

通用步骤：明确预测任务及数据许可 → 选择与部署场景一致的划分 → 仅在开发数据上构建预处理和模型 → 在预算内比较/调参 → 固定方案后评估 → 保存经核对的模型与输入契约 → 对新数据预测并检查适用范围。

输入位于 `${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/` 或既有 `output/`；新模型、预测与本地记录放在新的 `output/<run_id>/<workflow_id>/`。个人路径映射和参数在 `${AIRMOSAIC_CONFIG_DIR}`，登录状态在 `${AIRMOSAIC_AUTH_DIR}`，密码/令牌 仍由凭据管理器保管。参考流程不会自动创建这些目录或提供运行时隔离。

分类查询与详细边界见[机器学习分类文档](../../../harness/usage/machine-learning.md)。新增框架时，先如实登记参考或模板状态；只有实现、测试并审查过的适配器才能启用 run-tool。
