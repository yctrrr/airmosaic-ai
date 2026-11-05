# Public v35l: chemical forward, adjoint and gradient tutorial

**English** | [中文](adjoint_ZH.md)

Reproduce the checked three-hour **chemistry-component** case, **2026-10-26 03–06 UTC**, global 4° latitude ×5° longitude, 47 layers and 43 tracers. The control is surface initial NOx scaling and the response is terminal surface Ox mass. This is the public v35l fork; it is not authenticated official v36. Keep its executable and inputs separate from Classic.

## 1. Prepare software and obtain source

Use Linux/POSIX, Python ≥3.10, Git, make, Intel `ifort`, matching NetCDF-C/Fortran, NumPy and netCDF4. The successful environment used Intel oneAPI 2023 and NetCDF 4.9.2. Load your site's compatible environment inside an authorized compute allocation. The commands do not submit jobs or install dependencies.

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

The preparation helper records the selected model version, checks patch context in a fresh copy and applies the supplied [profile patch](../templates/adjoint_v35l/chemistry-component.patch) to a fresh copy. It selects GEOS-FP, removes unselected observation dependencies and pairs excluded surface exchange/dust settling in forward and adjoint code. It allocates zero surface-loss rates without supplying fictional land tables. It does not replace chemical equations or enable a full-process model. Keep `profile-receipt.json`.

For a later version, select its release package or branch by model number and update the matching configuration. The helper does not require an old commit or historical source-file hashes; it records actual source identity and before/after hashes automatically. The bundled patch/dependency table was tested with v35l. Adapt patch conflicts or changed interfaces, then rebuild, check inputs and verify derivatives. Patch applicability establishes source preparation only.

## 2. Compile the prepared copy

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

`-j1` avoids legacy module-order races; the supplied dependency file adds the required module order. `-qopenmp` is the supported Intel OpenMP option; `-convert big_endian` matches BPCH input. `-mcmodel=large` accommodates legacy arrays. `HDF=no`, `SAT_NETCDF=no`, `LIDORT=no` and `USE_MKL=no` exclude unselected optional dependencies. `AIRMOSAIC_CHEM_COMPONENT` defines this bounded process configuration and must be present. These options do not make arbitrary branches compatible. Check the make exit status and nonempty binary; file presence alone can also describe an old failed build.

## 3. Arrange physical inputs

| Input | Meaning / native location beneath `data_root` |
|---|---|
| GEOS-FP constants | `GEOS_FP/2011/01/GEOSFP.20110101.CN.4x5.nc`; land/ocean fractions and grid constants; the directory year is the constants product's date |
| Hybrid levels | `GEOS_FP/2011/01/GEOSFP.ApBp.nc`; pressure-coordinate support |
| GEOS-FP daily files | `GEOS_FP/2026/10/GEOSFP.20261026.{A1,A3cld,A3dyn,A3mstC,A3mstE,I3}.4x5.nc`; hourly/three-hourly means and instantaneous states |
| UV albedo | `uvalbedo_200111/uvalbedo.geos.4x5`; climatological surface reflectivity, converted from the official backward-compatible NetCDF |
| TOMS ozone | `TOMS_201203/TOMS_O3col_2010.geos.4x5`; conservative spherical remap from the official 1×1 BPCH, 36 blocks |
| Initial state | Verified 43-tracer legacy restart; the demonstration changes time metadata only and explicitly labels the result artificial |
| Chemistry tables | Eleven files copied from the selected model source's `runs/v8-02-01/geos5/`: `chemga.dat`, `diaginfo.dat`, `globchem.dat`, `jv_atms.dat`, `jv_spec_aod.dat`, `jv_spec.dat`, `mglob.dat`, `ratj.d`, `RXN_ID`, `STR_ID`, `tracerinfo.dat` |

The constants, I3 endpoints and interval means are all needed. Starting at 03 and ending at 04 UTC was insufficient for the native I3 interface; use the complete demonstrated 03–06 interval. Renaming meteorological files does not change their actual timestamps or fields.

The following inventory maps official objects to the native layout, reuses existing files and downloads only missing files. Existing files still need product/time/content checks. The shared transfer ledger has a cumulative 2 GiB ceiling; failed attempts retain reservations and partial files. Review rather than reset the ledger if it blocks. HTTPS certificate verification stays enabled.

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

