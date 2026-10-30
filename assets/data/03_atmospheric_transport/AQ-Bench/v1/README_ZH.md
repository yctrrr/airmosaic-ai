# AQ-Bench v1：公开输入副本

[English](README.md) | **中文**

本目录保存公开 AQ-Bench 输入的字节一致副本，署名 **Betancourt 等（2020）**。数据 DOI：[10.23728/b2share.30d42b5a87344e82855a486bf2123e9f](https://doi.org/10.23728/b2share.30d42b5a87344e82855a486bf2123e9f)。[来源记录](https://b2share.eudat.eu/records/xp9ww-efm51)；[数据论文](https://doi.org/10.5194/essd-13-3013-2021)。

## 内容与许可

| 文件 | 内容 |
|---|---|
| `AQbench_dataset.csv` | 5,577 个站点、53 列；2010–2014 年臭氧汇总指标及站点元数据 |
| `AQbench_variables.csv` | 53 列的字典、单位、类型及缺失值说明 |
| `asset.json` | 公开来源、许可与原文件 SHA256 |

数据采用[知识共享署名 4.0](https://creativecommons.org/licenses/by/4.0/)许可。再分发时保留数据作者署名、来源 DOI 和许可，说明所做修改。此处两个 CSV 均未修改；数据许可与仓库软件许可分别适用。

样本键为 `id`；`dataset` 提供训练、验证和测试标签，分别有 3,348、1,114、1,115 行。示例目标 `o3_average_values` 的单位为 ppb。这是历史站点汇总数据，不能静默将其他臭氧目标列用作预测特征。保留源文件，在准备阶段处理声明的 `-999` 缺失标记；科学质量与适用范围以数据论文为依据。

## 两个保存位置

外部工作副本使用 `${AIRMOSAIC_ASSETS_DIR}/data/03_atmospheric_transport/AQ-Bench/v1/`；本仓库副本采用相同的相对数据集与版本布局。两处 CSV 的 SHA256 一致，项目可显式选用任一副本。后续变更采用新版本，不覆盖 v1。个人来源定位、凭据、旧代码及参考结果不放入本目录。

[public-data-manifest.json](../../../../public-data-manifest.json) 将指定 CSV 登记为只读公开数据，与合成示例分开。这是输入允许清单，不是获取工具或数据目录注册。

完成常规[环境配置](../../../../../config/examples/README_ZH.md)后，可预检仓库输入示例：

```powershell
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/aq-bench-repository.json --dry-run
```

执行器核对选定公开文件的哈希。实际计算需要另行授权调用，并满足[回归技能依赖](../../../../../skills/model/shared/machine_learning_model/SKILL_ZH.md)；新结果仍保存在公共资产目录之外。原有外部输入参数示例继续可用。
