# 人口与健康基础数据

**状态**：AirMosaic 已登记 WorldPop 和 IHME GBD 的受控适配器。本次检查目录与说明，没有发起真实下载、检查私人会话或验证新数据版本。

| 数据 | 真实 tool_id | 输入与前置条件 |
|---|---|---|
| WorldPop | worldpop_download | 产品、国家、年份、下载范围；requests，联网授权 |
| IHME GBD | ihme_gbd_fetch_results | 版本、年份、地区、病因、年龄、性别、measure/metric；授权的本机浏览器会话 |

## 操作步骤

1. 将研究需求拆成产品/维度清单，明确人数、率、比例及不确定区间。
2. 阅读 [WorldPop skill](../../skills/data_acquisition/01_socioeconomic/worldpop/SKILL.md)或 [GBD skill](../../skills/data_acquisition/04_impact/ihme-gbd-results/SKILL.md)，查询 tool_id 和依赖。
3. 核对当次产品和页面维度 ID；历史参数示例不是当前业务含义的证明。本人会话由调用方准备，不能复制他人认证状态。
4. 按[数据获取指南](../../harness/usage/data-acquisition.md)准备非秘密 JSON，通过 run-tool dry-run 检查 blockers，再按授权执行。
5. 验证实际文件、请求维度、年份、空间范围、缺失和单位后，才纳入缓存和下游模型。

## 边界与验收

WorldPop 的 download=false 仍会联网发现并写元数据；人口重采样/分区统计没有独立已登记入口。GBD 的会话声明不是登录验证，check-tool 可继续显示认证 unverified。run-tool 的成功状态不验证科学口径。

健康计算还需要匹配的人口结构、死亡率、风险函数与浓度；数据获取不等同于完成健康模型。详见[浓度与健康方法](../04_impact/health_impacts.md)。

## 阶段与 Skill 映射

主目录：shared；适用阶段：01_socioeconomic, 04_impact。对应 [worldpop](../../skills/data_acquisition/01_socioeconomic/worldpop/SKILL.md)、[ihme-gbd-results](../../skills/data_acquisition/04_impact/ihme-gbd-results/SKILL.md)。执行状态以本文及真实工具 manifest 为准；没有 tool_id 的方法只供指导。
