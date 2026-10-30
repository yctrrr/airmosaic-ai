# 准备、编译与运行 GCAM

[English](build-and-run.md) | **中文**

本说明适用于任务选定的模型版本和环境，提供人工操作流程，不是 AirMosaic 编译或模拟适配器。[方法说明](../../../../../methods/04_integrated_impacts/gcam_ZH.md)解释实验设计与验收，[输出操作](operations_ZH.md)说明已经实现的分析工具。

## 1. 选择必要的路径

| 需求 | 路径 | 继续前核对 |
|---|---|---|
| 运行未修改且兼容的模型 | 使用对应平台发行包 | 可执行文件、支持库与输入 XML 属于同一发行版 |
| 修改 C++ 行为或面向其他平台 | 编译选定源码版本 | 编译器、依赖版本、子模块、构建选项和架构 |
| 修改数据系统的输入或处理 | 重建匹配的 gcamdata 输出 | R 包与接口、依赖锁定、受影响模块及 XML 兼容性 |
| 查询已有结果 | 使用输出分析工具 | 数据库已完成写入，情景与布局、Java/BaseX 及单位适用 |

修改情景 XML 通常不需要重编译 C++；使用发行包自带 XML 不需要重跑 gcamdata。源码压缩包不一定是完整运行包。GCAM-China 与 GCAM-Core 的二进制、输入及配置名不能互换。[官方用户指南](https://jgcri.github.io/gcam-doc/user-guide.html)区分了发行包使用、源码编译和输入生成。

## 2. 选择位置并固定版本

在任务记录中写明模型变体、发行版或源码提交、平台、所选配置、输入版本、要求的模拟时期及预期产物。基准与干预分别命名保留，不用最新主分支替代研究锁定的源码。

| 变量 | 含义 |
|---|---|
| `GCAM_SOURCE_DIR` | 经审查的外部源码与构建副本；是本文约定，不是自动加载机制 |
| `GCAM_RUN_DIR` | 新的外部模型任务副本，包含经审查的 `exe/input/libs` 布局，配置、日志和数据库相互独立 |
| `GCAM_RELEASE_DIR` | AirMosaic 现有输出分析适配器实际选择的模型根目录 |

`GCAM_SOURCE_DIR` 和 `GCAM_RUN_DIR` 仅为任务会话约定，AirMosaic 不自动加载它们，它们也不是执行器参数。使用对应示例前，在本地将其设置为已审查且存在的位置。

运行副本通过单独审查的任务准备步骤建立，不能只复制可执行文件。不要在原研究目录或多人共用的运行目录启动模型。按拟用工作目录核对配置、日志、批处理、输入与输出的全部引用。新建运行目录不会自动改写 XML 中的绝对路径。

为兼容当前分析适配器，所选模型根须在 Git 外，且不能与 `AIRMOSAIC_ASSETS_DIR`、`AIRMOSAIC_CONFIG_DIR` 或 `AIRMOSAIC_AUTH_DIR` 重叠。原生模型输出可留在该独立模型任务目录，衍生分析产物使用外部 `assets/results/<project_id>/`。模型副本放进资产根并不会使其成为合法的 `GCAM_RELEASE_DIR`。其他原生输出位置需要明确配置及适配器审查，不能绕过路径检查。见[存储边界](../../../../../harness/storage-and-credentials_ZH.md)。

## 3. 必要时才编译

以下 Makefile 路径按 `gcam-v8.2` 源码结构核对，其他分支需先检查。[该版本根 Makefile](https://github.com/JGCRI/gcam-core/blob/gcam-v8.2/Makefile)通过 `install_hector` 初始化锁定的 Hector 子模块，并把模型目标交给 Linux 构建目录。取得子模块可能需要联网。

依赖选择以实际[分支构建配置](https://github.com/JGCRI/gcam-core/blob/gcam-v8.2/cvs/objects/build/linux/configure.gcam)为准：

| 项目 | 配置决策 |
|---|---|
| C++ 工具链 | 编译器及所需语言标准；官方说明的 GCAM 7+ 路径使用 C++17 |
| Boost 与 Eigen | 匹配源码 include 结构的头文件根，以及所需 Boost 库 |
| Hector | 所选父源码记录的子模块版本，不任意改用最新检出 |
| TBB | 头文件与库的代际、编译器二进制接口及并行构建选项兼容 |
| Java/JNI | JDK 头文件、平台头文件子目录、JVM 库和匹配架构 |
| JAR 资源 | 包含所需驱动与数据库资源的兼容版本类路径 |

在选定任务环境中设置分支要求的变量，常见名称包括 `CXX`、`BOOST_INCLUDE`、`BOOST_LIB`、`EIGEN_INCLUDE`、`TBB_INCLUDE`、`TBB_LIB`、`JAVA_INCLUDE`、`JAVA_LIB` 和 `JARS_LIB`。`JARS_LIB` 是类路径或文件模式，不只是目录名。JDK 布局随版本变化，不能把旧 `jre/lib/server` 路径或历史 Conda 配方当作通用要求。结合所选源码阅读[官方编译说明](https://jgcri.github.io/gcam-doc/gcam-build.html)。

依赖准备完成后，在经审查且固定版本的 Git 源码副本中运行。没有 Git 元信息或锁定子模块的源码压缩包需另行准备：

```bash
set -eu
: "${GCAM_SOURCE_DIR:?Select a reviewed external source copy}"
: "${GCAM_BUILD_JOBS:=1}"
cd "$GCAM_SOURCE_DIR"
git submodule status
make install_hector
cd cvs/objects/build/linux
make gcam -j "$GCAM_BUILD_JOBS"
```

并行度依据可用内存和 CPU 配额选择，不照搬教程的固定值。核对构建退出码和新生成的可执行文件，记录源码身份、选项与依赖版本。Windows 使用所选分支的 Visual Studio 项目，使工具集及 Hector 依赖匹配，再选择适合的发布与架构配置。官方 v8.2 项目路径为 `cvs/objects/build/vc10/objects.vcxproj`，应检查项目内容，不能据目录名推断必须使用哪个编译器版本。Xcode 与 Makefile 路径也须依照所选源码设置。旧目标文件问题使用新构建副本解决，不清理正在运行的模型目录。具体错误见[构建排错](build-troubleshooting.md)。

## 4. 仅为选定的数据任务生成输入 XML

使用与模型及输入版本匹配的 gcamdata 源码和独立 R 依赖环境。审查包元信息和锁定文件；恢复包可能下载依赖，但不会运行模型。先在该数据系统源码目录核对实际接口：

```r
devtools::load_all(".")
formals(driver)
formals(driver_drake)
```

检查后再选择一种驱动及输出范围。已核对的 v8.2 源码中，`driver()` 有 `write_outputs`、`write_xml`、`outdir` 和 `xmldir`；`driver_drake()` 管理缓存目标，参数并不相同。不要假定所有根 Makefile 示例或历史指南使用相同拼写。重建受影响 XML 需要明确依赖及下游覆盖范围，保留源输入并区分生成版本；不删除或解锁其他进程正在使用的缓存。[gcamdata 入门指南](https://jgcri.github.io/gcamdata/articles/getting-started/getting-started.html)说明两种驱动路径，其中历史包版本不是所有模型分支的现行要求。

## 5. 核对配置并从 `exe` 启动

配置名及参数行为由实际二进制解析器和随包启动脚本决定。启动脚本可能绑定特定配置，并不转发用户参数。已核对的 core v8.2 解析器同时接受 `-C file.xml` 和 `-Cfile.xml`，`-L` 指定日志配置，`--version`/`--versionID` 报告程序身份。不同分支的默认值和脚本可能不同，先核对所选版本，不直接套用这些选项。见[固定标签的参数解析器](https://github.com/JGCRI/gcam-core/blob/gcam-v8.2/cvs/objects/main/source/main.cpp)。

启动前检查任务配置的情景组件顺序、校准与输入引用、模拟时期、批处理模式、日志位置，以及全部数据库和输出目标。保留发行包相对布局，在本地选择兼容 JVM 运行环境，并以该副本的 `exe` 为工作目录。并行写入任务分别使用未占用的数据库及输出位置；只换配置文件名不能隔离输出。

以下 Windows PowerShell 示例假定已准备经审查的运行副本和兼容库，并存在任务副本 `configuration_task.xml` 及 `log_conf.xml`。执行它会真实运行模型，不是预检命令：

```powershell
if (-not $env:GCAM_RUN_DIR) { throw 'Select the reviewed isolated model task copy.' }
$gcamExeDir = Join-Path $env:GCAM_RUN_DIR 'exe'
$gcamBinary = Join-Path $gcamExeDir 'gcam.exe'
foreach ($gcamFile in @($gcamBinary, (Join-Path $gcamExeDir 'configuration_task.xml'), (Join-Path $gcamExeDir 'log_conf.xml'))) {
    if (-not (Test-Path -LiteralPath $gcamFile -PathType Leaf)) { throw 'A reviewed runtime file is missing.' }
}
Push-Location -LiteralPath $gcamExeDir
try {
    & $gcamBinary --version
    if ($LASTEXITCODE -ne 0) { throw 'Executable identity check failed.' }
    & $gcamBinary -C 'configuration_task.xml' -L 'log_conf.xml'
    $gcamExitCode = $LASTEXITCODE
    if ($gcamExitCode -ne 0) { throw 'GCAM returned a nonzero exit code; inspect the task logs.' }
} finally {
    Pop-Location
}
```

POSIX 采用等价方式，从副本 `exe` 目录调用实际二进制，并选择该分支需要的共享库环境。已核对 Makefile 的 POSIX 路径也生成 `gcam.exe`。不要假定 Windows `.bat`、macOS `.command` 和直接执行应用相同环境或保留相同子进程退出码；尽量保留直接进程的退出码。

## 6. 验证后再交接

核对进程结束、配置指定的主日志和求解器日志、所有要求时期、市场或求解失败情况，以及数据库写入完成。进程码为零或日志看似成功都不足以单独验收。已核对主程序可能在返回失败状态前仍打印最后的成功样式信息，因此需结合退出码及各期求解证据。科学使用前核对情景身份、时间覆盖、单位、校准和结果合理性。

GCAM 或其他写入程序仍使用数据库时，不打开、替换或删除它。写入完成后查询，保留原库。模型默认输出布局未必匹配所有 AirMosaic 适配器：

| 现有工具 | `GCAM_RELEASE_DIR` 下要求的源布局 |
|---|---|
| `gcam_inspect_output_structure` | `output/database_basexdb` 及 `database_R/Prov_code_china.csv` |
| `gcam_extract_market_sector`、`gcam_extract_technology_components` | `output/<scenario>/database_basexdb` 及兼容的发行包 JAR 资源 |

按实际产物审查交接和布局，不虚构情景文件夹，也不只为通过预检而复制数据库。参数和衍生输出见[输出操作](operations_ZH.md)。这些工具的预检不生成输入、不启动 GCAM，也不验证模拟。原生日志和个人配置留在本地，共享版本、要求与完成时期、检查及未解决科学问题的脱敏摘要。

## 来源与核验范围

版本依据核对日期为 2026-10-30：参考本地 GCAM-China v8 安装运行说明、gcamdata 使用说明，以及 core v8.2 构建文件、驱动签名和参数解析器，并与上述官方来源核对。这属于接口及文档检查，不是各平台都已实跑的配方。依赖、任务副本引用、输入生成以及数值和科学验收仍需在所选任务环境验证。
