---
name: worldpop
description: 通过 worldpop_download 发现并按需下载指定国家、年份和产品的人口文件；分区统计另行实现。
---

# WorldPop 人口数据获取

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


> 调用状态：`worldpop_download` 支持通过执行器查询元数据及按需下载；分区统计没有独立可执行工具。

当前本机状态：官方目录元数据与直接获取的小文件已验证；执行器参数预检通过，实际目录调用尚未通过。见[接口状态](references/worldpop-api.md)。`year` 严格匹配 `popyear`，接受整数或整数文本，拒绝缺失、布尔、浮点及非精确年份；其他产品条件仍须核对。

产品来源、误差和规范化见[人口栅格方法](../../../../methods/01_socioeconomic_natural_change/worldpop.md)。首次获取按[公开目录与小文件示例](references/first-download-example.md)操作，无需账号或令牌。

## 工作目录与认证

遵守[存储约定](../../../../harness/storage-and-credentials_ZH.md)和[执行指南](../../../../harness/usage/run-tool.md)。仓库外三个已存在根目录相互独立：`AIRMOSAIC_LOCAL_WORKSPACE` 存数据与结果，`AIRMOSAIC_CONFIG_DIR` 存非秘密设置与任务参数，`AIRMOSAIC_AUTH_DIR` 存浏览器状态。密码和令牌留在秘密管理器，不读取或分享凭据、浏览器配置内容。命令从仓库根目录使用已安装解释器运行，默认输出为 `output/<run_id>/<tool_id>/`。个人配置不自动加载。直接运行脚本会绕过检查；执行器不是操作系统沙箱。

## 用途

按任务范围获取所需国家、年份和产品；栅格及派生表留在本地工作区，不进入 GitHub。

## 官方接口

- 当前数据目录及脚本地址：`https://hub.worldpop.org/rest/data`，不再从旧跳转地址开始。
- 独立区域统计服务：`https://api.worldpop.org/v2/`；本项目没有对应适配器或真实统计验证。
- 元数据常用文件服务器：`https://data.worldpop.org`。

官方有接口频率限制。缓存元数据与文件，避免重复查询相同产品。

## 结果与缓存

执行器写入 `${AIRMOSAIC_LOCAL_WORKSPACE}/output/<run_id>/worldpop_download/`：元数据位于 `metadata/`，下载位于 `raw/<iso3>/<project>/<year>/`。运行记录位于 `runs/<run_id>/record.json`，不含原参数值和文件名。

`${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/worldpop/` 是可复用缓存，不是执行器输出位置。发布缓存需另行授权；没有自动发布、栅格重采样或分区统计。

## 注册工具的调用

从仓库根目录使用真实工具编号，先查声明。工具编号是命令参数，不是参数文件内的键。

```powershell
python -m airmosaic_core.cli describe-tool worldpop_download
python -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --dry-run
# Discovery also uses the network and writes metadata; execute only within task authorization.
python -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --allow-network
```

公开示例：

```json
{"project":"wpgp","iso3":"CHN","year":2020,"download":false,"limit":1}
```

调用方只需提供 `project`，执行器补齐 `root`。`year` 与 `limit` 是整数，`download` 是布尔值，`contains`、`extensions` 是逗号分隔字符串而非数组。任务参数另存个人配置目录。只有明确下载任务才设置 `download=true`；即使为假仍会联网查询。未允许联网的预检返回权限阻塞，不执行请求。

## 代理执行边界

仅使用注册工具，不直接执行原脚本绕过路径或权限拒绝。元数据筛选不证明年份或产品适用；格式有效的国家代码或别名仍可能不存在。工具不自动验证下载内容、坐标系统、人口总量或科学适用性；复用或分享前核对任务产物。

## 产品选择

知道准确产品名时使用准确名称；含糊请求先查元数据，核对标题、文件名、年份和分辨率，再下载。

人口目录使用 `pop` 组下的项目别名，例如 `wpgp` 对应 2000–2020 年分国全球产品。

新一代全球产品属于独立系列。已验证样例为 `G2_CN_POP_R25A_1km`、LIE、`popyear = 2020`、R2025A v1、受约束且经联合国总量调整。查询真实别名并审查元数据，不能根据旧别名或日期文本认定支持。

常见筛选维度：

- 国家三字母代码。
- 产品或项目别名。
- 年份。
- 文件扩展名，如 `.tif`、`.tiff`、`.zip`、`.csv`。
- 标题、文件名和元数据中的年龄、性别说明。
- 是否经联合国总量调整。
- 是否为空间受约束产品。

## 检查清单

- 文件非空，扩展名符合预期。
- 文件旁保留元数据。
- 记录项目别名、国家、年份与下载地址。
- 核对显式年份、单位、版本、约束与调整口径、坐标、网格、缺失编码及有效值的有限非负性；发布日期或文本匹配不能替代这些检查。
- 未获任务授权不解压或重采样。
- 不提交原栅格、派生栅格、缓存清单或私人路径。

## 参考资料

- `references/worldpop-api.md`：接口地址和元数据字段。
- `references/privacy-redaction-rules.md`：脱敏检查。
