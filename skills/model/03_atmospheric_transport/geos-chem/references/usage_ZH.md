# Classic 14.8.0：完成第一次可核对的正向运行

[English](usage.md) | **中文**

本教程复现成功的 **TransportTracers/MERRA-2/全球 4×5/47 层**配置，时段为 **2019-01-01 00:00—01:00 UTC**，输出 21 个浓度字段和 21 个重启字段。这里的化学开关执行输送示踪配置本身的过程，尚未用于完整污染化学评估。

## 1. 准备目录与软件

使用 Linux/POSIX、Git、Python 3.10+、CMake ≥3.13、相容的 Fortran/C/C++ 编译器，以及匹配的 NetCDF-C/NetCDF-Fortran。成功构建使用 Intel Fortran 和 NetCDF。按实际环境设置 `FC`、`CC`、`CXX`、`GC_CMAKE`、`GC_NETCDF_PREFIX`；运行时使用同一套库。无关 conda 环境中的库可能干扰 Intel/NetCDF 链接。

```bash
set -euo pipefail
: "${AIRMOSAIC_REPO:?set the AirMosaic source checkout}"
: "${GC_ROOT:?set an existing project directory outside Git}"
GC_SKILL="$AIRMOSAIC_REPO/skills/model/03_atmospheric_transport/geos-chem"
mkdir -p "$GC_ROOT/source" "$GC_ROOT/inputs/ExtData" "$GC_ROOT/results"
```

路径尽量短且不含空格。`GC_ROOT` 存放数据与输出，`AIRMOSAIC_REPO` 是本 skill 所在的源码仓库。模型需在已授权计算资源中执行；示例最多使用 4 线程、24 GiB 申请和共享节点。以下命令不会自动提交调度作业。

## 2. 按模型版本获取源码

```bash
GC_VERSION="14.8.0"
GC_SOURCE="$GC_ROOT/source/GCClassic-$GC_VERSION"
GC_CASE="$GC_ROOT/results/classic_$GC_VERSION"
git clone --branch "$GC_VERSION" --recurse-submodules \
  https://github.com/geoschem/GCClassic.git "$GC_SOURCE"
git -C "$GC_SOURCE" describe --tags --always
git -C "$GC_SOURCE" submodule status --recursive
mkdir "$GC_CASE"
cp "$GC_SKILL/templates/classic_14.8.0/settings.json" "$GC_CASE/settings.json"
```

按模型编号选择对应的发布标签，此处为 **Classic 14.8.0**，无需填写或匹配指定 Git 提交哈希。脚本核对源码声明的模型版本，自动记录实际源码标识。子模块状态不能带 `-`、`+`、`U` 前缀。该版本的 `GEOS-Chem`、`HEMCO`、`Cloud-J`、`HETP` 都是 `src/` 的直接子目录。辅助脚本保留实测的 `MECH=fullchem` 编译选项，运行时仍选择 `TransportTracers`。

更新模型时，将 `GC_VERSION` 改为目标发布版本，并使用该版本的配置与数据说明。这里的完整模板与固定输出检查器以 14.8.0 案例为基准；升级后检查配置接口、编译选项、输入兼容性与输出，原试验结论不会自动继承。

## 3. 编译一次

```bash
: "${FC:?}" "${CC:?}" "${CXX:?}" "${GC_CMAKE:?}" "${GC_NETCDF_PREFIX:?}"
python "$GC_SKILL/scripts/build_classic.py" \
  --root "$GC_ROOT" --source "$GC_SOURCE" --build "$GC_CASE/build" \
  --version "$GC_VERSION" \
  --fc "$FC" --cc "$CC" --cxx "$CXX" --cmake "$GC_CMAKE" \
  --netcdf-prefix "$GC_NETCDF_PREFIX" --jobs 4 --max-seconds 3600
# Execute the same plan inside the authorized allocation:
python "$GC_SKILL/scripts/build_classic.py" \
  --root "$GC_ROOT" --source "$GC_SOURCE" --build "$GC_CASE/build" \
  --version "$GC_VERSION" \
  --fc "$FC" --cc "$CC" --cxx "$CXX" --cmake "$GC_CMAKE" \
  --netcdf-prefix "$GC_NETCDF_PREFIX" --jobs 4 --max-seconds 3600 --execute
```

