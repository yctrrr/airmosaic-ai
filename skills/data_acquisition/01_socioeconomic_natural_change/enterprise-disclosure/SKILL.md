---
name: enterprise-disclosure-methods
description: Collect and verify scoped enterprise reports through authorized source websites and prepare a source-index handoff; no collection adapter is bundled.
---

# Enterprise reports and disclosure

**English** | [中文](SKILL_ZH.md)

Use for financial/annual/ESG reports or provincial environmental disclosures. Keep the requested source family explicit: provincial disclosures, listed-company announcements and database tables have different coverage.

## Prepare

Record enterprises or selection rules, reporting years, report types, permitted sources, and a maximum number of reports. Use an authorized browser and a PDF/Office reader; a spreadsheet editor is enough for the index. Keep source files in a fresh external `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/enterprise_disclosure/` folder. Non-secret query settings belong in `AIRMOSAIC_CONFIG_DIR`; retain login state in the existing authorized browser rather than exporting it.

## Collect and record

1. Open the source website, search the exact company and year, and distinguish the legal entity from its parent, subsidiaries and facilities.
2. Open each relevant listing, then the full report and attachments. Save the available originals without replacing earlier versions. A listing or attachment URL alone is not a complete report.
3. Maintain a CSV/worksheet with `entity_key`, `report_year`, `report_type`, `source`, `retrieved_at`, `local_file`, `version`, `status`, and `notes`. Keep authenticated URLs local. Mark inaccessible, metadata-only, missing-attachment and complete states separately.
4. Open saved files and compare entity, reporting period, report title and attachments with the source page. Record checksum and page/section references for extracted claims.
5. Deliver the index, verified originals and a coverage/gap table for the agreed scope. Stop an affected source on access restrictions or an unresolved challenge; preserve its status for the authorized follow-up.

No collector or `run-tool` ID is provided here. Existing external queues must be operated through their own reviewed task instructions. [CSMAR](../csmar/SKILL.md) provides a separate basic-company ZIP processor, not a disclosure crawler.

For source comparability and interpretation, use [enterprise-source methods](../../../../methods/01_socioeconomic_natural_change/enterprise_sources.md).
