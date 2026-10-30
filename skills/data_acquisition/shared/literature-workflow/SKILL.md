---
name: literature-workflow-methods
description: Find, deduplicate and verify research papers and supplements, then prepare an archive or reference-manager import handoff without a bundled collector.
---

# Literature discovery and handoff

**English** | [中文](SKILL_ZH.md)

Use for a bounded topic search or supplied DOI/title/link. This repository provides a manual workflow, with no collector or library-import adapter.

## Prepare and retrieve

1. Define the research question, sources, time/language limits and candidate cap. Use an authorized browser, PDF reader and a CSV/worksheet index. Choose a local library destination outside Git and a separate pending-review folder.
2. Search the existing index by DOI and normalized title before retrieving. Open the publisher/repository landing page; record title, authors, year, DOI or stable URL and document version.
3. Retrieve authorized main text and supplements separately. Keep dataset/code links as separate records. Open each saved file to confirm its actual type, title and readability; record failed retrievals without inventing attachments.
4. Review scope and relevance before moving files into the selected topic folder. A summary must cite page/section evidence and distinguish author claims from your assessment.
5. Prepare a reference-manager handoff listing bibliographic identity, local file, attachment role, target collection and duplicate decision. If library modification is requested, use the installed reference manager's reviewed import/link-file operation and verify the resulting item and attachments.

## Checks and optional external software

Deliver the search log, inclusion/exclusion decisions, verified file index, gaps and actual import status. A plan is not a completed import. Do not forward full texts to an external summarizer unless that use is authorized.

If an external literature project is selected, inspect its real CLI and configuration first. Historical names `run_weekly.py`, `run_summary.py` and `prepare_zotero_import.py` do not refer to scripts bundled here. In the previously reviewed external project, `run_weekly.py --dry-run` still used discovery/browser access and wrote archive/log files; `prepare_zotero_import.py` produced a plan without importing. Recheck the selected version before use.

For evidence synthesis and research limitations, read [literature methods](../../../../methods/shared/literature.md).