成功后得到 `build/bin/gcclassic`。脚本核对源码内容，在新目录编译，保存编译/链接日志和程序哈希。`--jobs` 是编译并行数，不是科学参数。合并的 NetCDF 安装目录应有 `include/`、`lib/libnetcdf.so`、`lib/libnetcdff.so`；分开安装时需明确适配 CMake。参见[官方编译说明](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/compile-cmake.html)。

## 4. 配置输入文件

编辑复制出的 `settings.json`，把 `@DATA_ROOT@` 替换成 `GC_ROOT/inputs/ExtData` 对应的绝对路径。第一次运行保留示范时段。脚本从[完整原生模板](../templates/classic_14.8.0/settings.json)生成配置，并从对应源码复制物种库与下载器。

```bash
python "$GC_SKILL/scripts/configure_run.py" --mode classic \
  --root "$GC_ROOT" --source "$GC_SOURCE" --run "$GC_CASE/run" \
  --settings "$GC_CASE/settings.json"
python "$GC_SKILL/scripts/configure_run.py" --mode classic \
  --root "$GC_ROOT" --source "$GC_SOURCE" --run "$GC_CASE/run" \
  --settings "$GC_CASE/settings.json" --execute
cp "$GC_CASE/build/bin/gcclassic" "$GC_CASE/run/gcclassic"
cd "$GC_CASE/run"
./gcclassic --dryrun > log.dryrun 2>&1
```

| 文件/参数 | 含义与作用 |
|---|---|
| `settings.json:start_utc`、`end_utc` | UTC 模拟时段，写入 `simulation.start_date/end_date`；脚本支持整小时区间 |
| `settings.json:data_root` | 已存在的外部数据根目录，同时写入 YAML 与 HEMCO 路径 |
| `geoschem_config.yml:simulation.name` | 模拟类型，本教程保持 `TransportTracers` |
| `simulation.met_field` | `MERRA2`，必须与实际气象文件及 HEMCO 气象配置匹配 |
| `simulation.read_restart_as_real8` | `false` 使用实测的 HEMCO 读取/重映射路线，适用于这里的 47 层约化网格 |
| `grid.resolution`、`number_of_levels` | 纬向 4°×经向 5°、47 层；修改后需要匹配的气象、重启及新检查 |
| `grid.longitude/latitude` | 全球范围、日期变更线定位和半极区网格，定义实际坐标，不能当成事后裁剪 |
| `timesteps.transport_timestep_in_s` | 输送步长，示例为 600 秒 |
| `timesteps.chemistry_timestep_in_s` | 当前模拟类型的化学步长，示例为 1200 秒 |
| `operations.*.activate` | 化学、对流、沉降、边界层混合和输送开关；修改会改变物理试验 |
| `operations.transport.transported_species` | 21 个输送物种；重启与物种元数据必须对应 |
| `HEMCO_Config.rc:ROOT`、`METDIR`、`GC_RESTART` | 清单根目录、气象路径选择和初始重启来源，要检查整个启用区块 |
| HEMCO 数据行 | 依次给出名称、文件、变量、时间覆盖、循环规则、维度、单位、目标物种、缩放因子编号、类别和层级 |
| `HEMCO_Diagn.rc` | 排放诊断，不能用 `HISTORY.rc` 代替 |
| `HISTORY.rc:COLLECTIONS` | 启用的输出集合；只定义集合不会自动启用 |
| `SpeciesConc.frequency` | 输出/采样间隔，`00000000 010000` 表示一小时 |
| `SpeciesConc.duration` | 多久新建一个文件，与采样间隔不同 |
| `SpeciesConc.mode` | `time-averaged` 保存区间平均，`instantaneous` 保存采样时刻状态 |
| `SpeciesConc.fields` | 输出变量；`SpeciesConcVV_?ALL?` 表示全部物种的干空气混合比 |
| `Restart.frequency/duration` | `'End'` 在结束时写出可供续跑的状态 |
| `species_database.yml` | 物种标识、分子量与性质，保持源码匹配版本 |

原生空跑只列出所需输入，不生成浓度结果。五个生成的配置文件和 `species_database.yml` 应配套保存。

## 5. 准备物理文件

数据根目录需要预处理的 MERRA-2 气象、匹配的重启、常量以及空跑列出的启用源和辅助资料。成功案例需要 16 个文件、约 498 MB。已有匹配文件直接复用，只对缺失文件执行清单、测量与限额下载：

