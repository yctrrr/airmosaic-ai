# 公开 v35l：化学正向、伴随与梯度入门

[English](adjoint.md) | **中文**

本教程复现已核对的三小时**化学分量**案例：**2026-10-26 03—06 UTC**、全球纬向 4°×经向 5°、47 层、43 示踪物。控制量为地表初始 NOx 缩放，响应为结束时地表 Ox 质量。使用公开 v35l 分支，尚非经认证的官方 v36；程序、输入与 Classic 分开保存。

## 1. 准备软件并获取源码

需要 Linux/POSIX、Python ≥3.10、Git、make、Intel `ifort`、匹配的 NetCDF-C/Fortran，以及 NumPy、netCDF4。实测环境为 Intel oneAPI 2023、NetCDF 4.9.2。在已授权计算资源内加载本站相容环境；以下命令不自动提交作业或安装依赖。

```bash
set -euo pipefail
: "${AIRMOSAIC_REPO:?set the AirMosaic source checkout}"
: "${GC_ROOT:?set an existing project directory outside Git}"
GC_SKILL="$AIRMOSAIC_REPO/skills/model/03_atmospheric_transport/geos-chem"
mkdir -p "$GC_ROOT/source" "$GC_ROOT/inputs/ExtData" "$GC_ROOT/results"
```

```bash
GC_ADJOINT_VERSION="v35l"
GC_SOURCE="$GC_ROOT/source/adjoint-$GC_ADJOINT_VERSION"
GC_CASE="$GC_ROOT/results/adjoint_$GC_ADJOINT_VERSION"
git -c core.autocrlf=false clone https://github.com/stevezhang1990/GEOS-Chem-adjoint-v35.git "$GC_SOURCE"
mkdir "$GC_CASE"
python "$GC_SKILL/scripts/prepare_v35l.py" --root "$GC_ROOT" \
  --source "$GC_SOURCE" --version "$GC_ADJOINT_VERSION" --output "$GC_CASE/build"
python "$GC_SKILL/scripts/prepare_v35l.py" --root "$GC_ROOT" \
  --source "$GC_SOURCE" --version "$GC_ADJOINT_VERSION" --output "$GC_CASE/build" --execute
```

准备脚本按模型编号记录所选版本，在新副本检查补丁上下文后应用[分量配置补丁](../templates/adjoint_v35l/chemistry-component.patch)。它选择 GEOS-FP、移除未选观测依赖，并在正向和伴随两端对应排除地表交换与沙尘沉降；只分配零地表损失率，不伪造地表资料。未替换化学方程，也未启用完整过程模型。保存 `profile-receipt.json`。

后续版本按模型编号选择对应发布包或分支，并更新配套配置。脚本不要求旧提交或历史源码文件哈希一致；实际源码标识和修改前后哈希自动记录在本次准备记录中。附带补丁与依赖表以 v35l 为实测基础，遇到补丁冲突或新接口时需适配后重新编译、检查输入和验证导数。补丁可应用仅表示源码准备通过。

## 2. 编译准备好的副本

```bash
command -v ifort
nf-config --version
nc-config --version
cd "$GC_CASE/build"
make -f Makefile -f airmosaic_module_dependencies.mk -j1 geos \
  HDF=no SAT_NETCDF=no LIDORT=no USE_MKL=no \
  "GC_BIN=$(dirname "$(command -v nf-config)")" \
  "GC_INCLUDE=$(nf-config --includedir)" "GC_LIB=$(nf-config --prefix)/lib" \
  'FFLAGS=-mcmodel=large -cpp -w -O2 -auto -noalign -convert big_endian -fp-model precise -qopenmp -Dmultitask -DAIRMOSAIC_CHEM_COMPONENT' \
  > build.log 2>&1
test -s geos
sha256sum geos > binary.sha256
```

