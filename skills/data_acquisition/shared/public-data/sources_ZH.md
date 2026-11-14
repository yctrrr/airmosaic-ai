# 常用科研数据入口

[English](sources.md) | **中文**

| 入口 | 获取方式 |
|---|---|
| [Zotero](https://www.zotero.org/support/adding_items_to_zotero) | 查已有论文条目和附件，通过数据可用性声明进入数据 DOI。 |
| [Harvard Dataverse 年度夜光](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YGIVCD) | 网页选择发布版本和年度 Version 2 ZIP，或用本技能调用[下载 API](https://guides.dataverse.org/en/latest/api/dataaccess.html)。 |
| [Zenodo](https://developers.zenodo.org/)、[Figshare](https://docs.figshare.com/) | 打开数据 DOI，选论文所引版本并按文件列表获取。仓储提供记录 API 时可按其文档查询。 |
| [ORNL LandScan](https://landscan.ornl.gov/) | 在下载门户选择 LandScan Global 及年度。GDP 使用 30 弧秒总人口栅格。生产者另提供 [2000–2022 年存档](https://doi.org/10.6084/m9.figshare.28439699)。 |
| [Copernicus C3S 土地覆盖](https://cds.climate.copernicus.eu/datasets/satellite-land-cover) | 在官方表单选择 v2.1.1 与年份，接受条款后使用[年度 CDS 辅助脚本](../../../model/01_socioeconomic_natural_change/gridded-gdp/scripts/Get-CdsLandCover.ps1)。核对 `lccs_class` 与内嵌年份。 |
| [WorldPop](../../01_socioeconomic_natural_change/worldpop/SKILL_ZH.md)、[ERA5](../../01_socioeconomic_natural_change/era5/SKILL_ZH.md) | 按产品技能查询目录和执行获取。 |

GDP 的 CSMAR 输入沿用[本地授权获取技能](../../01_socioeconomic_natural_change/csmar/SKILL_ZH.md)。

县省 CSV 的字段，以及 Dataverse 裁剪后的年度接入方式，见 [GDP 输入说明](../../../../workflows/gridded_gdp/README_ZH.md#准备真实项目)。
