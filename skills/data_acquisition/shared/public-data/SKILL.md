---
name: public-data-acquisition
description: Trace public research datasets from articles and Zotero records and download and crop annual Dataverse raster archives with provider checksums.
compatibility: "PowerShell 7, curl, R with terra, jsonlite and digest. Direct scripts."
metadata:
  version: "0.1.0"
---

# Acquire public research data

**English** | [中文](SKILL_ZH.md)

Follow the [source method](../../../../methods/shared/public_data_acquisition.md) and the [common source directory](sources.md). Start from a DOI or authorized Zotero metadata and attachments, check the publisher's availability statement, and follow the dataset DOI. Importing citations or linking local attachments uses the existing [literature workflow](../literature-workflow/SKILL.md).

From the repository root, choose a fresh external destination. Use the first call to see the published files, then fix the release number for the download. This example selects one year of the harmonized NPP-VIIRS-like series.

```powershell
$script = './skills/data_acquisition/shared/public-data/scripts'
& "$script/Get-DataverseRaster.ps1" -Years 2025
$raw = & "$script/Get-DataverseRaster.ps1" -Years 2025 -Action Download -CatalogVersion '10.1' -Destination $externalDir
Rscript --vanilla "$script/crop_annual_raster.R" (Join-Path $raw 'source.tif') $externalDir (Join-Path $raw 'source.json') 73 135.01 17.99 54
```

`externalDir` is an existing writable directory outside Git. The script uses Dataverse file metadata for size and checksum verification and retains the original ZIP. The crop compares every persisted pixel and its missingness with the original. Use the returned crop directory's `source.json` and `crop.tif` for workflow intake. Repeat the same request to reuse verified artifacts. A missing year, ambiguous file, invalid archive or checksum mismatch stops intake. Other repositories in the source directory use their documented retrieval routes.

For GDP, use the project's `geo.extent` in west, east, south, north order in place of the illustrative bounds. The [GDP handoff instructions](../../../../workflows/gridded_gdp/README.md#reuse-an-existing-night-light-crop) show how to attach the returned crop directory to an annual input.
