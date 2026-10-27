# 人口与健康基础数据

**状态**：AirMosaic 已登记 WorldPop 和 IHME GBD 的受控适配器。WorldPop 官方目录和 Global2 小文件直接获取已验证，run-tool 本机实际目录调用尚未通过；GBD 2023 全球全因死亡数量的单条网页查询、下载与 CSV 内容检查已通过，未执行 run-tool 真实调用。不检查或复制私人会话。

WorldPop 的产品来源、误差和规范化见 [01 人口栅格方法](../01_socioeconomic_natural_change/worldpop.md)，获取与时间记录见[小文件示例](../../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/references/first-download-example.md)。已验证的是人数/像元的单个 Global2 文件，区域汇总和健康计算另行适配。

GBD 的来源、估计误差、数量/率、年龄与不确定区间见 [04 GBD 方法](../04_integrated_impacts/ihme_gbd.md)，网页首次操作见[最小查询向导](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/references/first-download-guide.md)。人口分母产品需单独核对，不能从病因结果适配器推断已实现人口导出。

| 数据 | 真实 tool_id | 输入与前置条件 |
|---|---|---|
| WorldPop | worldpop_download | 产品、国家、年份、下载范围；requests，联网授权 |
| IHME GBD | ihme_gbd_fetch_results | 版本、年份、地区、病因、年龄、性别、measure/metric；授权的本机浏览器会话 |

## 操作步骤

1. 将研究需求拆成产品/维度清单，明确人数、率、比例及不确定区间。
2. 阅读 [WorldPop skill](../../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/SKILL.md)或 [GBD skill](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/SKILL.md)，查询 tool_id 和依赖。
3. 核对当次产品和页面维度 ID；历史参数示例不是当前业务含义的证明。本人会话由调用方准备，不能复制他人认证状态。
4. 按[数据获取指南](../../harness/usage/data-acquisition.md)准备非秘密 JSON，通过 run-tool dry-run 检查 blockers，再按授权执行。
5. 验证实际文件、请求维度、年份、空间范围、缺失和单位后，才纳入缓存和下游模型。

## 边界与验收

WorldPop 的 download=false 仍会联网发现并写元数据；人口重采样/分区统计没有独立已登记入口。GBD 的会话声明不是登录验证，check-tool 可继续显示认证 unverified。run-tool 的成功状态不验证科学口径。

健康计算还需要匹配的人口结构、死亡率、风险函数与浓度；数据获取不等同于完成健康模型。详见[浓度与健康方法](../04_integrated_impacts/health_impacts.md)。

## 阶段与 Skill 映射

主目录：shared；适用阶段：01_socioeconomic_natural_change, 04_integrated_impacts。对应 [worldpop](../../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/SKILL.md)、[ihme-gbd-results](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/SKILL.md)。执行状态以本文及真实工具 manifest 为准；没有 tool_id 的方法只供指导。
