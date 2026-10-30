"""Fixed R launch protocol for reviewed model-analysis adapters."""

from __future__ import annotations

import os
from pathlib import Path
import platform

from .tool_execution_paths import checked_path, ToolExecutionError


R_ADAPTERS = {"gcam_inspect", "gcam_plot", "mlr3_regression"}
# No task value is interpolated into R source. Rscript forwards trailing values
# to commandArgs(TRUE) itself. Namespace checks precede source.
R_GUARD = (
    'packages <- strsplit(Sys.getenv("AIRMOSAIC_R_PACKAGES"), ",", fixed=TRUE)[[1]]; '
    'available <- tryCatch(all(vapply(packages, requireNamespace, logical(1), quietly=TRUE)), '
    'error=function(e) FALSE); '
    'if (!available) quit(save="no", status=70L); '
    'status <- tryCatch({source(Sys.getenv("AIRMOSAIC_R_ENTRYPOINT"), echo=FALSE); 0L}, '
    'error=function(e) 71L); '
    'quit(save="no", status=status)'
)

OUTPUTS = {
    "gcam_inspect": tuple("inspect_" + name + ".csv" for name in (
        "scenarios", "province_top_level", "industrial_sector_tree", "industrial_cost_nodes")),
    "gcam_plot": ("sector_change_2021_2035.png", "sector_change_weighted_mean.csv"),
}


def r_executable() -> Path | None:
    """Local native Rscript only; never implicit CWD or shell launcher lookup."""
    for value in os.environ.get("PATH", "").split(os.pathsep):
        if not value.strip():
            continue
        try:
            candidate = checked_path(str(checked_path(value.strip('"')) /
                                         ("Rscript.exe" if os.name == "nt" else "Rscript")))
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        except (OSError, ValueError):
            continue
    return None


def command(entry: dict, parameters: dict, executable: Path) -> list[str]:
    argv = [str(executable), "--vanilla", "-e", R_GUARD]
    for name, value in parameters.items():
        binding = entry["argument_bindings"][name]
        if binding == "env:UNIT_PRICE_OUT_DIR":
            continue
        argv.extend([binding + str(value)] if binding.endswith("=") else [binding, str(value)])
    return argv


def environment(env: dict, entry: Path, packages: list[str], temp: Path,
                output: str | None, library: Path | None = None) -> dict:
    env.update(AIRMOSAIC_R_ENTRYPOINT=str(entry), AIRMOSAIC_R_PACKAGES=",".join(packages))
    if os.name == "nt":
        # R native libraries need this OS metadata during teardown on Windows.
        # Never broaden inheritance to the caller's whole environment.
        arch = os.environ.get("PROCESSOR_ARCHITECTURE", platform.machine()).upper()
        if arch in {"AMD64", "ARM64", "X86"}:
            env["PROCESSOR_ARCHITECTURE"] = arch
    # --vanilla skips profiles/Renviron. Explicit overrides also prevent R's
    # default personal and site library paths from reaching unrelated state.
    for key in ("R_LIBS", "R_LIBS_USER", "R_LIBS_SITE"):
        env[key] = str(library if library is not None else temp / "r-library")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "R_RANGER_NUM_THREADS"):
        env[key] = "1"
    if output is not None:
        env["UNIT_PRICE_OUT_DIR"] = output
    return env


def outputs_complete(adapter: str, output: Path) -> bool:
    if adapter == "mlr3_regression":
        from .mlr3_workflow import validate_outputs
        return validate_outputs(output)
    try:
        return all((path := checked_path(str(output / name))).is_file() and path.stat().st_size > 0
                   for name in OUTPUTS[adapter])
    except (OSError, ToolExecutionError):
        return False
