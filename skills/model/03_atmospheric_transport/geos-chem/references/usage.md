# GEOS-Chem 使用流程与实用注意事项

本指南是人工准备清单，没有自动执行器。方法维护只用说明与合成接口；真实模型输入、下载、编译和计算属于另行明确的任务。

## 版本与运行目录

先固定 Classic 或 GCHP、源码/子模块版本和编译器。Classic 使用单节点 OpenMP；多节点任务应选择并核对 GCHP 的 MPI 环境，不能仅提高 Classic 的节点数。[官方快速开始](https://geos-chem.readthedocs.io/en/stable/getting-started/quick-start.html)给出两种入口的区别。

源码、build、运行目录、输入缓存和个人认证分开管理。使用所选版本的运行目录生成器；交互步骤可能涉及个人登记、个人配置文件写入，不能默认让 agent 提交个人信息。运行目录中 CodeDir 等模型内部链接是上游约定，不表示 run-tool 接受这些链接路径。

## 环境、构建与配置

核对 Fortran/C/C++、CMake、NetCDF C/Fortran 及所选并行库，先确认它们来自相容工具链。用新 build 目录配置，构建后安装到任务运行目录，记录实际二进制和源码对应关系。切换编译器或重大版本时不要沿用旧缓存。

下列是 Linux Classic 的人工编译示意，前提是已按该版本生成独立运行目录、确认 CodeDir 和依赖、授权构建；本轮没有执行。变量由使用者本地设置，并行数按实际资源确定，不提供自动安装或提交作业脚本。

```bash
: "${GC_RUN_DIR:?Set the task run directory locally}"
: "${GC_BUILD_JOBS:?Set the authorized build parallelism}"
cd "${GC_RUN_DIR}/build"
cmake ../CodeDir -DRUNDIR=..
cmake --build . --parallel "${GC_BUILD_JOBS}"
cmake --install .
```

Classic 的主要配置职责：geoschem_config.yml 管理模拟，HEMCO_Config.rc 管理输入读取/缩放关系，HEMCO_Diagn.rc 与 HISTORY.rc 管理诊断。旧笔记中的 input.geos、旧可执行名或云镜像目录不能直接复制到新版任务。

GCHP 应先检查该版本的 setCommonRunSettings.sh 与派生配置关系。HEMCO_Config.rc 中的缩放/物种关系不等同于 ExtData 输入读取规则；修改一处后需核对相关配置的一致性。下一代 ExtData 格式也有版本及模拟类型限制，见[官方 GCHP 配置说明](https://gchp.readthedocs.io/en/14.8.0/user-guide/configuration-files.html)。

## 输入检查、dry-run 与下载

先列所需气象、初始/边界和诊断类别，检查时间、网格、物种及单位契约。嵌套域还需匹配域外边界覆盖。此处不提供排放清单具体数据或代码。

GEOS-Chem 自身 dry-run **会启动模型并可写日志**，与 AirMosaic 的 run-tool dry-run 不同。只有实际模型任务获授权后才使用。根据日志列出所需文件，再独立决定下载范围；下载会联网并写输入缓存。旧笔记中的下载参数已随版本变化，使用对应版本帮助及[官方 dry-run 下载指南](https://geos-chem.readthedocs.io/en/stable/gcclassic-user-guide/dry-run-download.html)，不直接照搬历史云命令。

## Restart、spin-up 与产物

restart 的时间、网格、物种和精度读取规则要与本次模拟匹配；宽松的缺物种/日期读取模式仅能在明确初始化方案中选择，不能用来掩盖正式输入缺失。spin-up 时长依物种、区域和初始化收敛检查确定，不把笔记中某个固定时长当通用标准。

同网格精度延续与跨网格初始化有不同要求：原生精度读取、HEMCO 重网格和裁剪的能力不能无条件同时使用。参考[官方 restart 说明](https://geos-chem.readthedocs.io/en/stable/gcclassic-user-guide/restart-files-gc.html)作选择，另行验证 GCHP 的重网格流程。

完成状态应同时核对退出码、预期终点、浓度/诊断和 restart。日志有结束标记不保证时空覆盖与研究口径正确。浓度校正只处理已有模拟结果；敏感性、情景差值、伴随与因果效应分别解释，不从某个 forward 可执行文件推断具备伴随能力。
