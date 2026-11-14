# 年度网格人均 GDP 工作流

[English](README.md) | **中文**

组合[公开数据获取技能](../../skills/data_acquisition/shared/public-data/SKILL_ZH.md)与[人均 GDP 技能](../../skills/model/01_socioeconomic_natural_change/gridded-gdp/SKILL_ZH.md)。科学定义集中在[方法说明](../../methods/01_socioeconomic_natural_change/gridded_gdp_ZH.md)。本目录的专用 PowerShell 控制器直接调用下列技能脚本，尚无 run-tool/MCP 适配器或通用工作流引擎。

## 运行合成案例

需要 PowerShell 7、curl、R，以及 `terra, sf, exactextractr, data.table, Matrix, xgboost, jsonlite, digest`。缺少 R 包时安装到自行选择的用户库并设置 `R_LIBS_USER`；控制器不自动安装依赖。

```powershell
$run = Join-Path $env:TEMP ("airmosaic-gdp-" + [guid]::NewGuid().ToString('N'))
& ./workflows/gridded_gdp/Invoke-GriddedGdp.ps1 -RunDirectory $run -Mode synthetic -Append
& ./workflows/gridded_gdp/Invoke-GriddedGdp.ps1 -RunDirectory $run -Mode synthetic -Append -Resume
```

案例构造两个省、八个县的虚拟边界、历史观测及三个年度的栅格。夜光 TIFF 打包为带虚拟 Dataverse 元数据的 ZIP，再经过同一套归档校验、解包和裁剪脚本。12 轮小模型测试预测和校准；第二个候选复用首个已验收模型追加 2023 年，不再拟合。合成验证记录比较指标，但关闭改善门槛。这些结果验证工程流程，不能代表全国预测精度。

合成流程完成后，可选一个 Git 外且独立于运行目录的新路径，直接用 R 阅读和复跑模型拟合。[示例脚本](../../skills/model/01_socioeconomic_natural_change/gridded-gdp/examples/fit_synthetic_panel.R)读取已生成的县—年面板，拟合并比较一个前推年份，再保存和重载全量模型，输出预测明细、指标和训练摘要。

```powershell
$modelExample = './skills/model/01_socioeconomic_natural_change/gridded-gdp/examples/fit_synthetic_panel.R'
$modelOutput = "$run-r-model"
Rscript --vanilla $modelExample (Join-Path $run 'resolved-initial.json') $modelOutput
```

## 准备真实项目

将 [workflow.json](examples/workflow.json) 复制到 Git 外的私有配置目录，替换根目录、路径和哈希。模板示范从 2000–2020 原模型更新到 2021 年；更新更多年份时同步扩展年度条目及年份列表。更新既有产品时保留原项目网格和县界。开始前审查示例验收容差，不能依据最终评估结果选择容差或参数。

| 输入 | 接入约定 |
|---|---|
| 县界 | 独立的 sf RDS 或单图层 GeoPackage。使用唯一六位字符串 `PAC, Province_code`、有效面、明确 CRS 和大陆 31 个省级地区，历史质心须匹配。 |
| 历史面板 | CSV 包含 `PAC, Province_code, observed_gdp` 及下列九个特征；只用正值观测目标，保留原 2000–2020 特征定义和县级键。 |
| 原模型 | 兼容的 XGBoost JSON，作为逐年前推的旧基线；只训练到历史截止年，特征顺序和对数目标相同。 |
| 县级 GDP | 合法获取的 CSMAR CRE_Cmect CSV：`Sgnyea, Prvcnm_id, Ctnm_id, Cmect07`。非正及缺失目标不参与训练，只在县级推理时补齐；重复主键停止接入。 |
| 省级 GDP | CRE_Gdp01 CSV：`Sgnyea, Prvcnm_id, Gdp0116`；同年省级正值基准完整。 |
| 夜光 | 同年 NPP-VIIRS-like Version 2。Dataverse 来源配置触发下载及原网格裁剪；已有 TIFF 需提供年份、产品、版本和 SHA-256。 |
| 人口 | 同年 LandScan Global 30 弧秒总人口，本地提供来源元数据和 SHA-256。工作流不自动操作 ORNL 门户，不替换为 Mosaic/WorldPop。 |
| 土地覆盖 | C3S v2.1.1；带内嵌年份的 NetCDF `lccs_class`，或经核验转换、带同年清单的文件。CDS 来源配置调用官方客户端及请求模板。 |

