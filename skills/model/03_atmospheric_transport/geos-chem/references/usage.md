# Classic 14.8.0: your first checked forward run

**English** | [中文](usage_ZH.md)

This tutorial reproduces the successful **TransportTracers/MERRA-2/global 4×5/47-level** case for **2019-01-01 00:00–01:00 UTC**. It produces 21 concentration fields and 21 restart fields. The chemistry switch here selects the tracer simulation's own processes; this case is not a full pollution-chemistry evaluation.

## 1. Prepare directories and software

Use Linux/POSIX with Git, Python 3.10+, CMake ≥3.13, a compatible Fortran/C/C++ toolchain, and matching NetCDF-C/NetCDF-Fortran. The successful build used Intel Fortran and NetCDF. Set `FC`, `CC`, `CXX`, `GC_CMAKE`, `GC_NETCDF_PREFIX` to the actual executable names/library prefix in your environment. The same environment must be available when running. An unrelated conda library environment can interfere with Intel/NetCDF linking.

```bash
set -euo pipefail
: "${AIRMOSAIC_REPO:?set the AirMosaic source checkout}"
: "${GC_ROOT:?set an existing project directory outside Git}"
GC_SKILL="$AIRMOSAIC_REPO/skills/model/03_atmospheric_transport/geos-chem"
mkdir -p "$GC_ROOT/source" "$GC_ROOT/inputs/ExtData" "$GC_ROOT/results"
```

Use short paths without spaces. `GC_ROOT` contains data and outputs; `AIRMOSAIC_REPO` contains this skill. A model run belongs in an authorized allocation; the example used at most four threads, a 24 GiB request and shared nodes. These commands do not submit a scheduler job.

## 2. Select source by model version

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

Choose the release tag for the model number, here **Classic 14.8.0**; no specified Git commit hash is required. The helper checks the model version declared in the source and records the actual source identity automatically. Submodules must not have `-`, `+` or `U` prefixes. In this release `GEOS-Chem`, `HEMCO`, `Cloud-J` and `HETP` are direct children of `src/`. The tested `MECH=fullchem` build option is preserved by the helper; the runtime simulation remains `TransportTracers`.

To upgrade, set `GC_VERSION` to the target release and follow its configuration/data documentation. These complete templates and the fixed output checker use the 14.8.0 case as their reference. Recheck configuration interfaces, build options, input compatibility and outputs for the new version; previous experiment results do not transfer automatically.

## 3. Compile once

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

Expected executable: `build/bin/gcclassic`. The helper checks source contents, uses a fresh build directory and saves compile/link logs and a binary hash. `--jobs` is compilation parallelism, not a scientific parameter. The combined prefix must contain `include/`, `lib/libnetcdf.so` and `lib/libnetcdff.so`; split installations need explicit CMake adaptation. See [official compilation](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/compile-cmake.html).

## 4. Configure the inputs

Edit the copied `settings.json`: replace `@DATA_ROOT@` with the absolute path of `GC_ROOT/inputs/ExtData`. Keep the demonstrated dates for the first run. The helper renders the [complete native templates](../templates/classic_14.8.0/settings.json) and copies the version-matched species database/downloader from the source.

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

| File / parameter | Meaning and effect |
|---|---|
| `settings.json:start_utc`, `end_utc` | UTC simulation interval, rendered to `simulation.start_date/end_date`; the helper supports whole-hour intervals |
| `settings.json:data_root` | Existing external data root, rendered into YAML and HEMCO input paths |
| `geoschem_config.yml:simulation.name` | Simulation family; keep `TransportTracers` for this tutorial |
| `simulation.met_field` | `MERRA2`; must match the actual meteorological files and HEMCO met settings |
| `simulation.read_restart_as_real8` | `false` uses the tested HEMCO reading/remapping route on the reduced 47-level grid |
| `grid.resolution`, `number_of_levels` | 4° latitude ×5° longitude, 47 layers; changing these requires compatible met/restart and a new check |
| `grid.longitude/latitude` | Global extent, date-line centering and half-size polar boxes; these define coordinates, not a post-processing crop |
| `timesteps.transport_timestep_in_s` | 600 seconds between transport updates |
| `timesteps.chemistry_timestep_in_s` | 1200 seconds between the simulation's chemistry updates |
| `operations.*.activate` | Enable chemistry, convection, deposition, PBL mixing and transport; changing a switch changes the physical experiment |
| `operations.transport.transported_species` | The 21 transported species and their required restart/metadata entries |
| `HEMCO_Config.rc:ROOT`, `METDIR`, `GC_RESTART` | Inventory root, met path selection and restart source; inspect the entire active block, not just filenames |
| HEMCO source line | Name, file, variable, time coverage, cycling rule, dimensions, units, target species, scale-factor IDs, category and hierarchy |
| `HEMCO_Diagn.rc` | Emission diagnostics; `HISTORY.rc` does not replace it |
| `HISTORY.rc:COLLECTIONS` | Enabled output collections; defining a collection alone does not activate it |
| `SpeciesConc.frequency` | Output/sample interval: `00000000 010000` means one hour |
| `SpeciesConc.duration` | How often a new file is opened; distinct from frequency |
| `SpeciesConc.mode` | `time-averaged` for an interval mean; `instantaneous` for a state at a sample time |
| `SpeciesConc.fields` | Requested variables; `SpeciesConcVV_?ALL?` outputs all species in dry-air mixing-ratio units |
| `Restart.frequency/duration` | `'End'` writes the end state needed to continue a run |
| `species_database.yml` | Species identities, molecular weights and properties; retain the source-matched copy |

