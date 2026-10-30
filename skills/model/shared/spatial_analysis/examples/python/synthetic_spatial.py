"""Offline, synthetic counterpart to the R route; no business data or geocoding."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyproj import network
from shapely.geometry import Point, box

repo = Path(__file__).resolve().parents[6]
path = repo / "skills/model/shared/spatial_analysis/scripts/python/spatial_helpers.py"
spec = importlib.util.spec_from_file_location("spatial_helpers", path)
spatial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spatial)
network.set_network_enabled(False)
areas = gpd.GeoDataFrame({"area_id": ["A", "B"], "value": [1, 2]},
    geometry=[box(500000, 0, 501000, 1000), box(501000, 0, 502000, 1000)], crs=32631)
points = gpd.GeoDataFrame({"sample_id": ["inside", "boundary", "outside"], "value": [1, 2, 3]},
    geometry=[Point(500500, 500), Point(501000, 500), Point(503000, 500)], crs=32631)
matches = spatial.point_polygon_matches(points, areas, "sample_id", "area_id")
assert matches.n_matches.tolist() == [1, 2, 0]
assert matches.match_status.tolist() == ["matched", "ambiguous", "unmatched"]
assert matches.candidate_ids.tolist() == [["A"], ["A", "B"], []]
strict = spatial.point_polygon_matches(points, areas, "sample_id", "area_id", "within")
assert strict.n_matches.tolist() == [1, 0, 0]
back = spatial.transform_gdf(spatial.transform_gdf(points, 4326), 32631)
assert np.max(points.geometry.distance(back.geometry)) < 0.001
grid = pd.DataFrame({"x": [500500, 501500], "y": [500, 500], "value": [1, 2]})
facets = pd.concat([grid.assign(scenario="baseline"), grid.assign(scenario="comparison", value=[2, 3])])
plots = {
    "polygons": spatial.plot_polygons(areas, "value", "Synthetic index (1)", limits=(0, 3)),
    "points": spatial.plot_points(points, "value", "Synthetic index (1)", limits=(0, 3)),
    "grid": spatial.grid_plot(grid, "x", "y", "value", "Synthetic index (1)", 32631, 1000, 1000),
    "facets": spatial.grid_facet_plot(facets, "x", "y", "value", "Synthetic index (1)",
                                      32631, 1000, 1000, "scenario", limits=(0, 3)),
}
def refuses(call):
    try:
        call()
    except ValueError:
        return True
    return False
assert refuses(lambda: spatial.point_polygon_matches(points.to_crs(4326), areas, "sample_id", "area_id"))
assert refuses(lambda: spatial.plot_polygons(areas, "value", "Synthetic index (1)", limits=(0, 1)))
assert refuses(lambda: spatial.grid_plot(pd.concat([grid, grid.iloc[:1]]), "x", "y", "value",
                                         "Synthetic index (1)", 32631, 1000, 1000))
assert refuses(lambda: spatial.point_polygon_matches(
    points.set_crs(None, allow_override=True), areas, "sample_id", "area_id"))
assert refuses(lambda: spatial.point_polygon_matches(
    points.assign(sample_id=["same", "same", "other"]), areas, "sample_id", "area_id"))
assert refuses(lambda: spatial.point_polygon_matches(
    spatial.transform_gdf(points, 4326), spatial.transform_gdf(areas, 4326), "sample_id", "area_id"))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out-dir", type=Path)
args = parser.parse_args()
for fig, _ in plots.values():
    fig.canvas.draw()
if args.out_dir:
    if not args.out_dir.is_dir() or any((args.out_dir / f"{name}.png").exists() for name in plots):
        raise ValueError("fresh_existing_output_directory_required")
    for name, (fig, _) in plots.items():
        fig.savefig(args.out_dir / f"{name}.png", dpi=120)
for fig, _ in plots.values():
    plt.close(fig)
print(json.dumps({"matched_counts": matches.n_matches.tolist(), "plot_builds": 4,
                  "refusal_checks": 6, "synthetic_only": True, "geocoding_requests": 0}))