特征严格按 `Agriculture_grid, Forest_grid, Grassland_grid, NTL_Pop, Urban_grid, Wetland_grid, Year, cenlat, cenlon` 排列。五类比例的分母为全部有效分类像元。县级土地覆盖特征沿用名义 0.1° 网格，保留细网格范围并将行列数取整。县级坐标沿用历史质心，网格使用取整后的中心坐标。GDP 目标统一为当年价元/人。

[cds-request.json](../../skills/model/01_socioeconomic_natural_change/gridded-gdp/examples/cds-request.json) 是可编辑的官方请求示例。核对当前 CDS 表单、接受条款，并在 Git 外配置已有官方客户端。土地覆盖辅助脚本保存请求 ID，后续查询和下载复用原任务。普通排队结束本次尝试，之后续接同一运行；提交结果未知或部分下载需检查后恢复。TLS 证书校验保持开启。本路线已做合成任务复用测试，交付的合成验收不包含真实 CDS 下载。

CSMAR 沿用[授权获取技能](../../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL_ZH.md)取得并放置导出文件。控制器在模型计算前核对必需本地输入，不读取浏览器会话或凭据文件。

### 复用已有夜光裁剪

按[公开数据技能](../../skills/data_acquisition/shared/public-data/SKILL_ZH.md)查询 Dataverse、下载年度归档并用 R 裁剪，坐标取 `geo.extent`，顺序为西、东、南、北。已有裁剪时，将 `$cropDirectory` 设为同时包含 `crop.tif` 和 `source.json` 的目录。私有配置的 `annual` 中先建立该年度条目，`$localConfigFile` 指向已有外部目录下的新文件。

```powershell
$gdp = './skills/model/01_socioeconomic_natural_change/gridded-gdp/scripts'
$localConfig = & "$gdp/Set-GdpNightLight.ps1" -Config $privateConfig -Year 2025 -CropDirectory $cropDirectory -OutputConfig $localConfigFile
```

辅助脚本核对产品、年份和范围，写出只替换 `annual.2025.light` 的新配置。对应年度的人口、土地覆盖及县省目标仍需齐备。若由控制器获取夜光，在私有配置中将该条目填为 `{"provider":"dataverse","year":2025,"version":"10.1"}`，并设置 `$localConfig = $privateConfig`。输入齐备后，把选定的配置交给控制器。

```powershell
& ./workflows/gridded_gdp/Invoke-GriddedGdp.ps1 -RunDirectory $freshExternalRun -Mode authorized -Config $localConfig
```

## 阶段和保留的实现

| 阶段 | 实现 | 主要证据 |
|---|---|---|
| 查目录、下载、裁剪 | public-data 的 `Get-DataverseRaster.ps1, crop_annual_raster.R`；GDP 的 `Get-CdsLandCover.ps1` | 原归档、发布方校验值、TIFF SHA-256、原网格逐像元比较、年度来源清单 |
| 特征准备 | `run_gdp.R prepare` 调用 `gdp_spatial.R, grid_overlap_sum.R` | 县级特征、对齐网格、人口守恒回执 |
| 面板与配对验证 | `run_gdp.R panel/validate, gdp_common.R` | 县—年观测面板；同一批整县留出及逐年前推的校准前预测 |
| 拟合与重载 | `run_gdp.R fit, config/model.json` | 固定 4,403 轮配方、全量训练数、保存和重载预测一致性 |
| 预测与校准 | `run_gdp.R grid` | 省级系数、县级目标、县级系数和三波段 0.01° GeoTIFF |
| 独立读回 | `run_gdp.R accept` | 重开 GeoTIFF，核对网格、NoData、正值、对齐输入与输出的县级人口守恒、省级闭合及县级 GDP p95/最大误差 |
| 可选本地发布 | `publish_gdp.R` | 预览清单、核验备份、发布事务和回滚 |

