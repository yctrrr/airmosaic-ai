"""Bounded, explicit-contract ecCodes reader; no discovery or resampling."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


def read_regular_grib(paths, contracts, *, requested_fields=None,
                      max_messages=100000, max_cells=100000000,
                      duplicate_policy="error"):
    """Return native regular_ll fields as [UTC time, y, x] float64 cubes.

    Each contract requires param_id, short_name, units, type_of_level and level;
    optional centre restricts the originating centre. All messages must match
    exactly one contract, even when requested_fields excludes their values.
    Missing field/time combinations and bitmap/nonfinite values become NaN.
    max_cells bounds both selected input values and the final dense allocation
    (not total process memory). No source paths appear in returned metadata.
    duplicate_policy='identical' skips repeated variable/time only when SHA256
    of the entire original encoded message matches; default 'error' rejects all.
    """
    import eccodes as ec

    def refuse(reason):
        raise ValueError("grib_grid_" + reason)

    if duplicate_policy not in ("error", "identical"):
        refuse("invalid_duplicate_policy")
    if (not isinstance(paths, (list, tuple)) or not paths
            or any(not isinstance(p, (str, Path)) or "://" in str(p) for p in paths)):
        refuse("requires_explicit_local_paths")
    if any(not isinstance(n, int) or isinstance(n, bool) or n <= 0
           for n in (max_messages, max_cells)):
        refuse("invalid_limits")
    required = {"param_id", "short_name", "units", "type_of_level", "level"}
    if not isinstance(contracts, dict) or not contracts:
        refuse("invalid_contracts")
    for name, contract in contracts.items():
        if (not isinstance(name, str) or not name.isidentifier()
                or not isinstance(contract, dict) or not required <= contract.keys()
                or contract.keys() - (required | {"centre"})
                or not isinstance(contract["param_id"], int)
                or isinstance(contract["param_id"], bool)
                or not isinstance(contract["level"], (int, float))
                or not np.isfinite(contract["level"])
                or any(not isinstance(contract[k], str) or not contract[k]
                       for k in ("short_name", "units", "type_of_level"))):
            refuse("invalid_contracts")
    selected = list(contracts) if requested_fields is None else list(requested_fields)
    if (not selected or any(not isinstance(n, str) for n in selected)
            or len(set(selected)) != len(selected) or set(selected) - contracts.keys()):
        refuse("invalid_requested_fields")
    frames = {name: {} for name in selected}
    counts = dict.fromkeys(contracts, 0)
    missing = dict.fromkeys(selected, 0)
    seen = {}
    x = y = earth = None
    total = loaded = cells = skipped_duplicates = 0
    try:
        for path in paths:
            with open(path, "rb") as stream:
                while True:
                    handle = ec.codes_grib_new_from_file(stream)
                    if handle is None:
                        break
                    try:
                        total += 1
                        if total > max_messages:
                            refuse("message_limit")
                        # Capture original encoded bytes before querying derived keys.
                        digest = (hashlib.sha256(ec.codes_get_message(handle)).digest()
                                  if duplicate_policy == "identical" else None)
                        get = lambda key: ec.codes_get(handle, key)
                        candidates = [name for name, c in contracts.items()
                                      if get("paramId") == c["param_id"]
                                      and get("shortName") == c["short_name"]
                                      and get("typeOfLevel") == c["type_of_level"]
                                      and get("level") == c["level"]
                                      and ("centre" not in c or get("centre") == c["centre"])]
                        if len(candidates) != 1:
                            refuse("unknown_or_ambiguous_identity")
                        name = candidates[0]
                        if get("units") != contracts[name]["units"]:
                            refuse("units_mismatch")
                        if (get("dataType") != "an" or get("stepType") != "instant" or get("startStep") != 0
                                or get("endStep") != 0):
                            refuse("unsupported_forecast_or_statistic")
                        date, clock = int(get("dataDate")), int(get("dataTime"))
                        valid_date, valid_clock = int(get("validityDate")), int(get("validityTime"))
                        if (date, clock) != (valid_date, valid_clock):
                            refuse("valid_time_mismatch")
                        try:
                            time = datetime.strptime(f"{date:08d}{clock:04d}", "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
                        except ValueError:
                            refuse("invalid_utc_time")
                        if (name, time) in seen:
                            if duplicate_policy == "error":
                                refuse("duplicate_variable_time")
                            if seen[(name, time)] != digest:
                                refuse("duplicate_message_conflict")
                            skipped_duplicates += 1
                            continue
                        seen[(name, time)] = digest
                        if (get("gridType") != "regular_ll" or get("jPointsAreConsecutive")
                                or get("alternativeRowScanning")):
                            refuse("unsupported_grid_or_scan")
                        nx, ny = int(get("Ni")), int(get("Nj"))
                        if nx < 2 or ny < 2 or nx * ny > max_cells:
                            refuse("grid_size_limit")
                        earth_now = {"shapeOfTheEarth": get("shapeOfTheEarth")}
                        for key in ("radius", "earthMajorAxis", "earthMinorAxis"):
                            if ec.codes_is_defined(handle, key):
                                earth_now[key] = get(key)
                        lons = np.asarray(ec.codes_get_array(handle, "longitudes")).reshape(ny, nx)
                        lats = np.asarray(ec.codes_get_array(handle, "latitudes")).reshape(ny, nx)
                        xx, yy = lons[0].copy(), lats[:, 0].copy()
                        def regular(axis):
                            delta = np.diff(axis)
                            return (np.isfinite(axis).all() and (np.all(delta > 0) or np.all(delta < 0))
                                    and np.allclose(delta, delta[0], rtol=1e-8, atol=1e-8))
                        if (not regular(xx) or not regular(yy)
                                or not np.allclose(lons, xx[None, :], rtol=0, atol=1e-8)
                                or not np.allclose(lats, yy[:, None], rtol=0, atol=1e-8)
                                or np.any(np.abs(yy) > 90)):
                            refuse("nonrectangular_coordinates")
                        if x is None:
                            x, y = xx, yy
                            earth = earth_now
                        elif (x.shape != xx.shape or y.shape != yy.shape
                              or earth != earth_now
                              or not np.allclose(x, xx, rtol=0, atol=1e-8)
                              or not np.allclose(y, yy, rtol=0, atol=1e-8)):
                            refuse("grid_mismatch")
                        counts[name] += 1
                        if name not in frames:
                            continue
                        cells += nx * ny
                        if cells > max_cells:
                            refuse("cell_limit")
                        values = np.asarray(ec.codes_get_values(handle), dtype=float).reshape(ny, nx).copy()
                        if get("bitmapPresent"):
                            bitmap = np.asarray(ec.codes_get_array(handle, "bitmap")).reshape(ny, nx)
                            values[bitmap == 0] = np.nan
                        values[~np.isfinite(values)] = np.nan
                        missing[name] += int(np.isnan(values).sum())
                        frames[name][time] = values
                        loaded += 1
                    finally:
                        ec.codes_release(handle)
    except ValueError as exc:
        if str(exc).startswith("grib_grid_"):
            raise
        raise ValueError("grib_grid_decode_failed") from None
    except Exception:
        raise ValueError("grib_grid_decode_failed") from None
    if not total or any(not frames[name] for name in selected):
        refuse("empty_requested_field")
    times = sorted({t for field in frames.values() for t in field})
    if len(times) * len(x) * len(y) * len(selected) > max_cells:
        refuse("dense_cell_limit")
    fields = {}
    absent = {}
    for name, rows in frames.items():
        cube = np.full((len(times), len(y), len(x)), np.nan)
        for i, time in enumerate(times):
            if time in rows:
                cube[i] = rows.pop(time)
        fields[name] = cube
        absent[name] = len(times) - counts[name]
    return {"x": x, "y": y, "times_utc": pd.DatetimeIndex(times), "fields": fields,
            "metadata": {"message_count": total, "decoded_message_count": loaded,
                         "duplicate_policy": duplicate_policy,
                         "skipped_duplicate_count": skipped_duplicates,
                         "field_message_counts": counts, "missing_value_counts": missing,
                         "absent_time_counts": absent, "grid_type": "regular_ll",
                         "crs": "native_grib_geographic", "earth_geometry": earth,
                         "eccodes_version": ec.codes_get_api_version(),
                         "coordinate_order": "native",
                         "identities": {name: dict(contracts[name]) for name in contracts},
                         "units": {name: contracts[name]["units"] for name in selected}}}
