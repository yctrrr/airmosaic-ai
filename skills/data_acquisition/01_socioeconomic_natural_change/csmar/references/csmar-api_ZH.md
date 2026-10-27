# CSMAR 网页流程实现参考

<!-- README-I18N:START -->

[English](csmar-api.md) | **中文**

<!-- README-I18N:END -->

当前访问、范围选择、下载和验收按[首次下载向导](first-download-guide_ZH.md)操作。本参考保留历史接口名称，供源码核对；它们不代表受支持的公共 API、当前端点已验证或 AirMosaic 已实现下载适配器。

## 历史接口名称

| 端点 | 历史用途 |
|---|---|
| `POST /api/csmar-main/single/saveOutline` | 创建查询记录 |
| `POST /api/csmar-main/singleData/pack` | 准备导出任务 |
| `GET /api/csmar-single/single/preview/<condition_id>` | 预览已记录的查询 |

首次验证不重构请求、不复制认证材料，也不抓取原始会话流量。访问方式变化或正式适配器需要另行限定实现范围。下载记录标识、认证链接和账户专用参数保留本地。

## 字段与格式检查

只选任务所需字段。仅当约定任务需要完整字段时才全选，核对已选名称与数量、字段说明及实际导出列。可选列表清空可能只是字段已移到已选列表，不代表丢失选择。

CSV、TXT 和 XLSX 是需在当前门户确认的格式选择，不预设通用可靠性排名。实际导出逐份检查编码、表头行、前导零、行数和缺列。已注册本地处理器只支持满足固定字段契约的 ZIP/XLSX；网页改选格式不会自动适配处理器。

## 会话与执行边界

自行启动项目浏览器时必须显式指定 `${AIRMOSAIC_AUTH_DIR}/browser_profiles/csmar/`；设置占位变量不会自动配置浏览器。宿主管理的会话有自己的存储，不迁移或导出。非秘密查询计划放 CONFIG_DIR，导出放数据工作区，凭据保留在本人受保护的机制中。

`csmar_browser_download` 仍为参考，`csmar_process_company_info` 是单独授权的本地处理工具，可通过 run-tool 和 MCP 调用。两者均不提供 CSMAR 自动登录或公共 API 凭据机制。
