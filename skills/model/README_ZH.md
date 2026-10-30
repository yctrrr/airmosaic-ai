# 模型使用

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->


按[四步流程](../../harness/four-step-workflow.md)进入：

- [01_socioeconomic_natural_change：社会经济与自然变化](01_socioeconomic_natural_change/README_ZH.md)
- [02_emission_inventory：排放清单](02_emission_inventory/README_ZH.md)
- [03_atmospheric_transport：大气输送与化学](03_atmospheric_transport/README_ZH.md)
- [04_integrated_impacts：综合影响评估](04_integrated_impacts/README_ZH.md)

没有明确主阶段的通用能力见[共享目录](shared/README_ZH.md)，有阶段归属的能力可由其他阶段引用，每步对应方法见[方法库](../../methods/README_ZH.md)。

数据与项目结果遵循[资产规范](../../harness/assets_ZH.md)：共享数据按阶段、实际名称和版本保存；结果按项目及运行归集，跨阶段引用同一数据。复用入库采用计算检查、人工复核、登记新版本三步。

目录规则为 `skills/model/<stage>/<capability>/`，阶段值与 `methods/<stage>/` 对应，无明确主阶段的通用能力使用 `shared`，其他阶段引用有主阶段的能力。方法说明与操作技能通过 `methods/index.yaml` 明确映射；一个方法可引用多个技能，但每个技能只有一个维护位置。
