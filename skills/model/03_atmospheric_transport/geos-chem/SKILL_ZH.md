---
name: geos-chem-workflow
description: 编译、配置并核对已测试的 Classic 14.8.0 输送和公开 v35l 化学分量伴随路线，提供原生模板与参数说明。
compatibility: "POSIX; Python>=3.10; Git; CMake>=3.13; Intel Fortran; NetCDF-C/Fortran; NumPy and netCDF4 for v35l conversions."
metadata:
  version: "0.3.1"
---

# GEOS-Chem：选择一条已成功运行的路线

[English](SKILL.md) | **中文**

**阶段：**03，大气输送与化学。科学解释先读[方法说明](../../../../methods/03_atmospheric_transport/geos_chem_ZH.md)。

| 你想做什么 | 从哪里开始 | 已测试配置 |
|---|---|---|
| 编译正向模型，得到浓度与重启文件 | [Classic 入门手册](references/usage_ZH.md) | Classic 14.8.0、TransportTracers、MERRA-2、全球 4×5、47 层、一小时 |
| 运行化学正向、伴随并检查导数 | [Adjoint 入门手册](references/adjoint_ZH.md) | 公开 v35l 分支、GEOS-FP、化学分量、三小时、初始 NOx 缩放 → 表面 Ox 质量 |

选择一条路线，按“源码 → 编译 → 输入配置 → 执行 → 输出检查”操作。两本手册都提供原生模板、参数含义、修改输入的示例及预期输出。[来源与实测范围](SOURCES_ZH.md)记录版本和公开 skill 参考，[排错表](references/build-troubleshooting_ZH.md)用于定位常见问题。

## 本 skill 提供的文件

- `templates/classic_14.8.0/`：完整的 `geoschem_config.yml`、HEMCO、HISTORY 模板及 `settings.json`。
- `templates/adjoint_v35l/`：完整的 `input.geos`、`input.gcadj`、`ITER`、配置 JSON、带哈希核对的化学分量补丁和模块依赖表。
- [configure_run.py](scripts/configure_run.py)：在新的外部目录生成两套配置，默认只预览。
- [build_classic.py](scripts/build_classic.py)、[prepare_v35l.py](scripts/prepare_v35l.py)：Classic 编译预览/执行，以及 v35l 源码配置副本准备。
- [bounded_inputs.py](scripts/bounded_inputs.py)、[prepare_v35l_inputs.py](scripts/prepare_v35l_inputs.py)：Classic 限额获取输入，以及本次测试使用的 v35l 输入格式转换。
- [run_v35l.py](scripts/run_v35l.py)、[check_outputs.py](scripts/check_outputs.py)、[check_v35l_gradients.py](scripts/check_v35l_gradients.py)：有时限的原生伴随试验、固定 Classic 输出检查、独立全域梯度检查。
- [prepare_classic.py](scripts/prepare_classic.py)：通过所选 Classic 源码自带的运行目录模板准备配置的替代入口。
- [gc_paths.py](scripts/gc_paths.py)、[v35l_bpch.py](scripts/v35l_bpch.py)：辅助脚本共用的路径/记录及原生 BPCH 工具。

脚本均在 `scripts/`。它们是直接辅助脚本，尚未注册 run-tool/MCP 模型执行器或调度器适配器。生成模板不会下载或验证物理数据。新整理的辅助脚本经过合成检查和已有输出回归核对；原模型试验验证的是特定配置的运行链，不等于每个新辅助脚本均已重新完成模型积分。

## 操作边界

源码、输入、新运行与检查放在 Git 外部。使用明确的编译器/库环境和已授权计算资源；凭据、站点路径与原始日志保留在私人目录。保留成功输入与结果，停用历史可合并为带核验及恢复索引的归档。

按模型编号选择源码并配套配置和输入。升级时复核接口与输出，明确化学/过程选择及目标与控制量定义。修改参数会形成新试验，需要重新检查输入、输出和导数。v35l 补丁定义的是化学分量，不支持据此直接开启完整大气输送、排放或反演。两档较大扰动达到预设全域容差，最小步长和许多局地格点未达到；技术运行与科学验收分别判断。
