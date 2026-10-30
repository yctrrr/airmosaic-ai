---
name: literature-workflow-methods
description: Find, deduplicate and verify research papers and supplements, then prepare an archive or reference-manager import handoff without a bundled collector.
---

# 文献发现与交接

[English](SKILL.md) | **中文**

用于有限主题检索或给定 DOI、标题、链接。本仓库提供人工流程，没有收集器或文献库导入适配器。

## 准备与获取

1. 明确研究问题、来源、时间/语言范围与候选数量上限。使用已授权浏览器、PDF 阅读器及 CSV/工作表索引；选择 Git 外文献库和独立待审核目录。
2. 获取前按 DOI 与规范化标题查询已有索引。打开出版方/仓储落地页，记录标题、作者、年份、DOI 或稳定链接和版本。
3. 分开获取获授权主文和补充材料，数据/代码链接另列。打开每个保存文件核对真实格式、标题和可读性；获取失败如实记录。
4. 审核主题与相关性后再放入选定分类目录。摘要提供页码/章节证据，区分作者结论和自己的判断。
5. 准备文献管理器交接表：文献身份、本地文件、附件角色、目标集合和重复项处置。任务要求修改文献库时，使用已安装管理器的已审核导入/链接文件操作，再核对条目与附件。

## 检查与可选外部软件

交付检索记录、纳入/排除理由、文件索引、缺口和实际导入状态。导入计划不能当作已导入；未经授权不将全文送往外部总结服务。

选择外部文献项目时，先检查其真实 CLI 和配置。历史名称 `run_weekly.py`、`run_summary.py`、`prepare_zotero_import.py` 均不是本仓库脚本。此前核对的外部版本中，`run_weekly.py --dry-run` 仍会发现来源、访问浏览器并写归档/日志，`prepare_zotero_import.py` 只生成计划。使用时重新核对所选版本。

证据综合与研究局限见[文献方法](../../../../methods/shared/literature_ZH.md)。