`-j1` 配合依赖文件避免旧代码的模块编译顺序竞争；`-qopenmp` 是该 Intel 环境支持的 OpenMP 参数，`-convert big_endian` 对应 BPCH 输入格式，`-mcmodel=large` 适配大型旧数组。`HDF=no`、`SAT_NETCDF=no`、`LIDORT=no`、`USE_MKL=no` 排除未选依赖。`AIRMOSAIC_CHEM_COMPONENT` 定义本试验的过程边界，必须保留；这些参数不能让任意分支相容。核对 make 退出码与非空程序文件，不能只凭一个可能遗留的文件判断成功。

## 3. 安排物理输入

| 输入 | 含义及 `data_root` 下的原生位置 |
|---|---|
| GEOS-FP 常量 | `GEOS_FP/2011/01/GEOSFP.20110101.CN.4x5.nc`，含陆海比例及网格常量；目录年份属于常量产品 |
| 混合层参数 | `GEOS_FP/2011/01/GEOSFP.ApBp.nc`，压力坐标支持 |
| GEOS-FP 逐日文件 | `GEOS_FP/2026/10/GEOSFP.20261026.{A1,A3cld,A3dyn,A3mstC,A3mstE,I3}.4x5.nc`，分别含小时/三小时平均与瞬时场 |
| 紫外反照率 | `uvalbedo_200111/uvalbedo.geos.4x5`，由官方兼容 NetCDF 转换的气候态反射率 |
| TOMS 臭氧 | `TOMS_201203/TOMS_O3col_2010.geos.4x5`，从官方 1×1 BPCH 按球面面积守恒重映射，共 36 块 |
| 初始场 | 已校验的旧 43 示踪物重启；本示例只改时间元数据，并明确标记为人工工作点 |
| 化学表 | 从所选模型源码的 `runs/v8-02-01/geos5/` 复制 11 个文件：`chemga.dat`、`diaginfo.dat`、`globchem.dat`、`jv_atms.dat`、`jv_spec_aod.dat`、`jv_spec.dat`、`mglob.dat`、`ratj.d`、`RXN_ID`、`STR_ID`、`tracerinfo.dat` |

常量、I3 两端和区间平均都需要。本案例 03—04 UTC 不能满足原生 I3 接口，采用完整的 03—06 时段。重命名气象文件不能改变内部时刻或字段。

下面的清单把官方对象映射到原生目录，复用已有文件，只获取缺失项。已有文件仍需核对产品、时间及内容。共用传输台账累计上限为 2 GiB，失败保留预留额度和部分文件；遇到额度阻断要复核台账，不应清零重试。HTTPS 始终保持证书校验。

```bash
GC_DATA="$GC_ROOT/inputs/v35l"
mkdir -p "$GC_DATA"
export GC_ROOT GC_DATA GC_CASE
python - <<'PY'
import json, os
from pathlib import Path
root=Path(os.environ['GC_ROOT']).resolve(); data=Path(os.environ['GC_DATA']).resolve()
case=Path(os.environ['GC_CASE']).resolve(); data.relative_to(root); case.relative_to(root)
mapping=[('GEOS_4x5/GEOS_FP/2011/01/'+n, 'GEOS_FP/2011/01/'+n) for n in
         ('GEOSFP.20110101.CN.4x5.nc','GEOSFP.ApBp.nc')]
mapping += [('GEOS_4x5/GEOS_FP/2026/10/GEOSFP.20261026.'+v+'.4x5.nc',
             'GEOS_FP/2026/10/GEOSFP.20261026.'+v+'.4x5.nc')
            for v in ('A1','A3cld','A3dyn','A3mstC','A3mstE','I3')]
mapping += [('HEMCO/UVALBEDO/v2019-06/uvalbedo.geos.4x5.nc','raw/uvalbedo.geos.4x5.nc'),
            ('CHEM_INPUTS/TOMS_201203/TOMS_O3col_2010.geos.1x1','raw/TOMS_O3col_2010.geos.1x1')]
items=[{'key':key,'target':(data/target).relative_to(root).as_posix()}
       for key,target in mapping if not (data/target).exists()]
with (case/'input-inventory.json').open('x') as f:
    json.dump({'schema':1,'portal':'https://geos-chem.s3-us-west-2.amazonaws.com/',
               'files':items,'measured':False},f,indent=2)
print('Missing files:',len(items))
PY
# Run these only when the inventory has missing files; inspect measured sizes first.
python "$GC_SKILL/scripts/bounded_inputs.py" measure --root "$GC_ROOT" \
  --manifest "$GC_CASE/input-inventory.json" --output "$GC_CASE/input-measured.json"
python "$GC_SKILL/scripts/bounded_inputs.py" fetch --root "$GC_ROOT" \
  --manifest "$GC_CASE/input-measured.json" --ledger "$GC_ROOT/input-transfer-ledger.json" \
  --max-bytes 2147483648 --execute
```

