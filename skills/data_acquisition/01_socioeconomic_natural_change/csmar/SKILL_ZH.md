---
name: csmar-downloader
description: 指导授权的 CSMAR 网页下载，并用 csmar_process_company_info 处理已有企业基本信息压缩包；网页下载不由执行器自动完成。
---

# CSMAR 数据获取

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


> 调用状态：`csmar_browser_download` 是不可执行的网页流程参考；仅 `csmar_process_company_info` 已接入执行器，用于已有企业信息压缩包。

## 工作目录与认证

遵守[共享存储约定](../../../../harness/storage-and-credentials_ZH.md)和[执行指南](../../../../harness/usage/run-tool.md)。仓库外三个已存在根目录相互独立：`AIRMOSAIC_ASSETS_DIR` 存数据与结果，`AIRMOSAIC_CONFIG_DIR` 存非秘密设置及任务参数，`AIRMOSAIC_AUTH_DIR` 存浏览器状态。密码和令牌留在秘密管理器，不读取或分享凭据及浏览器配置内容。仓库命令从根目录使用已安装项目的解释器运行。执行器默认分配 `results/<project_id>/<run_id>/01_socioeconomic_natural_change/<tool_id>/`，不自动加载个人配置。直接运行脚本会绕过检查；执行器不是操作系统沙箱。

从 `https://data.csmar.com/` 获取中国股票市场与会计研究数据库资料，用于第一步社会经济驱动分析。

## 所属研究步骤

`01_socioeconomic_natural_change`：为工业产出、能源使用及末端治理技术分析提供上市公司活动资料。

## 前置条件

- 已授权的浏览器工具；使用 JavaScript 浏览器流程时才需要 Node.js/Playwright。
- 具有机构数据权限的本人账号。
- Python 3.10+，以及 pandas、openpyxl。

## 网页获取参考

`csmar_browser_download` 的 `execution_supported: false`，执行器会拒绝调用。先查询目录信息，再使用宿主实际提供的授权浏览器工具或手动操作；项目没有浏览器启动或登录适配器。

首次访问、小范围获取、验收与本地处理衔接见[首次下载向导](references/first-download-guide_ZH.md)。来源质量统一见[企业来源方法](../../../../methods/01_socioeconomic_natural_change/enterprise_sources.md)。

[Chrome 已验证示例](references/first-download-example_ZH.md)记录了 2026-10-27 的八字段、单记录下载与落盘验收。网页获取与已接入执行器的本地处理保持分开。

1. 使用任务授权的浏览器会话。自行启动项目浏览器时，显式指定 `${AIRMOSAIC_AUTH_DIR}/browser_profiles/csmar/` 下的本人配置，设置变量不会自动选择配置。宿主管理的会话另有存储，这些变量不会迁移或约束该存储；不导出会话。
2. 本人登录并核对表权限，不导出会话信息或自动填写密码。
3. 选择任务要求的表、日期、记录与字段。仅在需要完整表时选择全部字段，提交前核对规模。
4. 提交查询生成下载记录，再打开记录完成最终保存。签名链接与账户资料留在本地。
5. 将导出及字段说明保存到授权缓存。存在下载记录不证明文件已落盘。

网页可提供 CSV/TXT 等格式，但下述处理器要求压缩包中包含工作簿；其他格式另行适配。浏览器操作有独立授权，不继承执行器路径保护。

## 核心表：上市公司基本信息

入口：

```
https://data.csmar.com/csmar.html#/datacenter/singletable/search?databaseId=176
```

需要核对的字段：

- 证券代码与简称。
- 统计截止日期。
- 证监会行业名称与代码。
- 统一社会信用代码。
- 中文全称。
- 省份、城市。
- 主营业务。
- 上市状态。

## 已注册的本地处理

使用已有压缩包，需要 pandas/openpyxl，无需网页登录。[公开参数](../../../../config/examples/run-tool/csmar.json)是普通 JSON 对象：

```json
{"zip":"${AIRMOSAIC_ASSETS_DIR}/data/01_socioeconomic_natural_change/CSMAR_ListedCompanyBasic/v1/company_basic.zip"}
```

将文件名映射为已授权输入，从仓库根目录运行：

```powershell
python -m airmosaic.cli describe-tool csmar_process_company_info
python -m airmosaic.cli run-tool csmar_process_company_info --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/csmar.json --dry-run
python -m airmosaic.cli run-tool csmar_process_company_info --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/csmar.json
```

执行器补齐 `out_dir`。脚本直接读取压缩包中的工作簿，不在输入旁解压或修改原件。结果位于 `results/<project_id>/<run_id>/01_socioeconomic_natural_change/csmar_process_company_info/`：

- `csmar_target_industry_company_candidates.csv`：行业候选记录。
- `csmar_target_industry_company_list_latest.csv`：最新公司记录。
- `csmar_target_industry_company_list_latest.xlsx`：包含两张表。

固定关键词覆盖火电、供热、钢铁、有色、水泥、石灰、砖瓦、玻璃和化工。当前实现使用区分大小写的英文关键词，并先选择每家企业的最新记录；核对语言、面板时期及空匹配。首次下载向导列出固定 15 列契约，其他表和格式另行适配。企业身份不能直接确定成本承担主体或物理生产边界；这不是通用财务报表处理器。

## 常见问题

| 问题 | 处理 |
|---|---|
| 导出字段缺失 | 核对网页格式选项；本地处理器对 CSV/TXT 需要适配 |
| 浏览器取消下载 | 查看 `chrome://downloads/`，再核对最终保存动作 |
| 登录账号不符 | 使用账号菜单退出，由本人重新登录 |
| 字段数量不符 | 重新选择任务字段并核对最终导出 |

## 参考资料

- [网页流程实现参考](references/csmar-api_ZH.md)：历史端点名称与当前接口边界。
- `examples/csmar_company_query.json`：查询参数示例。

数据与结果按[资产目录与复核入库规范](../../../../harness/assets_ZH.md)管理：数据按阶段、实际名称和版本共享；结果按项目及运行归集。跨阶段引用同一数据，复用入库需人工批准。
