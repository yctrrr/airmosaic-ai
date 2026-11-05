# Native GRIB regular-grid reader

**English** | [中文](grib-grid_ZH.md)

[grib_grid.py](../scripts/python/grib_grid.py) is a direct Python helper using installed `eccodes`, NumPy and pandas. It has no runner adapter, registry ID, configuration loader, directory search, network access or output writer. Importing the module does not open input files. Call it only with an authorized explicit local file list and reviewed variable contracts.

```python
import importlib.util
from pathlib import Path

module_path = Path("skills/model/shared/spatial_analysis/scripts/python/grib_grid.py")
spec = importlib.util.spec_from_file_location("grib_grid", module_path)
grib_grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grib_grid)

# paths is an explicitly supplied list of authorized local GRIB files.
# These identities describe ecCodes' ECMWF GRIB1 surface samples, not every
# edition/product. Validate the actual source's level contract before use.
identities = {
    "t2m": (167, "2t", "K"), "d2m": (168, "2d", "K"),
    "u10": (165, "10u", "m s**-1"), "v10": (166, "10v", "m s**-1"),
    "sp": (134, "sp", "Pa"), "aod550": (210207, "aod550", "~"),
}
contracts = {
    name: dict(param_id=p, short_name=s, units=u, type_of_level="surface",
               level=0, centre="ecmf")
    for name, (p, s, u) in identities.items()
}
result = grib_grid.read_regular_grib(
    paths, contracts, requested_fields=["t2m"],
    max_messages=100000, max_cells=8_000_000,
)
```

`read_regular_grib(paths, contracts, *, requested_fields=None, max_messages=100000, max_cells=100000000, duplicate_policy="error")` returns `x`, `y`, sorted timezone-aware UTC `times_utc`, `fields` mapping names to float64 `[time,y,x]` cubes, and bounded `metadata`. Every encountered message must match exactly one declared identity (parameter ID, short name, level type/value, optional centre), including unselected variables; units must match exactly. No conversion or implicit GRIB1 `heightAboveGround=2` assumption is made. Unknown/ambiguous identities, changed coordinates/earth geometry, unsupported scans and non-analysis or noninstantaneous/nonzero-step fields are refused.

The default `duplicate_policy="error"` rejects every duplicate `(variable, valid_time)`. Explicit `duplicate_policy="identical"` skips a duplicate only when SHA256 of the entire original encoded GRIB message matches the first message for that key. Equal decoded values with different encoding or metadata are refused with `grib_grid_duplicate_message_conflict`; nothing is averaged or overwritten. The same check applies to unselected fields and across supplied files. Metadata records `duplicate_policy` and total `skipped_duplicate_count`. `message_count` and `max_messages` include every encountered message; `field_message_counts`, `decoded_message_count`, missing-value counts and cell limits retain unique accepted-message semantics. Source files are unchanged; no message hashes or source paths are emitted.

Only rectangular `regular_ll` grids with at least two points on each monotonic, regularly spaced axis are supported. Row-major scanning is required; consecutive-j and alternating rows are refused. Coordinates and latitude direction are preserved. A longitude wrap that makes the native axis nonmonotonic is refused. There is no reprojection, axis reordering, interpolation or station-coordinate validation. Metadata records the source earth shape/radius/axes as available and labels CRS `native_grib_geographic`; reading angular coordinates does not establish WGS84 datum equivalence.

UTC valid date/time must equal the analysis reference date/time. The returned time union includes selected fields only. Absent variable/time combinations become NaN, with `absent_time_counts`; bitmap missing and nonfinite decoded values become NaN, with `missing_value_counts` counting decoded missing cells only. This does not certify expected-year completeness, cadence, local days, collection membership or station assumptions: check those explicitly downstream before daily aggregation/sampling.

`requested_fields` validates every supplied message but decodes value arrays only for selected variables. Meteorology and AOD may use separate explicit lists/calls; the reader does not discover collections. To bound annual memory, read one variable per call. `max_cells` limits selected input cells and the final dense union allocation, not total process memory; temporary decoded coordinates, message storage and output arrays add overhead. Eight million output float64 cells occupy about 64 MB. Metadata has per-contract counts/identities, ecCodes version and grid facts, without file paths or per-message logs. Errors expose fixed reason codes without source paths; direct callers still own authorization and storage boundaries.

From repository root, run actual ecCodes sample-based synthetic tests:

```sh
python -m pytest harness/checks/test_grib_grid_reader.py -q
```

Tests create GRIB messages under pytest temporary directories and check native affine planes, UTC sorting, all six example identities, variable selection, missingness and rejection boundaries. Duplicate tests check default refusal, explicit byte-identical acceptance, value/metadata/encoding conflicts, unselected fields and the all-message budget. Synthetic decoding does not establish real-source integration or scientific acceptance.