原始初态来自 [Zenodo 7517355](https://zenodo.org/records/7517355) 的 `gcadj_std.zip`，成员为 `gcadj_std/runs/v8-02-01/geosfp/restart.geos5.2005070100`。归档大小 1,348,591,027 字节；优先复用已核验本地成员。转换脚本自动核对示范所用重启成员的完整性。下载/解包属于单独的明确获取步骤，上面的官方桶脚本不获取 Zenodo。成功试验通过 HTTP Range 提取并校验成员，避免下载整个归档。

```bash
: "${GC_LEGACY_RESTART:?set the verified original restart inside GC_ROOT}"
python "$GC_SKILL/scripts/prepare_v35l_inputs.py" --root "$GC_ROOT" \
  --uv-netcdf "$GC_DATA/raw/uvalbedo.geos.4x5.nc" \
  --toms-bpch "$GC_DATA/raw/TOMS_O3col_2010.geos.1x1" \
  --legacy-restart "$GC_LEGACY_RESTART" \
  --cn-netcdf "$GC_DATA/GEOS_FP/2011/01/GEOSFP.20110101.CN.4x5.nc" \
  --start-utc 2026-10-26T03:00:00Z --output "$GC_DATA/derived"
mkdir "$GC_DATA/uvalbedo_200111" "$GC_DATA/TOMS_201203"
cp "$GC_DATA/derived/uvalbedo_200111/uvalbedo.geos.4x5" "$GC_DATA/uvalbedo_200111/"
cp "$GC_DATA/derived/TOMS_201203/TOMS_O3col_2010.geos.4x5" "$GC_DATA/TOMS_201203/"
cp "$GC_SKILL/templates/adjoint_v35l/settings.json" "$GC_CASE/settings.json"
```

转换脚本重开输出，检查数值相等或守恒。紫外反照率数值约为 0.01—0.95，旧 `percent` 标签**不构成除以 100 的依据**。原生 TOMS 代码将 2010 年之后的年份固定到 2010。派生重启只改 BPCH 时间元数据，保留所有示踪物原值，不能当作现代大气分析场或预热结果。旧 BPCH 未嵌入物种名称；43 示踪物对应关系由归档说明与分支表支持，尚无嵌入物种元数据的独立确认。

## 4. 配置新试验

编辑复制出的 `settings.json`：`data_root` 为 `GC_DATA` 的绝对路径，`restart_file` 为 `GC_DATA/derived/initial.artificial.2026102603.bpch` 对应的绝对路径。首次运行保留示范时段、控制 1、响应 2 和扰动 `[0.1,0.03,0.01]`。路径应短且不含空格。模板保留原生固定列格式，不要重新排版标签或删除未启用菜单行。

```bash
python "$GC_SKILL/scripts/configure_run.py" --mode adjoint --root "$GC_ROOT" \
  --source "$GC_SOURCE" --run "$GC_CASE/prepared" --settings "$GC_CASE/settings.json"
python "$GC_SKILL/scripts/configure_run.py" --mode adjoint --root "$GC_ROOT" \
  --source "$GC_SOURCE" --run "$GC_CASE/prepared" --settings "$GC_CASE/settings.json" --execute
```

| 设置/原生参数 | 含义及示范选择 |
|---|---|
| `start_utc`、`end_utc` | UTC 时段；脚本要求同一天、从三小时边界起算的三小时 I3 区间 |
| `data_root`、`restart_file` | 原生气象/辅助根目录与相容的 43 示踪物初态；生成配置不等于校验输入内容 |
| `control_tracer` / `ICSFD` | 扰动初态的示踪物编号，`1=NOx`，同时更新 LICS 控制表 |
| `response_tracer` / `NFD` | 保存的结束响应编号，`2=Ox`，同时更新观测/目标表 |
| `fd_steps` / `FD_DIFF` | 三个互异、递减的缩放加性扰动，无量纲，不是排放百分比 |
| `input.geos:Type of simulation`、`Number of Tracers` | `3`、`43`；NOx/Ox 是含多个化学物种的家族，复现时保留成员定义 |
| 输送/云对流/PBL/排放/沉降开关 | 本分量均为 `F`；开启任一项需要重新审定模型配置与匹配输入 |
| Online aerosol 开关 | 启用硫酸盐/碳质/沙尘/海盐化学状态，不表示启用了排放或沉降 |
| 化学步长 | 原生配置为 60 分钟，三小时有三次化学调用 |
| 重启名称/月输出安排 | `restart.output.component.YYYYMMDDhh`；仅结束日设为 `3`；原生固定格式分别读取 31/29/30 位日安排 |
| `LADJ`、`LSENS`、`L4DVAR`、`L3DVAR` | `T,T,F,F`，执行敏感性试验，未进行反演/同化优化 |
| `FD_GLOB`、`FD_SPOT` | `T,F`，扰动 `LFD=1` 层所有水平格点；IFD/JFD 不会缩小到单一受体 |
| `LICS`、`LADJ_EMS` | `T,F`，控制初始浓度缩放；未启用的排放表不构成排放试验 |
| `NSOPT`、LICS 的 `Tracer #1` | 一个控制示踪物，`SF_DEFAULT=1`，相对于输入初态缩放 |
| `REG_PARAM`、`ERROR`、`APSRC` | 先验设置；本示例 `APSRC=F`，不计先验目标项 |
| `NOBS`、目标表 `Tracer #1` | 一个响应示踪物 Ox；`tracer kg/box=T`，其他目标单位为 `F` |
| `LFD`、`IFD/JFD` | 地表第 1 层；`FD_GLOB` 下水平点测试索引不生效 |
| 区域掩膜/观测数量限制 | `F`；未启用的掩膜文件名是占位符，不是必需输入 |
| `OBS_FREQ`、forcing-time 行 | 原生观测时序参数，此处为 60 分钟及开始时刻；导数比较以 FD 驱动实际保存的结束场为准 |
| `LADJ_CHEM`、`LAERO_THEM`、ISORROPIAII | `T,T,F`，复现时保持这套化学/热力学选择 |
| `LDEL_CHKPT`、`LITR`、`LPRINTFD`、`LADJ_TRAJ` | `F,T,F,F`，保留检查点及迭代诊断，关闭额外调试/轨迹打印 |
| `ITER` | 两个整数分占两行：当前调用编号与最大调用数 `3` |
| `OptData/`、`adjtmp/`、`diagadj/`、`TMP/` | 目标/梯度数据、伴随检查点、诊断状态与临时工作文件 |

[完整模板](../templates/adjoint_v35l/input.gcadj.in)保留原生解析器所需的未启用选项，这些选项并非额外的成功配方。`configuration-receipt.json` 记录设置与文件哈希。之后若手动编辑原生文件，应重新准备配置并复核记录，运行器会拒绝被改动的已准备文件。

## 5. 执行基线、正扰动和负扰动

每个步长需要**分三次调用程序**：基线正向+伴随、正扰动、负扰动，并继承上一次的检查点。每次将 `ITER` 恢复为 `1\n3\n`、`2\n3\n`、`3\n3\n`；原生退出会将其改成一行。单次调用不是整个试验。辅助脚本在新目录逐次执行、拒绝复用已有输出，只在新副本移除继承的重启输出，避免其误通过下一次检查。

```bash
export OMP_NUM_THREADS=4 OMP_STACKSIZE=256M OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -s unlimited
python "$GC_SKILL/scripts/run_v35l.py" --root "$GC_ROOT" \
  --binary "$GC_CASE/build/geos" --prepared "$GC_CASE/prepared" --output "$GC_CASE/native"
python "$GC_SKILL/scripts/run_v35l.py" --root "$GC_ROOT" \
  --binary "$GC_CASE/build/geos" --prepared "$GC_CASE/prepared" --output "$GC_CASE/native" --execute
python "$GC_SKILL/scripts/check_v35l_gradients.py" --root "$GC_ROOT" \
  --runs "$GC_CASE/native" --control-tracer 1 --rtol 0.05 --output "$GC_CASE/gradient-check.json"
```

模型最多 4 线程、申请 24 GiB 内存，脚本按项目 10 GiB 上限保留至少 1 GiB 空间。成功案例峰值约 4.66 GiB，最后九次调用累计约 320 秒。`OMP_STACKSIZE` 设置工作线程栈，不能替代主线程的 `ulimit -s unlimited`。每次调用上限 1,800 秒，本次脚本调用总上限 10,800 秒；重试须先核对已有记录及项目累计预算，不能删除旧输出后直接重启。

## 6. 读取与检查结果

| 输出 | 含义与检查 |
|---|---|
| `run-status.json` | 九次终止调用；同时要求退出零、原生完成标记、本次目标文件和新写出的结束重启 |
| `step_*/iteration_3/diagadj/gctm.fd.*.01/.02/.03` | 基线/正/负扰动结束状态，BPCH `IJ-CHK-$`、`kg/box`、72×46×47，比较地表层 |
| `step_*/iteration_3/OptData/gctm.gdt.01` | 基线伴随，`IJ-GDT-$`，按控制示踪物提取地表层 |
| `OptData/cfn.01/.02/.03` | 原生目标记录，可辅助检查，不能替代状态场和导数检查 |
| `restart.output.component.2026102606` | 结束状态；另行核对时间、43 示踪物编号、维度、单位、有限值 |
| `gradient-check.json` | 中心差分与基线伴随比较，共同格点、非零有限范数及局地异常数量 |

h=0.1、0.03、0.01 的全域相对 L2 误差为 **1.4639%、2.6269%、6.2708%**，达到预设“相邻两档≤5%”条件。最小步长失败；在 3,312 个地表格点中，829/830/895 个满足 |FD|>1 且局地相对误差>5%。不能称全部格点、任意控制量或完整伴随均通过验证。原生 aerosol-feedback-adjoint 提示仍未解决。

## 7. 改变一个因素并重新检查

| 目标 | 修改 | 必须重新检查 |
|---|---|---|
| 更换初始物种 | `control_tracer`，如 `4=CO` | 初态元数据、缩放及新导数检查；默认 NOx 结论不自动继承 |
| 更换响应 | `response_tracer`，如 `26=SO2` | 目标表与 NFD 一致、质量单位和非零导数；兼容 CSV 列仍保留历史 `*_Ox_kg` 名称 |
| 更换日期 | 两个 UTC 设置及相容气象/初态 | 完整 I3 区间、平均场、辐射气候态假设及结束时间；转换初态仍标记为人工工作点 |
| 更换扰动 | 三个递减 `fd_steps` | 看结果前固定步长和阈值，检查截断/消减误差，不能调到通过为止 |
| 更换统计量或区域 | 在另一个准备案例中改原生目标与掩膜 | 目标权重、单位、解析语义和检查器都需适配，不能只改 IFD/JFD |
| 排放响应、输送或完整反演 | 设计新的过程/模型/输入方案 | 超出此分量配置，不能简单将排除开关改为 T |

导数、扰动含义与科学验收见[方法说明](../../../../../methods/03_atmospheric_transport/geos_chem_ZH.md)。保留最新成功案例及所需输入，未启用历史集中整理并提供核验后的恢复索引，不把每次失败写进主教程。
