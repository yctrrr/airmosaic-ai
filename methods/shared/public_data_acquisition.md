# Acquire public research data

**English** | [中文](public_data_acquisition_ZH.md)

Begin with the paper's data availability statement, supplement, DOI or an existing Zotero item. Record the original producer, repository, dataset identifier, release and file identifier separately. Verify the coverage, variable definition, units, release date and access terms on the provider record. For an annual input, distinguish the geophysical or statistical year from the catalog publication date.

Request only the files the task needs. Use the provider's file manifest and byte count or checksum, then verify the delivered bytes, actual format and contents. Record a local SHA-256 and the transformation if files are unpacked or cropped. A native-grid crop selects cells without changing their values, resolution or origin. A transformed product should keep a reference to its verified source and disclose any resampling.

Use the [public data skill](../../skills/data_acquisition/shared/public-data/SKILL.md) and its source directory for working links and retrieval commands.

Choose a crop that covers the downstream study extent. Keep the cropped TIFF with its source receipt so the next workflow can identify the product, observation year, release and actual footprint. The native crop preserves source cells. The receiving workflow performs any analysis-specific aggregation, such as summing light and population over the same support for GDP predictors.

For the night-light example, Harvard Dataverse is the distributor; the producer's harmonized series is distinct from raw satellite radiance. Its [dataset DOI](https://doi.org/10.7910/DVN/YGIVCD) has versioned updates beyond the original [Chen et al. (2021) data description](https://essd.copernicus.org/articles/13/889/2021/). Record the chosen release rather than inferring its units from the paper title. ORNL's [LandScan Global description](https://www.nature.com/articles/s41597-025-04817-z) defines ambient population counts at 30 arcseconds. Changing source/model inputs between annual releases can affect comparisons. GDP uses that ambient population as a proxy weight, which may differ from the population denominator of official GDP statistics. The [CDS land-cover record](https://cds.climate.copernicus.eu/datasets/satellite-land-cover) distinguishes product versions and quality flags. Annual alignment alone does not eliminate these measurement differences.

Official API responses must be valid metadata. An access page, temporary repository failure or unavailable year stops acquisition; do not disable TLS verification or replace a missing product silently. The source directory states which routes are automatic, official-client-assisted or manual. Zotero provides discovery/attachment context, not a universal permission to fetch or redistribute data.
