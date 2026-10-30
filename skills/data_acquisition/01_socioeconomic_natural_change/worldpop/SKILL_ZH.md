---
name: worldpop
description: 通过 worldpop_download 发现并按需下载 WorldPop 人口产品，明确国家、人口年份和发布版；栅格分析另行实现。
---

# WorldPop 获取

[English](SKILL.md) | **中文**

`worldpop_download` 支持公开目录发现和可选下载。依赖 Python 3.10+、已安装项目与 `requests`。设置 Git 外独立且已存在的 `AIRMOSAIC_ASSETS_DIR`、`AIRMOSAIC_CONFIG_DIR` 和 `AIRMOSAIC_AUTH_DIR`；公开请求无需账号或令牌。

历史状态（2026-10-26）：官方 Hub 元数据与直接 Global2 小文件获取通过；runner 预检通过，但真实目录调用失败。见[接口状态](references/worldpop-api.md)和[直接获取示例](references/first-download-example.md)，两条路线证据分别记录。

## 配置与运行

依据 [WorldPop 方法](../../../../methods/01_socioeconomic_natural_change/worldpop_ZH.md)选择产品、国家、`popyear`、版本、分辨率、约束方式和调整基准。[公共参数文件](../../../../config/examples/run-tool/worldpop.json)为：

```json
{"project":"wpgp","iso3":"CHN","year":2020,"download":false,"limit":1}
```

复制至 CONFIG_DIR 后适配。`project` 是 WorldPop 别名，不是 AirMosaic 项目 ID；runner 提供 `root`。`year`/`limit` 为整数（limit 1–100），`download` 为布尔，`contains`/`extensions` 是逗号分隔字符串。年份仅精确匹配 `popyear`，接受整数/整数文本，排除缺失、布尔和浮点年份；其他产品条件另查。`limit` 在筛选后应用，不限制远端响应量。

```sh
python -m runtime.cli describe-tool worldpop_download
python -m runtime.cli run-tool worldpop_download --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/worldpop.json --allow-network --dry-run
python -m runtime.cli run-tool worldpop_download --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/worldpop.json --allow-network
```

检查 `can_execute` 和 `blockers`。dry-run 不请求网络；真正运行时 `download=false` 仍联网并写元数据，限定文件获取改为 `true`。命令从仓库根执行，实际任务改用个人参数文件路径。

## 检查输出

目录为 `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/worldpop_download/`，`metadata/` 含 JSON/CSV，`raw/<iso3>/<project>/<year>/` 含文件。检查真实状态、元数据数量与条件、文件名及非空下载，再解码核对单位、CRS、网格、NoData、有限非负有效值和覆盖。零匹配不等于完成所需获取。

[已验证直接示例](references/first-download-example.md)使用 `G2_CN_POP_R25A_1km`、LIE、2020、R2025A v1、constrained 和 UN-adjusted，不证明旧 `wpgp` 别名支持 Global2。本目录无区域统计 API v2、重采样或分区统计适配器。复用缓存 `data/01_socioeconomic_natural_change/WorldPop/<version>/` 需另行复核发布，runner 不自动提升文件。
