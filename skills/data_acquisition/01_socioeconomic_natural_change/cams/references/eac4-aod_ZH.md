# EAC4 的 550 nm 总 AOD

[English](eac4-aod.md) | **中文**

来源身份和不确定性见[CAMS 方法](../../../../../methods/01_socioeconomic_natural_change/cams_ZH.md)。2026-10-30 核对 ADS 公开目录/表单，`cams-global-reanalysis-eac4` 的准确请求值为 `total_aerosol_optical_depth_550nm`。这是柱积分、无量纲的 AOD，不是地面 PM2.5、ERA5 变量或未经加工的卫星反演。同日核对的 ERA5 单层表单共有 262 个可选变量，没有 AOD 选项。本检查没有认证请求或下载 AOD。

## 请求与检查

1. 明确日期、UTC 采样、边界及新的项目输出。[请求示例](../../../../../config/examples/copernicus/cams-eac4-aod.request.json)只含小区域单个 UTC 场，不是中国全年或日产品。本变量为柱量，不选择模式层 60。
2. 使用[官方客户端操作](../../era5/references/operations_ZH.md)中的 `cams-eac4-aod`，或在[ADS 表单](https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4?tab=download)选择该变量。请求保存在新的个人配置文件中，保留其他 ERA5/ADS 设置。官方客户端可内部使用本人授权凭据，不检查或记录内容。
3. 下载后解码 GRIB，核对 AOD 参数身份、波长、无量纲单位、实际网格、UTC 有效时间、有限值和缺失。不套用 PM2.5 的 kg/m³ 转换，不统一以 1 为上限剔除，不用文件非空代替内容验收，也不把早先 PM2.5 示例的参数编号核对套给 AOD。
4. 逐日研究按已核实的当地日窗口选择原生三小时采样，明确将预期八个采样的均值作为日尺度协变量，缺采样保留缺口。PM2.5 的 20 小时门槛不适用。单场请求不验证日聚合。
5. 通过经审查的空间实现匹配坐标/时间，保存双线性权重、掩膜和输入网格身份。原生输出为 0.75°，插值到更细网格不会增加独立信息。共同预测网格与来源网格分别声明。

认证、路径及中断/重试沿用父技能。本路径没有 AOD 执行器适配器、自动聚合或已验证的站点/网格推理流水线，真实解码与空间验证仍待完成。

一手元数据：[EAC4 目录](https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4?tab=overview)、[ERA5 单层目录](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview)。
