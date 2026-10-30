---
name: gcam-configuration
description: Explain GCAM configuration chains or review authorized task-copy edits. Configuration is a manual reference, without a mutation or simulation adapter.
---

# 审查 GCAM 配置

[English](SKILL.md) | **中文**

`gcam_configuration_reference` 已入目录，但不支持 `run-tool` 执行。查看状态：

```sh
python -m runtime.cli describe-tool gcam_configuration_reference
```

显式选择外部 `GCAM_RELEASE_DIR`。解释任务仅检查指定 XML 及引用。修改获授权后，将所需配置及依赖复制到新任务目录，修改副本，检查 XML 解析、组件顺序、引用解析，并返回限定范围的 diff。编译、模拟需有各自任务范围。`examples/` 中的 JSON 是人工计划，不是 runner 参数。

按需读：[配置结构](references/configuration-files-overview.md)、[SSP/RCP](references/ssp-rcp-scenario-setup.md)、[输入链](references/input-data-chain-tracing.md)、[修改模式](references/common-config-manipulation.md)、[CCS](references/ccs-configuration-in-depth.md)、[部门命名](references/sector-naming-conventions.md)。编译、链接问题见[构建排错](../references/build-troubleshooting.md)。情景解释见[方法](../../../../../methods/04_integrated_impacts/gcam_ZH.md)。
