---
name: public-data-acquisition
description: Trace public research datasets from articles and Zotero records and download and crop annual Dataverse raster archives with provider checksums.
compatibility: "PowerShell 7, curl, R with terra, jsonlite and digest. Direct scripts."
metadata:
  version: "0.1.0"
---

# 公开科研数据获取

[English](SKILL.md) | **中文**

先读[公开数据方法](../../../../methods/shared/public_data_acquisition_ZH.md)和[常用数据目录](sources_ZH.md)。从 DOI、已授权的 Zotero 元数据或附件出发，查看论文数据可用性声明并进入数据发布页。需要导入引文或建立附件链接时，沿用[文献流程](../literature-workflow/SKILL_ZH.md)。

从仓库根目录执行。先查可用年份和文件，再固定版本下载。下例选择协调后的 NPP-VIIRS 类夜光年度序列中的 2025 年。

```powershell
$script = './skills/data_acquisition/shared/public-data/scripts'
& "$script/Get-DataverseRaster.ps1" -Years 2025
$raw = & "$script/Get-DataverseRaster.ps1" -Years 2025 -Action Download -CatalogVersion '10.1' -Destination $externalDir
Rscript --vanilla "$script/crop_annual_raster.R" (Join-Path $raw 'source.tif') $externalDir (Join-Path $raw 'source.json') 73 135.01 17.99 54
```

`externalDir` 为 Git 外的可写目录。脚本核对 Dataverse 文件字节数和校验值并保留原始 ZIP。裁剪后逐块读回，核对每个像元的数值与缺失位置。将返回目录里的 `source.json` 和 `crop.tif` 接入后续工作流。相同请求复用已校验文件。缺年、匹配歧义、归档异常或校验失败时停止接入。其他仓储按目录中的对应方式获取。

用于 GDP 时，将示例裁剪坐标替换为项目的 `geo.extent`，顺序为西、东、南、北。[GDP 接入说明](../../../../workflows/gridded_gdp/README_ZH.md#复用已有夜光裁剪)给出如何把返回的裁剪目录接到年度输入。
