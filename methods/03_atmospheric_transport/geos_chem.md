# GEOS-Chem：从排放接口到浓度

**步骤**：03 大气输送与化学。**状态**：参考说明，未注册编译、下载、模拟或调度适配器；没有可执行 tool_id。

## 使用顺序

1. 选择 Classic/GCHP 与源码版本，固定模拟、网格和比较设计。
2. 明确排放、气象、初始/边界及诊断的接口需求；只列方法，不提供排放清单具体数据和实现。
3. 核对工具链、依赖、独立运行目录和配置；根据所选版本构建，在任务环境验证，不能直接运行历史笔记命令。
4. 明确模型 dry-run、日志与后续下载的副作用；不等同于 run-tool 无执行预检。
5. 在后续授权任务中做短时验证，再检查终点、restart、诊断及浓度口径；浓度校正只能消费既有结果。
6. 向 04 交接时间平均、单位、网格、地表定义、有效范围及验证摘要。

对应[GEOS-Chem skill](../../skills/model/03_atmospheric_transport/geos-chem/SKILL.md)和[输入准备 skill](../../skills/data_acquisition/03_atmospheric_transport/atmospheric-inputs/SKILL.md)。编译/链接、资源、restart 和版本陷阱统一维护在 skill 的引用中，不重复复制命令。

本地笔记与官方资料已做文档核对；未读取数据、重现编译问题或运行模型。来源见该 skill 的 SOURCES.md。

## 阶段与 Skill 映射

主目录：03_atmospheric_transport；适用阶段：03_atmospheric_transport。对应 [atmospheric-inputs](../../skills/data_acquisition/03_atmospheric_transport/atmospheric-inputs/SKILL.md)、[geos-chem](../../skills/model/03_atmospheric_transport/geos-chem/SKILL.md)。执行状态以本文及真实工具 manifest 为准；没有 tool_id 的方法只供指导。
