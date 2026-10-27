# WorldPop API、注册入口与当前状态

复核日期：2026-10-26。数据来源、产品差异与质量规则见[方法说明](../../../../../methods/01_socioeconomic_natural_change/worldpop.md)，已验证的公开获取步骤见[首次获取示例](first-download-example.md)。

## 目录与区域统计分别使用

| 接口 | 用途与状态 |
|---|---|
| `https://hub.worldpop.org/rest/data` | 当前公开数据目录 REST API；已核对别名及一个国家/年份的 Global2 元数据 |
| `https://www.worldpop.org/rest/data` | 官方旧入口会重定向；脚本已改为直接访问 Hub，不依赖此地址 |
| `https://data.worldpop.org/` | 元数据返回的相对 `data_file` 的文件根；本次官方 TIFF 直接获取通过 |
| `https://api.worldpop.org/v2/` | 官方 Global2 区域统计服务，与目录/文件下载不同；项目没有其执行适配器，未提交统计任务 |

官方目录说明见[API Basics](https://www.worldpop.org/sdi/introapi/)，产品入口见 [Hub](https://hub.worldpop.org/project/categories?id=3)。旧文档中的端点或别名不能保证覆盖当前全部产品。

目录请求模式：

```text
GET https://hub.worldpop.org/rest/data/pop
GET https://hub.worldpop.org/rest/data/pop/<project>?iso3=<ISO3>
```

本次验证别名为 `G2_CN_POP_R25A_1km`、国家 `LIE`、`popyear = 2020`。Global1 的 `wpgp` 等别名属于另一组产品，不将两者混用。

## 过滤与实际执行

应按 `iso3`、`popyear`、产品类别、版本、单位和具体文件字段核对；`popyear` 表示人口数据年份，`date` 等发布字段不替代它。脚本的 `year` 现在严格匹配 `popyear`：允许整数或去除首尾空白后的整数文本与请求值相等，排除缺失、布尔、浮点及非精确年份。标题、说明、文件名和发布日期均不参与年份判断；`contains` 仍保留全文关键词筛选用途。年份及其他条件筛选完成后才应用 `limit`。

`worldpop_download` 已登记，支持元数据发现和可选文件下载的接口；本机本次 dry-run 无 blocker，但真实目录调用失败。未关闭 TLS 检查、继承私人代理/凭据或直接运行原脚本绕过执行器。官方公开接口小文件验证是单独记录的参考路线，不代表该工具运行验收通过。

2026-10-26 20:13:18–20:13:20（北京时间）复核更新后的 Hub 入口：Global2、LIE、2020、download=false、limit=1；dry-run 可执行，实际状态 failed、子进程退出码 1，未产生文件下载。17 个新增合成回归用例和全套 144 项测试通过；当前问题不通过取消安全检查处理。

`limit` 是本地筛选后保留记录数，不会把远端响应限制为相同数量。`download=false` 仍会联网并写元数据，不是无副作用预检。

## 元数据与路径

runner 任务元数据位于 `${AIRMOSAIC_ASSETS_DIR}/results/<project_id>/<run_id>/01_socioeconomic_natural_change/worldpop_download/metadata/`；直接官方接口的本次验证使用 `results/<project_id>/<run_id>/01_socioeconomic_natural_change/worldpop-global2/metadata/`。原文件分别存同任务的 raw，验收摘要在 `results/<project_id>/<run_id>/records/<tool_id>/`；不向 Git 写入原栅格、完整元数据或成员路径。

`data/01_socioeconomic_natural_change/WorldPop/<version>/` 仅作另行授权发布的复用缓存，不是当前任务的默认输出。参数放 CONFIG_DIR 的非秘密 JSON；公开获取不需要登录、API key 或认证会话。网络错误按当前安全配置排查，不取消证书验证或自动复制个人网络/登录配置。
