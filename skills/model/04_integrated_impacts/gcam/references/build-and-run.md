# Prepare, build and run GCAM

**English** | [中文](build-and-run_ZH.md)

Use this guide for a task-selected model version and environment. These are manual operations, not an AirMosaic compilation or simulation adapter. [Methods](../../../../../methods/04_integrated_impacts/gcam.md) explain experiment design and acceptance; [output operations](operations.md) document the implemented analysis tools.

## 1. Select the necessary route

| Need | Route | Check before proceeding |
|---|---|---|
| Run an unchanged compatible model | Use its platform release package | Executable, supporting libraries and input XML belong to the same release |
| Change C++ behavior or target another platform | Build the chosen source revision | Compiler, dependency versions, submodules, build options and architecture |
| Change data-system inputs or processing | Rebuild the matching gcamdata outputs | R package/API, dependency lock, affected modules and XML compatibility |
| Query an existing result | Use the output-analysis tools | Completed database, scenario/layout, Java/BaseX and applicable units |

Editing a scenario XML does not normally require rebuilding C++; using supplied XML does not require rerunning gcamdata. A source archive is not necessarily a complete runtime package. GCAM-China and GCAM-Core binaries, inputs and configuration names are not interchangeable. The [official user guide](https://jgcri.github.io/gcam-doc/user-guide.html) distinguishes release use, source compilation and input generation.

## 2. Choose locations and freeze the version

Record the model variant, release/tag or source revision, platform, selected configuration, input version, requested periods and expected outputs in the task record. Keep a baseline and an independently named intervention. Do not substitute the latest main branch for a study's pinned source.

| Variable | Meaning |
|---|---|
| `GCAM_SOURCE_DIR` | Reviewed external source/build copy; a documentation convention, not an automatic loader |
| `GCAM_RUN_DIR` | Fresh external model task copy with a reviewed `exe/input/libs` layout and independent configuration, logs and database |
| `GCAM_RELEASE_DIR` | Actual root selected for AirMosaic's existing output-analysis adapters |

`GCAM_SOURCE_DIR` and `GCAM_RUN_DIR` are task-session conventions only: AirMosaic does not automatically load them and they are not runner parameters. Set them locally to the reviewed existing locations before using the relevant example.

Create the runtime copy through a separately reviewed task preparation step; simply copying the executable is insufficient. Do not run in an original study or shared live model directory. Check all configuration, logger, batch, input and output references from the intended working directory. A run directory alone does not relocate absolute paths in XML.

For compatibility with the current analysis adapters, the selected model root must be outside Git and must not overlap `AIRMOSAIC_ASSETS_DIR`, `AIRMOSAIC_CONFIG_DIR` or `AIRMOSAIC_AUTH_DIR`. Native model outputs can remain in that isolated model task tree; derived analysis outputs use external `assets/results/<project_id>/`. Placing a native model copy inside the asset root does not make it acceptable as `GCAM_RELEASE_DIR`. Another native-output location needs explicit configuration and adapter review rather than a path-check bypass. See [storage boundaries](../../../../../harness/storage-and-credentials.md).

## 3. Compile only when needed

The following Makefile route was checked against the `gcam-v8.2` source structure; another branch must be inspected first. [Its root Makefile](https://github.com/JGCRI/gcam-core/blob/gcam-v8.2/Makefile) initializes the pinned Hector submodule through `install_hector` and delegates model targets to the Linux build directory. Submodule retrieval may require network access.

Select dependencies using the actual [branch build configuration](https://github.com/JGCRI/gcam-core/blob/gcam-v8.2/cvs/objects/build/linux/configure.gcam):

| Item | Configuration decision |
|---|---|
| C++ toolchain | Compiler and required language standard; the documented GCAM 7+ route uses C++17 |
| Boost and Eigen | Header roots matching the source's include structure; any required Boost libraries |
| Hector | Submodule revision recorded by the chosen parent source, not an arbitrary latest checkout |
| TBB | Header/library generation and compiler ABI compatible with the parallel build option |
| Java/JNI | JDK headers, platform header directory, JVM library and compatible architecture |
| JAR resources | Version-compatible classpath containing the required driver/database resources |

Set the branch-required variables in the chosen task environment. Typical names include `CXX`, `BOOST_INCLUDE`, `BOOST_LIB`, `EIGEN_INCLUDE`, `TBB_INCLUDE`, `TBB_LIB`, `JAVA_INCLUDE`, `JAVA_LIB` and `JARS_LIB`. `JARS_LIB` is a classpath/file pattern, not merely a directory name. JDK layout changes across versions; do not copy a historical `jre/lib/server` path or an old Conda recipe as a universal requirement. Review [official build instructions](https://jgcri.github.io/gcam-doc/gcam-build.html) together with the selected source.

After dependency preparation, run from the reviewed, version-pinned Git source copy. An archive without Git metadata or the pinned submodule needs separate preparation:

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

Choose parallelism from available memory and CPU allocation, not a fixed tutorial value. Check the build exit code and the newly generated executable, then record source identity, options and dependency versions. For Windows, use the selected branch's Visual Studio project, align its toolset and Hector dependencies, and choose the appropriate Release/architecture configuration. The documented v8.2 project path is `cvs/objects/build/vc10/objects.vcxproj`; inspect it rather than assuming the directory name specifies the required compiler version. Xcode and Makefile routes similarly require the chosen source's settings. Do not clean a live model tree to resolve stale objects; use a fresh build copy. Error-specific checks are in [build troubleshooting](build-troubleshooting.md).

## 4. Generate input XML only for the selected data task

Use the gcamdata source matched to the model/input version and an isolated R dependency environment. Review its package metadata and lockfile; package restoration may download dependencies and does not run the model. From that data-system source directory, first inspect the actual APIs:

```r
devtools::load_all(".")
formals(driver)
formals(driver_drake)
```

Choose one driver and its output scope after that inspection. In the checked v8.2 source, `driver()` has `write_outputs`, `write_xml`, `outdir` and `xmldir`; `driver_drake()` manages cached targets and exposes different arguments. Do not assume every root Makefile example or historical guide uses the same spelling. Rebuilding affected XML requires a task-specific plan for dependencies and downstream coverage. Preserve source inputs and distinguish generated XML versions; do not delete or unlock a cache used by another process. The [gcamdata getting-started guide](https://jgcri.github.io/gcamdata/articles/getting-started/getting-started.html) describes the two driver routes; its historical package versions are not current requirements for every model branch.

## 5. Review configuration and launch from `exe`

The actual executable parser and supplied launcher determine the configuration name and argument handling. A launcher may bind a particular configuration instead of forwarding arguments. In the checked core v8.2 parser, both `-C file.xml` and `-Cfile.xml` work; `-L` selects the logger configuration, and `--version`/`--versionID` report identity. Defaults and wrappers can differ by branch, so inspect the selected version rather than applying those flags blindly. See the [tagged argument parser](https://github.com/JGCRI/gcam-core/blob/gcam-v8.2/cvs/objects/main/source/main.cpp).

Before launching, review the task-copy configuration's scenario-component order, calibration/input references, run periods, batch mode, logger destinations and every database/output target. Retain the release's relative layout, prepare the version-compatible JVM runtime locally and use its `exe` directory as the working directory. Choose an unused database/output location for each concurrent writer. A relocated configuration filename alone does not isolate its outputs.

The following Windows PowerShell example assumes a reviewed runtime copy, compatible libraries already selected, and an existing task-copy `configuration_task.xml` and `log_conf.xml`. It performs a real model run when executed; it is not a dry-run command:

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

On POSIX, use the equivalent launch from that copy's `exe` directory and the actual binary name, with the selected branch's shared-library environment. The checked Makefile emits `gcam.exe` even on its POSIX route. Do not assume a Windows `.bat`, a macOS `.command`, and direct execution apply identical environment settings or preserve the child exit code. Retain the direct process exit code where possible.

## 6. Verify, then hand off

Check process termination, the configured main and solver logs, every requested period, market/solver failures and completion of database writes. A zero process code or a success-looking log line alone is insufficient. The checked parser/main source can print its final success-looking message before returning a failure status; combine the code with period/solver evidence. Confirm scenario identity, time coverage, units, calibration and plausibility before using the result scientifically.

Do not open, replace or delete a database while GCAM or another writer is using it. Query after writes finish and preserve the original database. Default native output layouts need not match every AirMosaic adapter:

| Existing tool | Required source layout below `GCAM_RELEASE_DIR` |
|---|---|
| `gcam_inspect_output_structure` | `output/database_basexdb` and `database_R/Prov_code_china.csv` |
| `gcam_extract_market_sector`, `gcam_extract_technology_components` | `output/<scenario>/database_basexdb` and the compatible release JAR resources |

Review the actual handoff and layout rather than inventing scenario folders or copying databases just to satisfy preflight. Use [output operations](operations.md) for parameters and derived outputs. Their dry-run checks do not build inputs, start GCAM or validate a simulation. Keep native logs and personal configuration local; share a sanitized account of versions, requested/completed periods, checks and unresolved scientific questions.

## Source and verification scope

Version basis, reviewed 2026-10-30: local GCAM-China v8 installation/run guidance and gcamdata usage guidance, plus core v8.2 build files, driver signatures and the argument parser, cross-checked with the linked official sources. These are interface and documentation checks, not an executed build/run recipe for every platform. Dependencies, task-copy references, input generation and numerical/scientific acceptance require verification in the chosen task environment.
