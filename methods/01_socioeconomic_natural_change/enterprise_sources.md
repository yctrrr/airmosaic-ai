# Enterprise financial and environmental sources

**English** | [中文](enterprise_sources_ZH.md)

## Research question

Use these sources to identify which enterprises report an activity, financial quantity or environmental action in a defined period. Define the population first: listed-company reports, industrial-enterprise statistics and provincial environmental disclosure systems cover different entities.

## Sources and definitions

Database tables such as CSMAR/RESSET provide structured fields; annual/ESG reports and provincial disclosures provide original narratives and attachments. Keep each table's definitions, original source, reporting boundary, statistical date, publication date and revision separately. Database curation does not make every field a direct transcription of the same original report.

For CSMAR, field documentation reviewed on 2026-10-27 indicated that `IndustryName`/`IndustryCode` use the listed-company association classification from 2023 and the applicable CSRC classification earlier. `IndustryNameC`/`IndustryCodeC` refer to the 2012 CSRC scheme and become blank after updates cease in 2023; `IndustryNameD`/`IndustryCodeD` use the association scheme. Recheck the selected export's dictionary rather than treating this historical observation as a permanent rule. Main-business and listing-status fields can reflect nearby/latest available information rather than the intended historical year-end.

## Organization and comparison

Keep securities codes as text, entity identifiers separate from securities, and parent/subsidiary/facility boundaries explicit. Use entity–period–report-type–version keys. Compare a listing with the saved full report and attachments; retain source references and revision evidence. A missing report, inaccessible report and observed zero are different observations.

## Error and quality

Evaluate population coverage, survivor selection, repeated reports, revisions, key validity, units and structural missingness. Listed companies cannot stand for all industrial firms without a sampling argument. A keyword-based candidate list needs review against full report evidence; empty matches can reflect language or classification mismatch. Source disagreement is a review item rather than a reason to overwrite one source automatically.

## Interpretation

A report supports only its stated entity, period and boundary. Financial amounts do not establish physical output, and legal identity alone does not establish a cost payer. Preserve quoted evidence and mark unresolved classifications before constructing [enterprise panels](enterprise_panels.md). Retrieval and file checks are described in the [disclosure skill](../../skills/data_acquisition/01_socioeconomic_natural_change/enterprise-disclosure/SKILL.md) and [CSMAR skill](../../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL.md).