The native dry-run inventories required paths. It does not generate scientific outputs. Keep all five rendered input files together, plus `species_database.yml`.

## 5. Supply the physical files

The data root needs preprocessed MERRA-2 meteorology, compatible restart, constants and the active source/ancillary files listed by the dry-run. The tested case required 16 files totaling about 498 MB. Reuse compatible files already present. For missing files only, inventory, measure and then fetch within the authorized cumulative budget:

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

Inspect the measured size before fetching. Existing final files and unknown/partial transfers are not silently overwritten; failed reservations remain in the same ledger. Larger studies use a separately reviewed budget and the version's official downloader. [Input documentation](https://geos-chem.readthedocs.io/en/14.8.0/gcclassic-user-guide/download-data.html).

## 6. Run and inspect results

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

The command must exit zero and the log must reach the selected end time. Inspect `OutputDir/GEOSChem.SpeciesConc.20190101_0000z.nc4` and `Restarts/GEOSChem.Restart.20190101_0100z.nc4`. The first is the hour's averaged concentration; the second is the instantaneous end state.

```bash
: "${GC_NETCDF_C_LIBRARY:?set the full path to the matching libnetcdf.so}"
python "$GC_SKILL/scripts/check_outputs.py" \
  --root "$GC_ROOT" --library "$GC_NETCDF_C_LIBRARY" \
  --concentration "$GC_CASE/run/OutputDir/GEOSChem.SpeciesConc.20190101_0000z.nc4" \
  --restart "$GC_CASE/run/Restarts/GEOSChem.Restart.20190101_0100z.nc4" \
  --history "$GC_CASE/run/HISTORY.rc" --unit 'mol mol-1 dry' \
  --output "$GC_CASE/output-check.json"
```

This checker is deliberately fixed to the successful 2019 one-hour/47-level/21-species case. It checks species, coordinates/hybrid levels, dimensions, units, averaging, interval and finite values. Changing dates, collections or species requires an adapted output contract; do not run this checker on another case and call that case validated.

## 7. Make one controlled change

| Desired change | Edit | Recheck / expected output |
|---|---|---|
| Run a different hour/day | Copy `settings.json`, change both UTC dates, render a new run | New restart and complete met coverage; rerun dry-run; output names carry the new time |
| Write 30-minute concentrations | In a fresh run change `SpeciesConc.frequency` to `00000000 003000`; choose a duration ≥ frequency | Two samples per hour; keep time averaging explicit; fixed checker needs adaptation |
| Write fewer variables | Change `SpeciesConc.fields` to existing transported names such as `SpeciesConcVV_CO_50` | Smaller diagnostic files; the simulated species remain unchanged |
| Change emissions | Adjust the active HEMCO source or scaling entry, preserving units and hierarchy | HEMCO diagnostics must show the intended flux change before interpreting concentrations |
| Change initial state | Update the active `GC_RESTART` file in HEMCO | Time/grid/species/units and spin-up must be reviewed |
| Change grid/process family | Regenerate a compatible configuration, build if required and obtain matching data | New experiment; this tutorial's acceptance does not carry over |

Output selection changes what is saved; input/process changes can change the modeled trajectory. Compare scenarios with the same meteorology, numerical settings and valid support when isolating an emission effect. See the [scientific method](../../../../../methods/03_atmospheric_transport/geos_chem.md) and [History guide](https://geos-chem.readthedocs.io/en/14.8.0/geos-chem-shared-docs/supplemental-guides/history-diag-guide.html).
