# 论文预测与评估实验

[English](prediction.md) | **中文**

本实验根据 [最终发表文章](https://doi.org/10.1016/j.atmosres.2026.108869) 第 2 节、表 1 和图 3，组合外部 AQ-Bench 数据、[回归技能](../../skills/model/shared/machine_learning_model/SKILL_ZH.md)与 [mlr3 技能](../../skills/model/shared/machine_learning_model/frameworks/r/mlr3/SKILL_ZH.md)开展独立实现。研究问题属于本项目；通用的数据与技能组合仍由 [workflow](../../workflows/ml_regression/README_ZH.md)说明。

先阅读并固定 [agent 指令](prediction_prompt_ZH.md)与 [实验协议](prediction.json)。国家/地区观测数严格大于 50，气候区归并为 dry、moist、wet；未知或不能归并的标签排除。原始 train 与 val 合并为 4077 条开发样本，test 保留 1009 条。两个特征组使用相同站点、十折划分和完整样本条件。

文章明确指定随机森林、两组变量和十折 RMSE 调参；没有给出完整搜索空间、原始种子及全部实现细节。本轮预先固定每组 20 个不重复候选、500 棵树、单线程及协议中的参数范围。获选参数在最终测试前保存，随后用全部开发样本重拟合。不能仅凭样本数或趋势一致宣称原论文数值复现成功。

## 执行步骤

从仓库根运行。先按项目存储规范显式设置 `AIRMOSAIC_ASSETS_DIR`、`AIRMOSAIC_CONFIG_DIR`、`AIRMOSAIC_AUTH_DIR` 与 `AIRMOSAIC_R_LIBRARY`；不读取配置或认证根中的文件，不安装软件或联网。依赖为 R、jsonlite、mlr3、mlr3learners 和 ranger。配置中只使用通用相对路径。

```powershell
# 预检：核对路径、哈希与字典，不读取数据行或拟合模型。
python projects/0001_ozone_environmental_drivers/run_prediction.py --batch-id paper_prediction_attempt01

# 合成检查：验证筛选、异常输入、指标、折外预测和测试目标隔离。
python projects/0001_ozone_environmental_drivers/run_prediction.py --batch-id paper_prediction_checks01 --self-test --timeout 180

# 经授权的真实计算：每次选择尚不存在的批次名。
python projects/0001_ozone_environmental_drivers/run_prediction.py --batch-id paper_prediction_attempt01 --execute --timeout 1800
```

这是项目专用启动器，不是新的工具编号，也不是通用 `run-tool` 的十折调参选项。它复用核心的路径检查、分离根检查、最小进程环境、进程树时限及固定 R 启动机制；R 复用回归技能的指标函数，用 mlr3 组织论文特有的重抽样与拟合。这些约束不构成操作系统沙箱。

## 保存与复核

当前实验自选外部 `assets/results/ozone_environmental_drivers/<batch_id>/`，其中保存：

- prompt、协议、实际执行源代码和所用技能的快照与哈希；
- 样本排除汇总、共同队列、站点折分、全部候选与每折评分、选定参数；
- 开发期折外预测、最终测试预测、均值基线、RMSE、MAE 与明确定义的样本外 R²；
- 两组模型、重载核对、预测图和杂质重要性；杂质重要性是有偏的预测诊断，不是因果效应；
- 软件版本、起止时间、脱敏进度、独立 Python 核验与产物哈希。

开发期折外成绩已经参与选参，不能作无偏最终性能。测试集用于冻结后的预测评价；站点随机划分不能替代空间外推验证。结果不提交、不自动入库。首轮结果已按[模型复现工作流](experiments/reference_comparison/README_ZH.md)完成原代码、保存模型与最终结果对照；保留历史训练来源缺口，科学结论由人类复核。新增运行需要独立比较批次。
