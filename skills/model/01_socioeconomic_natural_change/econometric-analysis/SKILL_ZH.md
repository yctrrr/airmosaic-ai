---
name: econometric-analysis
description: 为应用计量分析明确目标量和识别策略；适用时用输入 CSV 运行受限的横截面 OLS 演示。
compatibility: "Python 3.10+ with NumPy; direct OLS script, no registered AirMosaic tool"
metadata:
  version: "0.1.0"
---

# 设计计量分析

[English](SKILL.md) | **中文**

先阅读[计量方法](../../../../methods/01_socioeconomic_natural_change/economic_model/econometrics/README_ZH.md)，记录目标总体、观察单位、结果、暴露或处理、时间范围与目标估计量。区分描述、预测、因果推断与结构估计。对于因果问题，先说明混杂路径和识别变化来源，再选方法。此处 OLS 脚本给出条件相关；只有额外的研究设计才能支持更强解释。

## 选择操作路线

- **简单横截面相关分析：**在核对变量单位、样本构建和数据支持后，给 `scripts/run_ols.py` 明确指定结果变量及自变量。脚本含截距，输出经典与 HC1 标准误、拟合值和诊断。这两种标准误都假设观察独立；聚类、面板或时间序列数据需另选实现。
- **政策效应等因果目标：**先写出处理分配、比较组、时序、干扰和识别假设；研究设计成立后再选择经过审阅的 DiD、IV、RDD、面板等实现。本技能不包含这些估计器，也不自动给出因果结论。
- **预测：**明确留出验证设计和信息泄漏控制，转用预测工作流。**结构分析：**明确行为机制、校准或估计目标及反事实，使用适合的模型实现。

## 运行小型 OLS 演示

CSV 每行需有非空且唯一的 `unit_id`、数值型结果及数值型自变量；缺失和非有限数值会停止。表头重复、样本不足、设计矩阵缺秩或严重病态、结果无变化也会停止。清单中的 toy CSV 使用 `unit_id,y,x1,x2`。在仓库根目录运行，须已安装 NumPy，将 `AIRMOSAIC_ASSETS_DIR` 设为已有的仓库外资产根，并选择尚不存在的输出目录：

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/ols-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/econometric-analysis/scripts/run_ols.py --input assets/data/01_socioeconomic_natural_change/SyntheticEconometrics/v1/rows.csv --outcome y --predictors x1 x2 --out-dir $out
```

检查 `coefficients.csv`、`fitted.csv`、`summary.json` 中的输入 SHA256 和标准误适用范围，并与 [toy-manifest.json](../../../../assets/toy-manifest.json)核对。合成数据设计的截距约为 2，`x1` 斜率约为 3，`x2` 斜率约为 1；这些都不是科学参数。输出目录以排他方式创建，再运行需换新路径。研究数据须获当前任务授权，结果存于仓库外，并留下样本和变量来源；识别与推断还需依具体方法审查。脚本为直接辅助工具，没有 run-tool ID 或自动注册。

## 公开技能参照

本流程借鉴公开的 [EconAgentSkills](https://github.com/JonasWeinert/EconAgentSkills)中先识别再选估计器、分离数据规范与复现步骤的组织方式，以及 [econometrics-skill](https://github.com/xiaomihu1992/econometrics-skill/blob/main/SKILL.md)对结果、处理、混杂和识别变化的检查顺序；没有搬入它们的估计器库。将外部技能用于研究数据前应审查其实现和默认设置。[fixest](https://lrberge.github.io/fixest/reference/feols.html)是部分面板估计的官方实现选择。
