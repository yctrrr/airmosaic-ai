---
name: gridded-gdp
description: Prepare annual predictors, pair-validate, train, predict and calibrate China's gridded GDP per capita.
compatibility: "R with terra, sf, exactextractr, data.table, Matrix, xgboost, jsonlite and digest; PowerShell 7 controller."
metadata:
  version: "0.1.0"
---

# 年度网格人均 GDP 建模

[English](SKILL.md) | **中文**

按[估算方法](../../../../methods/01_socioeconomic_natural_change/gridded_gdp_ZH.md)和[工作流](../../../../workflows/gridded_gdp/README_ZH.md)运行。[R 入口](scripts/run_gdp.R)支持 `preflight`、`prepare`、`panel`、`validate`、`fit`、`grid` 和 `accept`。[PowerShell 包装脚本](scripts/Invoke-GdpWorkflow.ps1)另提供本地发布操作。需要获取和接入年度输入时，先走工作流入口。

输入包括同年夜光、总人口、LCCS 栅格、固定县界和授权县省统计表。更新模型还读历史面板与原始模型。按年追加核验并加载已验收模型及其验证证据。交接前检查候选回执、配对指标和两级闭合。直接脚本写入 Git 外部目录，授权产物留在对应受控空间。

接入已有年度夜光裁剪时，将裁剪目录和含该年度条目的配置交给 [Set-GdpNightLight.ps1](scripts/Set-GdpNightLight.ps1)。[合成 R 拟合示例](examples/fit_synthetic_panel.R)展示特征矩阵、对数 GDP 目标、一年前推比较、全量拟合及模型重载。具体命令及完整验证见工作流。

原始研究及方法引用为 [Shao 等，JHM 2026](https://doi.org/10.1016/j.jhazmat.2026.142141)，附 [BibTeX](references/method_citation.bib)。方法主文区分了后续 2021–2024 输入更新及 2000–2024 重训/配对验证。描述 Zenodo 数据包时保留历史模型代次，再分发仍需相应授权。
