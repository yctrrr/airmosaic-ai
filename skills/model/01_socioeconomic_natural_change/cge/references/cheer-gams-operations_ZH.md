# 使用仓库外的 CHEER GAMS 版本

[English](cheer-gams-operations.md) | **中文**

[CHEER 下载页](https://cheer.org.cn/downloads/)提供 CHEER 的 Python、GAMS 演示版和 CHEER-P 的 GAMS 演示版。其 GAMS 版本需要 GAMS 许可证。模型压缩包、GDX 数据、GAMS 安装和许可证均保存在本仓库外。本技能的 Python CGE 教学模型是独立的合成模型，**不运行 CHEER**。

## 检查和复现已取得的版本

1. 记录官方下载页、压缩包名称、下载日期、版本或基年说明及文件哈希。保留未修改的原件，在仓库外另建工作副本。运行前先查看文件。
2. 确认实际入口。此前检查过的演示包以 `run.gms` 为入口，但取得新压缩包后须重新核对。阅读启用的 `$include`、`$batinclude`、`$gdxin` 及模型求解语句。GAMS 的[包含文件解析](https://www.gams.com/latest/docs/UG_DollarControlOptions.html)受工作目录和 `InputDir` 影响；在区分大小写的系统上核对文件名，并找到所有引用的 GDX 文件。
3. 检查 `gams -v`、模型适用的求解器及 [GAMS 许可证](https://www.gams.com/latest/docs/UG_License.html)。缺少任一必要条件时，只能报告**源码预检**，不能把源码解析称为数值复现。
4. 先从已确认的模型工作目录运行原样基准。如果实际入口确为 `run.gms`，可用 `gams run.gms lo=2`。保存命令、列表文件（`.lst`）、求解器/模型状态和输出，并将求解基准与 SAM 和原文基准总量核对。
5. 仅编辑仓库外的工作副本。新增冲击时定位实际生效的参数定义和情景赋值，修改目标参数或包含文件，不改报告变量。基准与情景保留独立副本，使用相同闭合及价格基准，记录地区、部门、年份和单位。如果使用 MPSGE，可参考[官方语法指南](https://www.gams.com/latest/docs/UG_MPSGE_Intro.html)理解 `$SECTORS`、`$COMMODITIES`、`$CONSUMERS`、`$PROD` 和 `$DEMAND`。修改结构方程后须重新校准和检查基准。
6. 重新运行并检查列表文件、数值残差，对比成对情景的价格、产量、收入与环境输出。求解状态成功而基准不符，仍不能称为复现。结果、日志和私人数据留在 Git 仓库外。

在此前审阅的 CHEER-P 演示包中，`sets.gms` 定义索引，`cal.gms` 处理校准，`elasticities.gms` 保存假设弹性，`emission.gms` 涉及环境变量，`core.gms` 包含均衡逻辑，`run.gms` 组织运行。这些文件名只是**查找起点**：编辑前必须追踪下载版本中实际启用的包含关系。扩展部门时，要同时调整集合、SAM 映射、参数维度和受影响方程；做参数情景时，要先复现基准，再修改生效的赋值；做环境卫星账户时，要确认变量进入均衡方程还是只进入报告。

先前检查的 CHEER 压缩包中有部分包含路径大小写不一致。这是特定版本的预检发现，不能泛化为所有版本，也不意味着可自动修改源码。
