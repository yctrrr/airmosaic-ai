---
name: spatial-analysis
description: Match spatial points and polygons, transform verified coordinates and build maps through separate R or Python paths; guide raster and provider-specific geocoding tasks with explicit accuracy and privacy requirements.
---

# 空间分析与制图

[English](SKILL.md) | **中文**

按[方法说明](../../../../methods/shared/spatial_analysis_ZH.md)选择关系、坐标系、支撑与精度。[操作说明](references/operations_ZH.md)提供共用配置与结果检查，再选择 [R 路径](references/r-path_ZH.md)或 [Python 路径](references/python-path_ZH.md)；[地理编码](references/geocoding_ZH.md)另按来源或服务商处理。

## 当前能力

| 能力 | 状态 |
|---|---|
| 投影坐标下点与面的匹配 | R 与 Python 函数，保留唯一、缺失与歧义匹配 |
| 已知来源的坐标转换 | R 与 Python 函数，要求明确来源坐标系并关闭 PROJ 联网 |
| 点/面与矩形网格/分面图 | R 复用成员函数模式，Python 提供对应函数；两条路径均完成合成检查 |
| 最近邻/距离与栅格变换 | 库调用指导，需要按任务适配和验证 |
| 地理编码 | 本地地名表与服务选择指导，未默认接入在线客户端或实测服务 |

未注册新工具 ID、run-tool/MCP 适配器、自动配置加载器或地理编码服务。直接函数不继承 runner 的路径/凭据保护，加载时不读取数据或导出文件。

## 使用步骤

1. 声明获授权输入版本、几何/坐标系、标识、数值单位、边界日期、操作及新的外部项目输出。计算前解释关系或距离、坐标精度与权重选择。
2. 检查几何有效性、坐标约定、样本键及匹配基数。坐标系未知或服务坐标未核实，应先复核来源。
3. 按现有环境选择 R 或 Python，不隐式安装或下载。核对引擎与库版本，私人来源路径和凭据保留在个人机制中。
4. 仅加载所选经审查模块，显式传入数据、列名与坐标系，再检查匹配表或图对象。两条路径保留一致的匹配字段。歧义与未匹配需要明确处置，不自动回退到最近邻。
5. 检查实际输入/结果身份、样本键、距离/单位、覆盖、色标及适用总量。质量记录随结果保存，保留来源，派生数据入库前进行科学复核。

在仓库根运行合成检查，不读业务数据、不写输出：

```sh
Rscript --vanilla skills/model/shared/spatial_analysis/examples/r/synthetic_spatial.R
python skills/model/shared/spatial_analysis/examples/python/synthetic_spatial.py
```

每条语言路径检查唯一匹配、边界歧义和未匹配各一个，以及坐标往返、四种图构建和拒绝案例。Python 在独立依赖环境中完成检查，未修改项目主环境；未提交真实地理编码请求，也未验证栅格计算。

共享数据归外部 `AIRMOSAIC_ASSETS_DIR/data/<stage>/<dataset>/<version>/`，非秘密设置归 `AIRMOSAIC_CONFIG_DIR`，项目结果归外部 `assets/results/<project_id>/`。住宅/私人地址、敏感精确位置、令牌、含凭据的服务 URL 和个人文件路径不得进入共享材料。在线调用需按所选服务与授权范围执行；客户端库不代表服务访问授权。
