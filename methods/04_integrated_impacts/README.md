# 04_integrated_impacts：综合影响评估

污染与环境变化对健康、经济、分配、生态、农业及气候的影响。GBD 已有受控获取适配器，单条网页查询、下载及内容检查已通过，run-tool 真实获取待验证；健康计算/绘图是模板，完整成本和分配流程需适配。

| 方法 | 状态 |
|---|---|
| [健康影响与情景配对](health_impacts.md) | mixed |

健康基础数据说明见 [IHME GBD 来源、指标与规范化](ihme_gbd_ZH.md)，作为[人口与健康方法](../shared/population_health.md)的补充页；网页首次操作见[获取向导](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/references/first-download-guide_ZH.md)。

下载前用[GBD 数据范围表](ihme_gbd_availability_ZH.md)选择指标、地区、年份与年龄；表中区分官方提供的产品、项目适配范围及本轮实际获取状态。

暴露比较或气象协变量需求可引用第一步的 [ERA5](../01_socioeconomic_natural_change/era5.md) 和 [CAMS](../01_socioeconomic_natural_change/cams.md) 获取参考；不复制下载流程，也不把它们自动视为已验证的健康模型输入。

站点浓度比较可引用第三步的 [PM2.5 站点方法](../03_atmospheric_transport/pm25_stations.md)。主目录仍在 03，04 仅引用；需核对时空匹配和代表性，不能直接将站点值当作人口暴露。

[数据获取入口](../../skills/data_acquisition/04_integrated_impacts/README.md)与[模型使用入口](../../skills/model/04_integrated_impacts/README.md)逐项连接 skill。具体顺序及交接见[四步流程](../../harness/four-step-workflow.md)。[共享方法](../shared/README.md)只在本步需要时引用，不复制实现。

生态、农业和气候影响目前为范围导航，需人工选择受体、响应指标、方法及验证依据；尚无对应执行技能或工具。自然环境变化作为上游条件在 01 获取，作为响应结果在本步评估。
