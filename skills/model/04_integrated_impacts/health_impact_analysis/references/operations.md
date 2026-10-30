# Configure and adapt the health templates

**English** | [中文](operations_ZH.md)

## Inspect without execution

From the repository root:

```sh
python -m runtime.cli describe-tool pm25_hia_calculate_template
python -m runtime.cli describe-tool pm25_hia_visualize_template
```

The calculation template is `templates/calculate_pm25_deaths.R` (data.table). Visualization is `templates/visualize_pm25_deaths.R` (data.table, ggplot2, sf, RColorBrewer). Their paths are relative to this skill. Both run at source time; neither accepts CLI flags or loads a task JSON/YAML.

## Explicit task configuration

Keep input data in external assets, non-secret task settings in CONFIG_DIR, and adapted scripts/results under a fresh external `results/<project_id>/` task directory. No runner path checks or sanitized receipts apply to direct R calls.

| Variable | Use |
|---|---|
| `PM25_HIA_CONC_DIR` | `pm25_annual_<year>.csv`: X_Lon, Y_Lat, concentration |
| `PM25_HIA_POP_DIR` | `Population_g0.1_<year>.Rds`, `Age_Structure_Fraction_g0.1_<year>.Rds` |
| `PM25_HIA_MORT_FILE`, `PM25_HIA_RR_FILE` | Baseline-rate and RR lookup CSVs |
| `PM25_HIA_OUTPUT_DIR` | Explicit new external output directory |
| `PM25_HIA_YEARS`, `PM25_HIA_CURVE` | Comma-separated target years; selected curve label |
| `PM25_HIA_POP_FILE`, `PM25_HIA_SHP_DIR` | Plot population RDS and boundary directory |
| `PM25_HIA_PLOT_YEAR` | Single map year, independent of calculation years |

Use [schemas](data_requirements.md) for remaining fields. Assigning R variables before `source()` is insufficient: the template overwrites configuration with `Sys.getenv()`. Set environment variables or explicitly revise that configuration in the copy.

After task-copy adaptation and explicit calculation authorization, a local R driver can supply settings and source the adapted file:

```r
Sys.setenv(PM25_HIA_CONC_DIR = conc_dir, PM25_HIA_POP_DIR = pop_dir,
           PM25_HIA_MORT_FILE = mort_file, PM25_HIA_RR_FILE = rr_file,
           PM25_HIA_OUTPUT_DIR = result_dir, PM25_HIA_YEARS = target_years,
           PM25_HIA_CURVE = curve_label)
source(adapted_calculation_file)
```

The named R strings are required caller inputs, not defined defaults. Run the completed personal driver with `Rscript --vanilla <personal-driver.R>`. For plotting set its three additional variables above and source the adapted visualization file. `examples/workflow_pm25_hia.R` is illustrative: placeholder paths and `../../templates/` source paths must be replaced relative to the actual working directory.

## Required adaptation and checks

The current calculation hardcodes China/Rate filtering, rewrites mortality `Year`, caps concentration at 200, rounds to 0.1 and sums 80+ subgroup rates. These are implementation assumptions to review, not validated scientific defaults. Correct year filtering must use the original source year. Aggregate fine-age rates with corresponding population weights; do not simply add rates. Confirm whether age-sex fractions use a total-population or sex-specific denominator before multiplication by Pop.

Validate RR/reference concentration and domain, matched endpoints/ages, unique join keys, missing exposure and excluded population. Check RR=1 gives zero attributable deaths and a small hand-calculated case matches the adapted code. Review rate-to-person conversion (`/100000`), no duplicate endpoints and aggregation without overlapping overall/urban/other populations.

Expected calculation filenames are `pm25_premature_death_grid_<curve>_<year>.csv` and `pm25_premature_death_summary_<curve>_<year>.csv`. Check Mort is a death count, the actual `MortRate_PM25` scale in the adapted code, and summary totals against grid sums. Review map units, extent, population support and missing cells. Save configuration, source versions and validation outcomes with the task; file presence alone is insufficient.

The template also replaces missing joined attributable rates with zero. Adapt this behavior to preserve and report missing exposure/RR support; missing matches are not evidence of zero burden.

## ER selection and stop conditions

Read [actual ER sources](exposure_response.md) and run its read-only coefficient check before adapting a log-linear task. Store the selected source ID/version, reference and below-reference rule, exact eligibility, expected endpoint set, requested scenario estimand, whether baseline mortality is observed at baseline exposure or standardized/reference mortality, and exposure support in non-secret task configuration. A hash-valid source does not approve these scientific choices. Stop on missing source rows, hash mismatch, ambiguous ages/parameter headers, unknown units or mismatched exposure statistics. No converter to the R lookup schema is currently supplied.

The two `describe-tool` IDs above remain the actual catalog entries, with `execution.enabled=false`; do not call run-tool as a calculation workaround. The new Python helper is invoked directly and has no tool ID. Direct R `source()` calls remain conditional on adapting and reviewing a task copy. The template computes fixed-rate attributable burden only; risk-scaled avoided mortality requires a separately reviewed task implementation, not subtraction labelled as the same estimand.

Inspect the separate ER dataset reference with `python -m runtime.cli describe-dataset pm25_exposure_response`. This is detail metadata, not an automatic downloader or a claim that the acquisition-only `list-datasets` command supplies these curves.
