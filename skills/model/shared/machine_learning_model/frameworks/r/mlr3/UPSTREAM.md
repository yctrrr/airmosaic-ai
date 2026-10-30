# mlr3 参考项目跟踪

此文件用于跟踪 mlr3 对应项目的使用依据，帮助成员判断文档来自哪个版本、哪些规则已适配到 AirMosaic，以及哪些验证仍需在自己的环境完成。

| 项目 | 本次记录 |
|---|---|
| 参考仓库 | [zhjx19/ml-mlr3](https://github.com/zhjx19/ml-mlr3) |
| 参考分支 | main |
| 核对日期 | 2026-10-23 |
| 核对提交 | [1b6af27747b461bc706991521369f766d7a0a041](https://github.com/zhjx19/ml-mlr3/tree/1b6af27747b461bc706991521369f766d7a0a041) |
| 上游声明版本 | 2.5.0，见该提交的 [SKILL.md](https://github.com/zhjx19/ml-mlr3/blob/1b6af27747b461bc706991521369f766d7a0a041/SKILL.md) 和 [CHANGELOG.md](https://github.com/zhjx19/ml-mlr3/blob/1b6af27747b461bc706991521369f766d7a0a041/CHANGELOG.md) |
| 上游许可 | [Apache-2.0](https://github.com/zhjx19/ml-mlr3/blob/1b6af27747b461bc706991521369f766d7a0a041/LICENSE)；后续复制或修改其源码时须检查并保留适用声明 |
| 本地形态 | 使用指南、独立编写的合成示例、只读目录条目；没有复制上游可执行脚本或 vendoring 全仓库 |

## 参考内容与本地适配

上游强调开发/最终测试数据分离、重抽样内预处理、R6 对象修改隔离、API 核对与受限并行。本地指南将这些要求落实到数据分割、模型选择、预测契约和结果验收，并增加 AirMosaic 的数据/config/auth 分离及公开记录约束。

| 上游资料 | 本地使用方式 |
|---|---|
| SKILL.md | 参考建模阶段与错误预防；依赖当前安装的 API 和实际任务设计 |
| references/ | 按划分、特征处理、调参和评估问题定向查阅；不自动下载或执行 |
| scripts/verify_examples.R | 上游自己的示例验证入口；其历史通过记录不代表 AirMosaic 环境已通过 |
| CHANGELOG.md | 查找接口和依赖变化，再判断是否影响本地说明/示例 |

本地保留项目既有代码风格，不把上游的赋值符号、管道或随机种子偏好设为全项目规则。最终测试评估遵循已有用户授权和预定方案，不重复索取已经明确的许可。依赖安装、并行和网络操作按本次任务需要决定，不因上游提及而自动执行。

## 后续复核步骤

1. 手动查看 main 最新提交，与本文件记录的 SHA 比较；这是按需复核约定，没有创建定时监控。
2. 先阅读 README、CHANGELOG、SKILL.md 和本地引用到的 references 的差异，区分 API、方法、依赖和文字变化。
3. 在隔离任务环境检查相关字典键、函数参数和版本；仅使用合成/获授权数据验证，不运行未经审查的安装器或上游脚本。
4. 更新受影响的本地文档与示例；记录实际运行、仅解析、跳过和失败的区别。若需 run-tool 支持，另实现受控适配器及测试，再改变注册状态。
5. 隐私和链接检查后，更新核对日期、提交及本地验证范围；上游版本变化不自动改变任务模型或研究结论。

## 本地验证范围

2026-10-23：核对了上游提交和公开方法资料。当前检查环境可用 R/rpart，但未安装 mlr3、mlr3pipelines、mlr3tuning、mlr3learners、paradox；本轮不安装这些包、不训练真实模型。合成示例只进行 R 语法解析，运行与性能验证留待具备依赖的任务环境。查看整个仓库的验证记录时，应以本条范围为准，不沿用 GCAM 测试作为 mlr3 已运行的证据。

## 官方 API 依据

- [mlr3 TaskRegr](https://mlr3.mlr-org.com/reference/TaskRegr.html)：回归任务构造和目标类型。
- [mlr3 Learner](https://mlr3.mlr-org.com/reference/Learner.html)：训练、预测、字典与后端依赖。
- [resample](https://mlr3.mlr-org.com/reference/resample.html)：重抽样及模型/后端保存选项。
- [mlr3pipelines 字典](https://mlr3pipelines.mlr-org.com/reference/mlr_pipeops.html)：核对 PipeOp 及其依赖。
- [auto_tuner](https://mlr3tuning.mlr-org.com/reference/auto_tuner.html)：训练阶段的内部调参和最终拟合。
- [mlr3book：评估与比较](https://mlr3book.mlr-org.com/chapters/chapter3/evaluation_and_benchmarking.html)：划分、重抽样和比较的统计含义。

## 2026-10-27 本地实现更新

新增 `ml_regression_workflow`，详见[工作流指南](../../../../../../../workflows/ml_regression/README_ZH.md)。独立依赖库使用 R 4.5.3、mlr3 1.8.0、mlr3learners 0.16.0、ranger 0.18.0、jsonlite 2.0.0、rpart 4.1.24，完整加载版本见[环境参考](../../../../../../../workflows/ml_regression/environment.reference.json)。合成检查和 AQ-Bench 小样本覆盖了准备、建模、评估、解释及同配置复跑。该实现独立编写，没有复制上游执行脚本，不改变上述 2026-10-23 的上游核对范围。当前固定留出方案不依赖 mlr3pipelines；加入交叉验证仍需折内预处理适配。
