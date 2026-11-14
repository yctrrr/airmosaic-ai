# Common research data sources

**English** | [中文](sources_ZH.md)

| Entry | Retrieval |
|---|---|
| [Zotero](https://www.zotero.org/support/adding_items_to_zotero) | Look up the article or local supplement and follow its data DOI. |
| [Harvard Dataverse annual night lights](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YGIVCD) | Select a release and the annual Version 2 ZIP on the page, or use the skill's [Dataverse API route](https://guides.dataverse.org/en/latest/api/dataaccess.html). |
| [Zenodo](https://developers.zenodo.org/), [Figshare](https://docs.figshare.com/) | Open the dataset DOI, pick the cited version and save the stated files. Use the provider's records API where supported. |
| [ORNL LandScan](https://landscan.ornl.gov/) | Select LandScan Global and the observation year in the download portal. For this GDP workflow use the 30 arcsecond total-population raster. The producer also provides a [2000–2022 archive](https://doi.org/10.6084/m9.figshare.28439699). |
| [Copernicus C3S land cover](https://cds.climate.copernicus.eu/datasets/satellite-land-cover) | Choose v2.1.1 and the year in the official form, accept its terms and use the [annual CDS helper](../../../model/01_socioeconomic_natural_change/gridded-gdp/scripts/Get-CdsLandCover.ps1). Verify `lccs_class` and the embedded year. |
| [WorldPop](../../01_socioeconomic_natural_change/worldpop/SKILL.md), [ERA5](../../01_socioeconomic_natural_change/era5/SKILL.md) | Use the product-specific acquisition skills for catalog and download operations. |

CSMAR is a separate licensed input to the GDP workflow. Use the [CSMAR local skill](../../01_socioeconomic_natural_change/csmar/SKILL.md) for authorized intake.

See the [annual GDP inputs](../../../../workflows/gridded_gdp/README.md#prepare-a-real-project) for the county and province CSV fields and the handoff from a Dataverse crop.
