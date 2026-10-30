---
name: ihme-gbd-results
description: 使用已有授权本机浏览器会话及已核实版本/维度 ID，经 ihme_gbd_fetch_results 获取限定范围的 IHME GBD 病因结果。
---

# IHME GBD 结果

[English](SKILL.md) | **中文**

`ihme_gbd_fetch_results` 在已有任务自有 loopback CDP 会话获取病因结果表，不启动浏览器或登录。依赖 Python 3.10+、已安装项目、`pandas`、`requests`、`websocket-client`。

指标选择见 [GBD 方法](../../../../methods/04_integrated_impacts/ihme_gbd_ZH.md)及[可获取范围表](../../../../methods/04_integrated_impacts/ihme_gbd_availability_ZH.md)：死亡、YLLs、YLDs、DALYs、发病/患病可按病因选择；风险归因、SEV、HALE、人口、生育及生命表需各自核实渠道和维度。仅改 `context` 不会补齐风险/专题参数，`population_group` 不表示人口数量导出。

## 准备与运行

1. 本人打开 [GBD Results](https://vizhub.healthdata.org/gbd-results/)，处理条款、登录和验证，确认范围。普通网页导出按[首次向导](references/first-download-guide_ZH.md)，无需 CDP。
2. 适配器使用 `AIRMOSAIC_AUTH_DIR/browser_profiles/ihme-gbd/` 中任务自有 Chromium profile 与仅 loopback 的 CDP 端口，核实端口归属和当前页面选择。可执行路径映射及非秘密 JSON 放 CONFIG_DIR，不检查或复制认证状态。
3. 适配[参数示例](../../../../config/examples/run-tool/gbd.json)。必需的 `years`、`locations`、`causes`、`ages`、`sexes`、`measures`、`metrics` 是逗号分隔数字字符串（如 `"ages":"10,11"`），非数组/范围。按核实结果设整数 `version`、`port`、`population_group`、`wait_ms` 和字符串 `context`；runner 分配 `out`。

```powershell
python -m runtime.cli describe-tool ihme_gbd_fetch_results
$gbdParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gbd-task.json"
python -m runtime.cli run-tool ihme_gbd_fetch_results --project-id example_project --stage 04_integrated_impacts --params-file $gbdParams --dry-run --allow-network --confirm-browser-session
python -m runtime.cli run-tool ihme_gbd_fetch_results --project-id example_project --stage 04_integrated_impacts --params-file $gbdParams --allow-network --confirm-browser-session --timeout 300
```

仓库根目录运行，数据/配置/认证根在 Git 外分别存在。检查 `can_execute`/`blockers`，会话声明不验证登录或 ID。历史默认 `version=8352`、`context=cause`、`population_group=1`、`port=9222` 只作语法示例，不证明当前发布版映射。

## 检查与交付

runner 写入 `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/04_integrated_impacts/ihme_gbd_fetch_results/results.csv` 和 `results.csv.json`。检查 sidecar 错误/新鲜状态、返回维度、实际行数、重复键、缺失组合、有限值，以及存在区间时 `lower ≤ val ≤ upper`。错误后残留旧行不算成功。源表与派生核对见[处理验收](references/processing-validation_ZH.md)。

2026-10-26 历史证据：网页路线取得 717 字节 ZIP，含全球/全因/2023/全年龄/两性/死亡/数量单条记录和 18 列；真实 runner 调用仍待 CDP 归属核验。[范围表](../../../../methods/04_integrated_impacts/ihme_gbd_availability_ZH.md)保留产品覆盖与未执行的中国/基线方案。

raw、processed、quality 分开，保留轮次和完整维度。复用缓存 `data/04_integrated_impacts/GBD_MortalityRates/<version>/` 需另行复核发布。不导出账号、cookies 或临时任务链接。
