# Scientific review — pending template

**English** | [中文](review_ZH.md)

**Status: pending.** This public file is a review checklist, not a completed approval record. Scientific project experiments have not been approved by creating this file.

For each reviewed experiment, record the experiment ID, actual run ID, configuration hash, fixed input version, checks, scientific interpretation and unresolved limitations. Select exact files by their hashes and specify an approved use. Keep the actual decision and any private details with the experiment's private results, using the [review template](../../config/examples/assets/review.example.json).

Review questions:

- Are the study cohort, target and predictor roles appropriate for the scientific question?
- Were development decisions separated from final testing, with comparable stations and baselines?
- Do performance and explanation claims match the validation design and uncertainty evidence?
- Do selected files preserve observation, prediction or processed-data types and provenance?
- Which precise files and uses, if any, are approved for reuse?

The agent cannot approve its own output. A successful workflow does not automatically promote results into `data/`; follow the [asset review contract](../../harness/assets.md).
