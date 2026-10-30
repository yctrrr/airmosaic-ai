---
name: csmar-downloader
description: Guide authorized CSMAR browser downloads and process an existing listed-company basic-information ZIP with csmar_process_company_info. Browser download is not automated by run-tool.
---

# CSMAR 数据下载与本地处理

[English](SKILL.md) | **中文**

`csmar_browser_download` 是不可执行浏览器参考；`csmar_process_company_info` 可通过 `run-tool` 处理已下载且兼容的企业基础信息 ZIP。

## 准备

本地处理使用已安装项目的 Python 3.10+、`pandas`、`openpyxl`。网页获取需要本人机构权限和宿主实际可用的浏览器；仅选择 JavaScript 流程时才需 Node.js/Playwright。数据/结果、非秘密配置和浏览器状态分别放在 Git 外 `AIRMOSAIC_ASSETS_DIR`、`AIRMOSAIC_CONFIG_DIR`、`AIRMOSAIC_AUTH_DIR`；不会自动加载个人配置。

## 网页下载参考：csmar_browser_download

该参考的 `execution_supported: false`，`run-tool` 会拒绝；可用 `describe-tool csmar_browser_download` 查看元数据。本仓库没有浏览器启动或登录适配器。首次访问、限定获取、格式验收见[首次下载向导](references/first-download-guide_ZH.md)；[Chrome 历史示例](references/first-download-example_ZH.md)记录了 2026-10-27 的八字段一条记录下载及保存文件检查，不代表本次执行。

1. 使用任务授权浏览器。若自行启动项目浏览器，应实际配置 `${AIRMOSAIC_AUTH_DIR}/browser_profiles/csmar/`；设置变量本身不会选择 profile。宿主管理会话的存储位置另计，不导出会话。
2. 由成员完成认证并确认表权限，不导出 cookie 或自动填写密码。
3. 在 [CSMAR 门户](https://data.csmar.com/)选择所需表、日期、记录与字段；仅任务要求完整表时选择全部字段，提交前检查字段和查询规模。
4. 提交后打开下载记录，使用最终本地保存动作；认证下载链接和账号信息仅留本地。
5. 在授权数据缓存保存导出及字段说明。存在下载记录不代表已保存文件。

网页可能支持 CSV/TXT，但下述处理器只接收含 XLSX 的 ZIP。其他格式需另行适配，浏览器操作不继承 runner 路径检查。

## 上市公司基本信息表

[既有导航入口](https://data.csmar.com/csmar.html#/datacenter/singletable/search?databaseId=176)仅供定位，实际表身份在门户核对。任务所需关键字段包括证券代码/简称、统计截止日、行业名称/代码及分类版本、统一社会信用代码、中文全称、省市、主营业务和上市状态。

处理器所需的完整十五列见[向导字段契约](references/first-download-guide_ZH.md)。八字段的小范围获取不能直接用于该处理器；不能为了通过处理而虚构缺列。

## 本地处理：csmar_process_company_info

不需要浏览器登录。将[公开参数示例](../../../../config/examples/run-tool/csmar.json)的文件名改为授权输入，或建立个人参数文件：

```json
{"zip":"${AIRMOSAIC_ASSETS_DIR}/data/01_socioeconomic_natural_change/CSMAR_ListedCompanyBasic/v1/company_basic.zip"}
```

从仓库根目录执行；个人参数文件需相应替换 `--params-file`：

```powershell
python -m runtime.cli describe-tool csmar_process_company_info
python -m runtime.cli run-tool csmar_process_company_info --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/csmar.json --dry-run
python -m runtime.cli run-tool csmar_process_company_info --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/csmar.json
```

runner 自动提供 `out_dir`。脚本直接读取 ZIP 内工作簿，不在输入旁解压或修改原件。输出位于 `results/<project_id>/<run_id>/01_socioeconomic_natural_change/csmar_process_company_info/`：

- `csmar_target_industry_company_candidates.csv`：行业匹配行。
- `csmar_target_industry_company_list_latest.csv`：最新企业记录。
- `csmar_target_industry_company_list_latest.xlsx`：两张表。

固定关键词覆盖火电、供热、钢铁、有色、 水泥、石灰、砖瓦、玻璃和化工。当前先保留每家公司最新记录，再按区分大小写的英文关键词筛选；应检查语言、面板期间及空匹配。它不是通用财务报表处理器；公司身份也不能直接确定成本支付者或物理生产边界。来源质量见[企业来源方法](../../../../methods/01_socioeconomic_natural_change/enterprise_sources_ZH.md)。

## 结果检查

预检 `can_execute=true` 且 `blockers` 为空后，检查实际 runner 状态与上述三份文件。打开工作簿两张表，对照匹配数与独立公司数，检查日期、重复代码、语言匹配与空结果。`match_keywords` 列出该行业配置的词表，不是企业实际命中的具体词。保留输入 ZIP、字段说明与验收记录；处理成功不等于行业覆盖或主体/设施资格已确认。

## 按需参考

- [浏览器流程实现说明](references/csmar-api_ZH.md)：历史端点名称和接口边界。
- [查询示例](examples/csmar_company_query.json)：查询声明，不是下载 API 或可执行包装器。