```bash
python "$GC_SKILL/scripts/bounded_inputs.py" inventory \
  --root "$GC_ROOT" --data "$GC_ROOT/inputs/ExtData" --run "$GC_CASE/run" \
  --log "$GC_CASE/run/log.dryrun" --manifest "$GC_CASE/input-inventory.json"
python "$GC_SKILL/scripts/bounded_inputs.py" measure \
  --root "$GC_ROOT" --manifest "$GC_CASE/input-inventory.json" \
  --output "$GC_CASE/input-measured.json"
python "$GC_SKILL/scripts/bounded_inputs.py" fetch \
  --root "$GC_ROOT" --manifest "$GC_CASE/input-measured.json" \
  --ledger "$GC_ROOT/input-transfer-ledger.json" --max-bytes 2147483648 --execute
```

下载前检查测量大小。脚本不会静默覆盖已有完整文件或未知/部分传输；失败预留保留在同一台账。更大研究需另行审定预算，并使用该版本的官方获取方式。[输入数据说明](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/download-data.html)。

## 6. 运行与检查

```bash
cd "$GC_CASE/run"
export OMP_NUM_THREADS=4 OMP_STACKSIZE=128M OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -s unlimited
set +e
timeout --signal=TERM --kill-after=10 1800 ./gcclassic > log.run 2>&1
model_exit=$?
set -e
printf '%s\n' "$model_exit" > model.exit
test "$model_exit" -eq 0
```

命令退出码应为零，日志应到达设定终点。检查 `OutputDir/GEOSChem.SpeciesConc.20190101_0000z.nc4` 和 `Restarts/GEOSChem.Restart.20190101_0100z.nc4`：前者为该小时浓度平均，后者为结束瞬时状态。

```bash
: "${GC_NETCDF_C_LIBRARY:?set the full path to the matching libnetcdf.so}"
python "$GC_SKILL/scripts/check_outputs.py" \
  --root "$GC_ROOT" --library "$GC_NETCDF_C_LIBRARY" \
  --concentration "$GC_CASE/run/OutputDir/GEOSChem.SpeciesConc.20190101_0000z.nc4" \
  --restart "$GC_CASE/run/Restarts/GEOSChem.Restart.20190101_0100z.nc4" \
  --history "$GC_CASE/run/HISTORY.rc" --unit 'mol mol-1 dry' \
  --output "$GC_CASE/output-check.json"
```

检查器特意限定为成功的 2019 一小时/47 层/21 物种案例，检查物种、坐标/混合层、维度、单位、平均方式、时段及数值有限性。修改日期、输出集合或物种后，应适配输出核验约定，不能直接沿用这一检查器宣称新案例通过。

## 7. 每次改变一个因素

| 想做的改变 | 修改位置 | 重新检查与预期输出 |
|---|---|---|
| 换小时或日期 | 复制 `settings.json`，修改两个 UTC 时刻，生成新运行目录 | 新初态和完整气象覆盖；重新空跑；输出文件名随时间改变 |
| 每半小时输出浓度 | 在新运行中把 `SpeciesConc.frequency` 改为 `00000000 003000`，duration ≥ frequency | 每小时两个样本；明确平均方式；固定检查器需适配 |
| 少输出一些变量 | 把 `SpeciesConc.fields` 改为已有输送物种，如 `SpeciesConcVV_CO_50` | 诊断文件变小，实际模拟物种不变 |
| 改排放 | 修改启用的 HEMCO 源或缩放项，保持单位与层级一致 | 先用 HEMCO 诊断确认通量按预期改变，再解释浓度 |
| 换初始场 | 修改 HEMCO 中启用的 `GC_RESTART` | 复核时间、网格、物种、单位及预热 |
| 换网格或过程类型 | 重新生成相容配置，必要时重新编译并准备数据 | 属于新试验，本教程的验收结论不自动继承 |

输出选择改变保存内容；输入和过程改变可能改变模型轨迹。辨识排放影响时，对比情景应保持气象、数值设置和有效空间/时间范围一致。另见[科学方法](../../../../../methods/03_atmospheric_transport/geos_chem_ZH.md)与[History 说明](https://geos-chem.readthedocs.io/en/14.8.0/geos-chem-shared-docs/supplemental-guides/history-diag-guide.html)。