在仓库根目录也可对已解析的私有配置逐阶段调用：

```powershell
$gdp = './skills/model/01_socioeconomic_natural_change/gridded-gdp/scripts'
Rscript --vanilla "$gdp/run_gdp.R" $resolvedConfig preflight
Rscript --vanilla "$gdp/run_gdp.R" $resolvedConfig validate
Rscript --vanilla "$gdp/run_gdp.R" $resolvedConfig accept
```

后续阶段先解析上游依赖。不可变中间结果以输入、配置、代码和相关运行库版本生成签名；复用时核全量文件清单及哈希。不要修改已完成中间结果。失败尝试保留供排查；代码或设计变化时另建运行。原代码和请求身份一致时才能 `-Resume`。控制器记录阶段边界事件和状态，不自动记录全部 R 内部操作或智能体的完整代码生成历史。

## 年度追加与本地发布

追加新年度时，配置 `accepted_model` 为既有候选 ID，`accepted_model_root` 为其 Git 外候选目录，`accepted_receipt_sha256` 为核实的回执哈希。保留其训练年、特征约定、县界及网格，`output_years` 只选更晚年度并提供完整年度输入及县省表。控制器核验并复用模型与配对指标，跳过面板构建、验证拟合和全量重训。更新模型时则不设 `accepted_model`，先通过配对门槛再重训。

候选保存在 `work/candidates/<id>/`，含 `receipt.json, grid_acceptance.csv, validation_metrics.csv` 及沿用原命名的目录：

- `Grid_interpolate_0.01g/Grid_XGBoost_GDP_pc_0.01g_<year>.tif`：`GDP_pc, Pop_all, factor2`。
- `Grid_interpolate_0.01g/Grid_to_county_XGBoost_GDP_pc_<year>.csv`。
- `County_interpolate/County_XGBoost_GDP_pc_<year>.csv` 与 `Province_GDP_pc_calibration_<year>.csv`。
- `County_interpolate/Xgboost_GDP_model_<first>-<last>.json`。

年度县表不会替换原项目的历史合并表。只有单独选择本地发布操作后才会修改已有年度成品：

```powershell
Rscript --vanilla "$gdp/publish_gdp.R" $resolvedConfig $candidate 'reviewed-release' plan
Rscript --vanilla "$gdp/publish_gdp.R" $resolvedConfig $candidate 'reviewed-release' publish
Rscript --vanilla "$gdp/publish_gdp.R" $resolvedConfig $candidate 'reviewed-release' rollback
```

选择独立的 Git 外 `release_root`。发布脚本备份变更文件，在替换前保存事务日志，替换后核验。事务的 `complete.json` 状态为 `published` 才算发布完成，回滚后改为 `rolled_back`。多文件发布中断后可能需要回滚，消费者应避开发布期间读取。这是本地文件交付，不是公开上传仓库。

## 解释与仍缺输入

`validation_metrics.csv` 报告逐年及汇总（`test_year=0`）的对数 RMSE、对数 R²、绝对百分比误差中位数、样本数和县数。误差中位数用**比例值**，乘 100 转成百分数。生产改善门槛要求两个验证域的汇总对数 RMSE 及误差中位数均下降，不借此调参。校准后闭合衡量数值一致性，不能证明像元精度。

交接时，2025 同产品年度人口及全国同口径县级 GDP 仍缺。真实更新前需复核可用性；本工作流尚未补齐这些缺口，也未重跑正式全国 GDP 结果。来源权利、县界来源及历史特征定义还需项目审查。授权表、校准系数、模型权重和网格在确认再分发权利前保留在受控空间。

原始方法论文与将来的数据集版本 DOI 分别引用。2021–2024 输入更新及 2000–2024 重训和配对验证属于后续增量，2000–2020 网格保留历史模型。拟议 Zenodo 方案用一个 `grids_2000-2024.zip`，逐年保留实际范围并注明模型代次。CSMAR 衍生产物再分发权限仍待核定。[Shao 等，Journal of Hazardous Materials 510（2026），142141](https://doi.org/10.1016/j.jhazmat.2026.142141)
