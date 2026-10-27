# GBD Processing Validation

<!-- README-I18N:START -->

**English** | [中文](processing-validation_ZH.md)

<!-- README-I18N:END -->

Data meaning, uncertainty, age mappings and normalization rules live in the [GBD method](../../../../../methods/04_integrated_impacts/ihme_gbd.md). Keep processing code in the calling project; this reference is an operational checklist.

1. Confirm that fresh results match the reviewed query and round before exporting. Follow the [first-download guide](first-download-guide.md).
2. Preserve the original export and its schema. Write derived tables and validation reports separately under the task output directory in `AIRMOSAIC_LOCAL_WORKSPACE`; cache publication is a separate authorized operation.
3. Define an explicit mapping from source dimensions to project columns. Join by the full applicable key, including round, context, year, location, measure, metric, cause/risk, age and sex; do not assume project aliases such as endpoint or agegroup are source fields.
4. Compare mapped values to source rows within a declared numeric tolerance. Report requested combinations missing from the source, unexpected derived combinations, duplicates, non-finite values and invalid uncertainty ordering.
5. Keep raw exports, derived health tables, account information and temporary download links outside Git. Share only a reviewed summary.
