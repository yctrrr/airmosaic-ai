# 来源与核验范围

[English](SOURCES.md) | **中文**

核对日期为 2026-11-05。共享资产包含可复用说明/模板，不含私人运行记录。早期技术笔记来源见[来源快照](../../../../methods/source-snapshots.yaml)。

## 一手来源

| 来源 | 用途 |
|---|---|
| [Classic 14.8.0 发布](https://github.com/geoschem/GCClassic/releases/tag/14.8.0) | 发布版本与递归子模块 |
| [14.8.0 运行配置](https://geos-chem.readthedocs.io/en/14.8.0/geos-chem-shared-docs/doc/geoschem-config.html)、[CMake 编译](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/compile-cmake.html) | 原生文件、编译器/库设置；模板来自成功的 Classic 14.8.0 运行 |
| [空跑](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/dry-run-run.html)、[输入获取](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/download-data.html)、[History](https://geos-chem.readthedocs.io/en/14.8.0/geos-chem-shared-docs/supplemental-guides/history-diag-guide.html) | 必需文件清单、诊断、平均与时间含义 |
| [公开 v35l 源码](https://github.com/stevezhang1990/GEOS-Chem-adjoint-v35) | `code/Makefile`、`define.h`、`adjoint/define_adj.h`、`inverse_mod.f`、输入解析器及 `runs/v8-02-01/geos5` 完整表；正向/伴随配对配置 |
| [历史伴随手册](https://spot.colorado.edu/~henzed/GC_adj/GC_adj_man.pdf) | 菜单/控制背景，具体含义以本分支实际源码为准 |
| [官方公开输入桶](https://geos-chem.s3-us-west-2.amazonaws.com/)、[输入布局与对象键](references/adjoint_ZH.md) | GEOS-FP、向后兼容紫外反照率和 TOMS；原始/转换哈希留在试验记录 |
| [Zenodo 旧输入归档](https://zenodo.org/records/7517355) | 已校验 `gcadj_std.zip` 重启成员；仅证明输入来源，不构成将公开源码标为官方 v36 的依据 |

Classic 检查器采用 Classic 14.8.0 案例的 47 层 Ap/Bp、21 输送物种、干空气单位和 History 区间起点时间戳。单记录时段由开始/结束属性、平均元数据和匹配的一小时 HISTORY 配置核对，不假设必有 CF time-bounds 变量。

## 公开 skill 参考

已查阅 [earth-space-ai/geos-chem-skill](https://github.com/earth-space-ai/geos-chem-skill)，框架版本 `0.1.0`，借鉴任务导航及多文件配置清单。其自述为 `0.1.0-scaffold`，列出的八份详细 reference 在查阅时尚不存在，未复制或安装其文件。未采用其中 HEMCO/Cloud-J 嵌套路径说法：实测 Classic 14.8.0 的 GEOS-Chem、HEMCO、Cloud-J、HETP 均为 `src/` 直接子目录。操作依据仍为模型源码和实际成功配置。

## 已检查范围

| 检查 | 结果与边界 |
|---|---|
| Classic 模型 | Classic 14.8.0 及其配套子模块、Intel/NetCDF 编译、原生空跑、16 个物理输入（498,084,688 字节）、一小时 TransportTracers 运行退出零 |
| Classic 输出 | 浓度与重启各 21 字段，核对网格、混合层、维度、物种、单位、时间、平均方式和有限值 |
| v35l 原生模型 | 化学分量、GEOS-FP、2026-10-26 03—06 UTC、43 示踪物，最后九次调用退出零；程序标识保存在试验记录 |
| 独立梯度检查 | h=.1/.03/.01 的相对 L2 为 1.4639%/2.6269%/6.2708%，相邻两档达到预定 5% 条件；最小步长及大量局地格点失败 |
| 新源码准备脚本 | 原 v35l 配置重放的 11 个参考文件一致；现按模型编号和补丁适用性选择版本，自动记录实际源码标识 |
| 通用辅助脚本 | 合成配置/路径/源码、导数/格点、原生调用协议/失败、球面守恒及 BPCH 往返检查；保存的 3,312 格点×3 步长比较复现原独立指标 |
| 新运行器/转换器 | 合成检查和原成功实现经验，尚非每个通用 CLI 都重新执行了端到端物理运行 |
| 完整大气/反演 | 本试验未建立；人工旧初态、辐射气候态和缺失 aerosol-feedback adjoint 仍是限制 |
| 执行注册 | 直接脚本，无注册 run-tool/MCP 模拟、调度适配器或自动宿主安装 |

源码/配置核对、运行完成、数值检查与科学验收分别记录。完整私人证据及可恢复未启用历史保存在外部项目；科学验收需要人工审阅。
