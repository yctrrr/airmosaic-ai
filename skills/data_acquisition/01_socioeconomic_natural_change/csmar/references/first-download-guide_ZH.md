# CSMAR 首次下载与本地交接

<!-- README-I18N:START -->

[English](first-download-guide.md) | **中文**

<!-- README-I18N:END -->

本向导用于成员协助完成首次下载。`csmar_browser_download` 仍是不可执行参考；`csmar_process_company_info` 处理已下载且兼容的 ZIP。网页环节尚不是 MCP 下载工具。

## 1. 准备权限与范围

打开[官方门户](https://data.csmar.com/)。由本人完成登录，核对所需表及时间范围在权限内；注册账号本身不证明拥有表权限。注册信息、验证码与协议均由本人处理。只记录权限状态，不记录账户资料。

首次限定一家企业和一个统计截止日。提交前确认具体表名、日期含义、字段定义与预期规模。现有[表入口](https://data.csmar.com/csmar.html#/datacenter/singletable/search?databaseId=176)仅为导航线索，不保证当前表身份；链接变化时按表名在门户查找。

小范围获取检查只选择已授权的企业与日期、名称、行业和地区字段。个人联系方式及管理人员信息只有另有需要和授权时才选。不因页面默认选项而扩大到全部企业、年份或字段。

## 2. 分开管理存储

新导出与字段说明保存到 `${AIRMOSAIC_ASSETS_DIR}/results/<project_id>/<run_id>/01_socioeconomic_natural_change/csmar_browser_download/`，不覆盖旧下载。非秘密查询计划放在 `${AIRMOSAIC_CONFIG_DIR}/csmar/`。自行启动的任务浏览器使用 `${AIRMOSAIC_AUTH_DIR}/browser_profiles/csmar/`，调用方必须实际配置该位置。

宿主管理的浏览器有自己的会话存储。设置这些变量不会迁移会话，也不证明该存储边界已生效。仅使用任务授权的会话，不导出或搬移登录状态。两种浏览器方式均不继承执行器的路径检查。

## 3. 查询并保存

在当前表单设置所需日期、企业代码和字段，支持预览时先看预览。创建下载任务前核对已选字段名称、数量和范围。缺少权限或出现验证提示时保留原范围，交由本人协助。

进入产生的下载记录，完成最终本地保存。任务排队时保留单个请求，重试前先核对状态。不发送下载邮件、不把认证链接复制到共享资料，也不调用未公开接口替代网页流程。字段说明与新导出共同保留。

在本地分别记录权限确认、范围确认、提交、文件保存完成和内容检查时间，统一时区，例如 `Asia/Shanghai`。待完成步骤保留待完成状态，不编造时间，不把服务端任务标识写进公开示例。

## 4. 验收新导出

- 确认文件是所需压缩包或数据，而非登录页、错误页；打开其中数据前先检查归档完整性。
- 比较已选字段、字段说明与实际列。预览或下载记录存在均不足以证明落盘文件正确。
- 企业代码按文本保留前导零。核对所需企业与日期、非空记录、重复键及缺失；未查看表的主键定义前，不假设恰好只有一行。
- 保留源值和字段含义。数据质量与分析边界统一见[企业来源方法](../../../../../methods/01_socioeconomic_natural_change/enterprise_sources_ZH.md)。

本次验证只检查新获取且在任务授权内的文件，不读取既有原始数据。导出和详细检查记录留在 Git 外；共享状态、数量与通用字段契约。

## 5. 判断是否适合本地处理

现有处理器要求 ZIP 中有 XLSX 工作簿，且具备下列准确列名：

```text
Symbol EndDate ShortName FullName
IndustryName IndustryCode IndustryNameC IndustryCodeC
IndustryNameD IndustryCodeD SocialCreditCode PROVINCE CITY
MAINBUSSINESS LISTINGSTATE
```

字段较少、仅用于获取验证的导出不满足此契约。只有在约定范围内才补充获取字段，或单独适配处理器；不虚构缺失列，不在未经核对的情况下改列名。多个工作簿、其他结构、CSV/TXT 或其他数据表均需人工核对或适配。格式和导出语言以当前来源实际选项为准。

当前筛选使用区分大小写的英文关键词，并先保留每家企业的最新日期再筛选。列齐全不证明行业筛选有效。中文或其他语言文本、大小写、目标面板时期及空匹配均需审核。这些是当前实现边界，不是可静默套用的规范化规则。

对于已授权且兼容的 ZIP，准备个人任务 JSON，例如：

```json
{"zip":"${AIRMOSAIC_ASSETS_DIR}/results/<project_id>/<run_id>/01_socioeconomic_natural_change/csmar_browser_download/company_basic.zip"}
```

替换为实际授权文件名。使用项目解释器查询 `csmar_process_company_info`，以个人 JSON 预检，再在任务授权内执行。执行器分配全新输出目录并写脱敏回执，读取 ZIP 时不在输入旁解压。

通过 MCP 使用同一工具编号，预检对象如下：

```json
{"parameters":{"zip":"${AIRMOSAIC_ASSETS_DIR}/results/<project_id>/<run_id>/01_socioeconomic_natural_change/csmar_browser_download/company_basic.zip"},"dry_run":true}
```

MCP 实际处理需要服务启动时授予 `--execute-tool csmar_process_company_info`，再在单次任务授权内使用 `dry_run: false`；不需要联网或浏览器授权。核对 `can_execute`、`blockers`，随后检查实际回执及三个预期输出文件。处理成功不等于企业候选名单通过科学验收。

## 当前验证状态

2026-10-27，首次限定范围的 Chrome 下载和落盘内容检查已通过：八个字段、一条有效记录。网页动作和操作时间见[已验证示例](first-download-example_ZH.md)。现有 ZIP 处理器和 MCP 执行边界另有合成检查；八列样例没有用于真实行业筛选。

导航与操作依据：由大学图书馆托管的供应商 [CSMAR Solution 用户手册第 3.1、3.3.1 节](https://library.zuel.edu.cn/_upload/article/files/16/da/a36893834ff8978060d5256a93b8/2eb4b7ef-b51f-4606-9535-223c4fe52b90.pdf)。手册说明通用的权限、查询与保存流程，当前字段和权限仍在实际门户核对；上列处理器契约来自仓库实现。