Obtain the original initial state from [Zenodo record 7517355](https://zenodo.org/records/7517355), `gcadj_std.zip`, member `gcadj_std/runs/v8-02-01/geosfp/restart.geos5.2005070100`. The archive is 1,348,591,027 bytes; reuse a verified local member when available. The conversion helper automatically checks the demonstrated restart member’s integrity. Downloading/extracting the archive is a separate explicit acquisition step; the above bucket helper does not fetch Zenodo. The successful test extracted the member with HTTP Range requests and verified its hash, rather than downloading the whole archive.

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

The conversion script reopens outputs and checks numerical equality/conservation. Preserve UV numeric values (about 0.01–0.95); the legacy `percent` label does **not** justify dividing by 100. TOMS years after 2010 are clamped by native source to 2010. The derived restart retains every original tracer value and changes BPCH time metadata only; it is not a modern atmospheric analysis or spin-up. Species names are not embedded in this legacy BPCH; the 43-tracer mapping is supported by the archive documentation and branch table, without independent embedded metadata confirmation.

## 4. Configure a fresh experiment

In the copied `settings.json`, set `data_root` to `GC_DATA`'s absolute path and `restart_file` to `GC_DATA/derived/initial.artificial.2026102603.bpch`'s absolute path. Keep the demonstrated dates, control 1, response 2 and perturbations `[0.1,0.03,0.01]` for the first case. Paths must be short and have no spaces. Templates retain the original fixed-column menu layout; do not reformat labels or remove inactive menu rows.

```bash
python "$GC_SKILL/scripts/configure_run.py" --mode adjoint --root "$GC_ROOT" \
  --source "$GC_SOURCE" --run "$GC_CASE/prepared" --settings "$GC_CASE/settings.json"
python "$GC_SKILL/scripts/configure_run.py" --mode adjoint --root "$GC_ROOT" \
  --source "$GC_SOURCE" --run "$GC_CASE/prepared" --settings "$GC_CASE/settings.json" --execute
```

| Setting / native parameter | Meaning and demonstrated choice |
|---|---|
| `start_utc`, `end_utc` | UTC interval; helper requires a same-day, three-hour I3 interval starting on a three-hour boundary |
| `data_root`, `restart_file` | Native met/auxiliary root and compatible 43-tracer initial state; rendering alone does not validate their contents |
| `control_tracer` / `ICSFD` | Perturbed initial tracer ID, `1=NOx`; also updates the LICS control table |
| `response_tracer` / `NFD` | Saved terminal response tracer ID, `2=Ox`; also updates the observation/objective table |
| `fd_steps` / `FD_DIFF` | Three distinct descending additive scale perturbations; these are dimensionless, not emission percentages |
| `input.geos:Type of simulation`, `Number of Tracers` | `3`, `43`; NOx/Ox families include multiple chemical species; keep their membership definitions |
| Transport / cloud convection / PBL / emissions / deposition | All `F` in this component; enabling one requires another reviewed model configuration and compatible inputs |
| Online aerosol switches | Sulfate/carbon/dust/sea-salt chemistry state enabled; does not imply enabled emission or deposition processes |
| Chemistry timestep | 60 minutes in the native chemistry setup; three-hour run contains three chemistry calls |
| Restart name / monthly schedule | `restart.output.component.YYYYMMDDhh`; only the end day is set to `3`; native fixed formats use 31/29/30-day row widths |
| `LADJ`, `LSENS`, `L4DVAR`, `L3DVAR` | `T,T,F,F`: sensitivity experiment, without an inversion/assimilation optimization |
| `FD_GLOB`, `FD_SPOT` | `T,F`: perturb all horizontal cells at `LFD=1`; IFD/JFD do not reduce this test to one receptor |
| `LICS`, `LADJ_EMS` | `T,F`: initial-condition scaling control; inactive emission table does not create an emission experiment |
| `NSOPT`, LICS `Tracer #1` | One optimized tracer, with `SF_DEFAULT=1`; scaling is relative to the supplied initial field |
| `REG_PARAM`, `ERROR`, `APSRC` | Prior settings; `APSRC=F` excludes the a priori cost term in this demonstration |
| `NOBS`, objective `Tracer #1` | One response tracer, Ox; `tracer kg/box=T`, other objective units `F` |
| `LFD`, `IFD/JFD` | Surface level 1; horizontal spot indices are inactive under `FD_GLOB` |
| Regional mask / observation limiting | `F`; inactive mask filenames are placeholders, not required inputs |
| `OBS_FREQ`, forcing-time line | Native observation timing controls, `60` minutes and the start time here; use the FD driver's actual terminal-state outputs for the derivative comparison |
| `LADJ_CHEM`, `LAERO_THEM`, ISORROPIAII | `T,T,F`; preserve this chemical/thermodynamic selection for reproduction |
| `LDEL_CHKPT`, `LITR`, `LPRINTFD`, `LADJ_TRAJ` | `F,T,F,F`: keep checkpoints and iteration diagnostics, disable extra debug/trajectory printing |
| `ITER` | Two integers on separate lines: current call number and maximum number of calls (`3`) |
| `OptData/`, `adjtmp/`, `diagadj/`, `TMP/` | Cost/gradient data, adjoint checkpoints, diagnostic states and temporary working files |

The [complete templates](../templates/adjoint_v35l/input.gcadj.in) contain the inactive options for the native parser. They are not additional tested recipes. The generated `configuration-receipt.json` binds settings and file hashes. To edit native files afterwards, prepare a new configuration and update its reviewed receipt; the runner refuses changed prepared files.

## 5. Execute baseline, plus and minus calls

For each perturbation, the native driver needs **three separate executable invocations**: baseline forward+adjoint, positive perturbation, negative perturbation. Each call inherits its predecessor's checkpoints. Restore `ITER` to `1\n3\n`, then `2\n3\n`, then `3\n3\n`; the program rewrites it to one line on exit. A single command is not the whole test. The helper handles this protocol in fresh per-call directories and refuses output reuse. It removes inherited restart products only in the new copy so they cannot falsely pass the next call's output gate.

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

Use at most four model threads and 24 GiB requested memory; keep at least 1 GiB disk reserve under the helper's 10 GiB project ceiling. The successful case peaked near 4.66 GiB and used about 320 seconds for the nine final calls. `OMP_STACKSIZE` covers worker stacks; it does not replace `ulimit -s unlimited` for the main thread. Runtime limits are 1,800 seconds per call and 10,800 seconds for this helper invocation; retries require reviewing existing receipts and the cumulative project budget, not deleting the previous output directory.

## 6. Read and check the outputs

| Output | Interpretation / check |
|---|---|
| `run-status.json` | Nine terminal calls; require exit zero **and** native finish marker, current cost file and newly written end restart |
| `step_*/iteration_3/diagadj/gctm.fd.*.01/.02/.03` | Baseline/plus/minus terminal states, BPCH `IJ-CHK-$`, `kg/box`, 72×46×47; compare surface layer |
| `step_*/iteration_3/OptData/gctm.gdt.01` | Baseline adjoint, `IJ-GDT-$`; select the control tracer's field and surface layer |
| `OptData/cfn.01/.02/.03` | Native cost records; useful alongside, not a substitute for state-field and derivative checks |
| `restart.output.component.2026102606` | End state; verify time, 43 tracer IDs, shape, units and finite values independently |
| `gradient-check.json` | Centered FD versus baseline adjoint, common cell support, nonzero finite norms and local exception counts |

The demonstration's global relative L2 errors were **1.4639%, 2.6269%, 6.2708%** for h=0.1,0.03,0.01. It met the predeclared criterion of two neighboring steps ≤5%. The smallest step failed; 829/830/895 of 3,312 surface cells had |FD|>1 and local relative error >5%. Do not describe every cell, arbitrary control or the complete adjoint as validated. The native aerosol-feedback-adjoint warning remains unresolved.

## 7. Change one factor and repeat its checks

| Goal | Change | What must be checked again |
|---|---|---|
| Different initial species | `control_tracer`, e.g. `4=CO` | Matching initial metadata, control scaling and a fresh derivative check; the default NOx result does not transfer |
| Different response | `response_tracer`, e.g. `26=SO2` | Objective table and NFD agree, correct mass units and nonzero derivative; CSV compatibility columns retain historical `*_Ox_kg` names |
| Different date | Both UTC settings and compatible met/initial state | Complete I3 interval, means, radiation climatology assumptions and output time; input conversion labels artificial initial states |
| Different perturbations | Three descending `fd_steps` | Predeclare values/tolerance before looking at results; inspect cancellation and truncation instead of tuning to pass |
| Different output statistic/region | Native objective and mask settings, in a separately prepared case | Objective weights, units, parser semantics and matching checker need adaptation; IFD/JFD alone are insufficient |
| Emission response, transport or full inversion | New model/process/input design | Outside this component profile; do not just turn an excluded flag on |

See the [method](../../../../../methods/03_atmospheric_transport/geos_chem.md) for derivatives, perturbation meaning and scientific acceptance. Keep the latest successful case and its inputs accessible; consolidate inactive history with a verified recovery index rather than teaching every failed attempt.
