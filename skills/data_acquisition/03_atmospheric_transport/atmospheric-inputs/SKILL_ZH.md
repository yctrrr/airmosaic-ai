---
name: atmospheric-input-methods
description: 为指定版本 GEOS-Chem 明确气象、初始和边界条件及诊断输入契约；参考技能，无下载器。
---

# 大气模式输入契约

[English](SKILL.md) | **中文**

为选定的 GEOS-Chem Classic 或 GCHP 版本整理输入清单；本参考没有下载器、执行适配器或 run-tool ID。

## 明确配置

记录准确版本、Classic/GCHP、模拟类型、时间范围、水平/垂直网格与重启时刻。以选定版本的配置与输入说明为准，不从文件名推断兼容。

| 输入 | 记录契约 | 交接前检查 |
|---|---|---|
| 气象 | 产品/发布版、频率、网格、垂直坐标和必要变量 | 完整时次、单位、日历和层顺序 |
| 初始/重启场 | 模式/物种版本、初始化时刻、单位和网格 | 物种映射与起始时刻一致性 |
| 嵌套边界 | 母域来源、边界频率、物种和水平/垂直映射 | 区域覆盖、时间插值及边界/层次一致性 |
| 诊断 | 字段、频率、平均方式和输出坐标 | 足够解释评价指标和质量收支的定义 |
| 排放接口 | 必需物种、单位、时间与空间支持 | 仅概念兼容，清单构建另有方法 |

交付清单、未决兼容问题和有范围的获取计划，注明来源版本与预期文件。模式自身 dry-run 会执行程序并写日志，需另有运行范围。

一般气象协变量和成分场见 [ERA5](../../01_socioeconomic_natural_change/era5/SKILL_ZH.md)、[CAMS](../../01_socioeconomic_natural_change/cams/SKILL_ZH.md)，其文件需另行转换才能符合 GEOS-Chem 契约。科学背景见[输送方法](../../../../methods/03_atmospheric_transport/README_ZH.md)。

非秘密设置、数据结果和会话分别在 Git 外的 CONFIG_DIR、ASSETS_DIR、AUTH_DIR。本技能整理契约，不自动获取或检查原输入。
