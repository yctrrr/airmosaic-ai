# Using an external CHEER GAMS release

**English** | [中文](cheer-gams-operations_ZH.md)

The [CHEER downloads page](https://cheer.org.cn/downloads/) offers CHEER demo in Python and GAMS and CHEER-P demo in GAMS. Its GAMS versions require a GAMS license. The model archive, GDX databases, GAMS installation and license remain external to this repository. The Python CGE tutorial in this skill is an independent synthetic model; it does not execute CHEER.

## Inspect and reproduce an obtained release

1. Record the official download page, archive filename, download date, release/base-year statements and archive hash. Keep an untouched copy and work from a separate external copy. Inspect files before running them.
2. Identify the actual entry point; `run.gms` was the entry in the previously inspected demos, but verify the obtained archive. Read enabled `$include`, `$batinclude`, `$gdxin` and model/solve statements. GAMS [include resolution](https://www.gams.com/latest/docs/UG_DollarControlOptions.html) depends on the working directory and `InputDir`. Check file case on case-sensitive hosts and locate every referenced GDX file before execution.
3. Check `gams -v`, an available model-compatible solver and the [GAMS license](https://www.gams.com/latest/docs/UG_License.html). If any are missing, report **source preflight only**. Do not call a parsed source tree a numerical reproduction.
4. Run the unchanged benchmark first from the verified model work directory. If its confirmed entry is `run.gms`, `gams run.gms lo=2` is an example. Record the command, listing (`.lst`), solver/model status and output files. Compare the solved benchmark with the supplied SAM and published reference totals before editing scenarios.
5. Edit only the external working copy. For a new shock, locate the parameter definition and active scenario assignment; change the intended value or include rather than a report variable. Keep benchmark and scenario copies separate, use the same closure and numeraire, and document affected region, sector, year and units. For an MPSGE release, its [official syntax guide](https://www.gams.com/latest/docs/UG_MPSGE_Intro.html) explains `$SECTORS`, `$COMMODITIES`, `$CONSUMERS`, `$PROD`, `$DEMAND` and model generation. Changes to structural equations require recalibration and benchmark checks.
6. Re-run, inspect listing and numeric residuals, and compare paired benchmark/scenario prices, quantities, income and environmental outputs. A successful solver status without benchmark replication is insufficient. Keep results, logs and private data outside Git.

In the previously reviewed CHEER-P demo, `sets.gms` defined indices, `cal.gms` handled calibration, `elasticities.gms` held assumed elasticities, `emission.gms` contained environmental quantities, `core.gms` contained equilibrium logic, and `run.gms` orchestrated the run. Treat these names as **search starting points**: trace the enabled include graph in the downloaded release before editing. For a sector expansion, change sets, SAM mapping, parameter dimensions and every affected equation together; for a parameter scenario, change the active assignment after baseline replication; for an environmental satellite, verify whether it enters an equation or only a report.

The previously inspected CHEER archives had some include-path case mismatches. This is a release-specific preflight observation, not a claim about all versions or a license to alter source files automatically.
