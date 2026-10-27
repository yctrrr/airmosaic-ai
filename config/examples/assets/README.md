# Project and asset templates

**English** | [中文](README_ZH.md)

Copy only selected templates to a reviewed private location. These files contain synthetic labels and no real data. They are documentation templates, not automatically loaded configuration or executable tool parameters.

- [Project](project.example.json): input references, task requirements and project acceptance conditions. Keep the real copy under CONFIG_DIR.
- [Asset](asset.example.json): actual dataset name, fixed version, primary/applicable stages, workspace-relative path, data type and provenance. Keep completed metadata beside the registered dataset.
- [Review](review.example.json): pending file selection, checks and human decision. Keep the completed record with the source results. Hashes and approval are populated only in a separately authorized review; a template is not approval.

For tool execution, use [run-tool parameters](../run-tool) and explicit project/stage context. Reference paths are checked by the runner; asset IDs in these templates are not currently resolved automatically. The [asset contract](../../../harness/assets.md) defines the three-step process and legacy compatibility.
