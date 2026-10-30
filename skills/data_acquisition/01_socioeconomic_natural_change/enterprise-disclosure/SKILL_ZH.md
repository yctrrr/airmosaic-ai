---
name: enterprise-disclosure-methods
description: Collect and verify scoped enterprise reports through authorized source websites and prepare a source-index handoff; no collection adapter is bundled.
---

# 企业报告与环境披露

[English](SKILL.md) | **中文**

用于财务报告、年报、ESG 或省级环境披露。先明确来源类别：省级披露、上市公告与数据库表的覆盖范围不同。

## 准备

记录企业名单或筛选规则、报告年份、类型、允许来源和报告数量上限。使用已授权浏览器及 PDF/Office 阅读器；索引用电子表格即可。在外部 `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/enterprise_disclosure/` 新建任务目录保存原件。非秘密查询设置放在 `AIRMOSAIC_CONFIG_DIR`；沿用已授权浏览器会话，不导出登录状态。

## 获取与记录

1. 在来源网站按准确企业与年份查询，区分法人、母子公司和设施。
2. 依次打开列表、报告正文与附件；保存可取得原件，不覆盖旧版本。只有列表或附件链接时不能算完整报告。
3. 建立 CSV/工作表：`entity_key`、`report_year`、`report_type`、`source`、`retrieved_at`、`local_file`、`version`、`status`、`notes`。认证链接仅留本地；区分无法访问、仅元数据、附件缺失与完整。
4. 打开已保存文件，对照网页核对主体、报告期、标题和附件。记录校验和，以及提取结论的页码/章节。
5. 交付索引、已验证原件和约定范围的覆盖/缺口表。遇到访问限制或未解决挑战，停止受影响来源并保留状态，交由已授权后续流程处理。

这里没有采集器或 `run-tool` ID。已有外部队列应遵照其所属任务操作说明。[CSMAR](../csmar/SKILL_ZH.md) 提供独立的企业基础信息 ZIP 处理器，不能用作披露爬虫。

来源可比性和解释见[企业来源方法](../../../../methods/01_socioeconomic_natural_change/enterprise_sources_ZH.md)。
