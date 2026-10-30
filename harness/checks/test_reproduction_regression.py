"""Synthetic-only bounded reproduction library and project delegation checks."""
import os
from pathlib import Path
import shutil
import subprocess

import pytest

REPO = Path(__file__).resolve().parents[2]
LIB = REPO / "skills/model/shared/machine_learning_model/scripts/r"
PROJECT = REPO / "projects/0001_ozone_environmental_drivers"


def run_r(code, tmp_path, extra=None):
    executable = shutil.which("Rscript")
    if executable is None:
        pytest.skip("Rscript unavailable")
    env = dict(os.environ)
    library = env.get("AIRMOSAIC_R_LIBRARY", str(REPO / ".missing-test-r-library"))
    for name in ("R_LIBS", "R_LIBS_USER", "R_LIBS_SITE"):
        env[name] = library
    env.update(AIRMOSAIC_SKILL_IO=str(LIB / "common/io.R"),
               AIRMOSAIC_REPRODUCTION_LIB=str(LIB / "models/reproduction.R"))
    env.update(extra or {})
    check = subprocess.run([executable, "--vanilla", "-e",
        'quit(status=if(all(vapply(c("mlr3","mlr3learners","ranger","jsonlite"), requireNamespace, logical(1), quietly=TRUE))) 0L else 1L)'],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    if check.returncode:
        pytest.skip("Packages unavailable in explicit R library")
    entry = tmp_path / "synthetic.R"
    entry.write_text(code, encoding="utf-8")
    result = subprocess.run([executable, "--vanilla", str(entry)], cwd=tmp_path,
                            env=env, capture_output=True, timeout=120)
    assert result.returncode == 0, result.stderr.decode(errors="replace")


def test_generic_cv_determinism_leakage_and_boundaries(tmp_path):
    run_r('''
source(Sys.getenv("AIRMOSAIC_SKILL_IO"))
source(Sys.getenv("AIRMOSAIC_REPRODUCTION_LIB"))
suppressPackageStartupMessages(library(mlr3learners))
set.seed(23)
d <- data.frame(x = seq_len(60), category = factor(rep(c("low", "high"), 30)),
                response = seq_len(60) * 0.2 + rnorm(60))
fold <- rep(1:3, each = 20)
cfg <- list(target = "response", folds = 3L, num_trees = 8L, candidate_count = 2L,
            seed = 301L, min_node_sizes = list(1L, 3L), sample_fractions = list(0.8, 1),
            replace = TRUE, respect_unordered_factors = "partition")
features <- c("x", "category")
a <- reproduction_search_forest(d, features, fold, cfg, 1L, "category")
b <- reproduction_search_forest(d, features, fold, cfg, 1L, "category")
stopifnot(identical(a, b), nrow(a$comparison) == 2, nrow(a$fold_scores) == 6,
          all(is.finite(a$response)))
# Each first candidate's fold prediction is unaffected by that fold's outcomes.
# Selection itself uses all validation outcomes; compare candidate fits, not winners.
set.seed(cfg$seed + 101L)
grid <- expand.grid(mtry=seq_along(features), min.node.size=unlist(cfg$min_node_sizes),
                    sample.fraction=unlist(cfg$sample_fractions), KEEP.OUT.ATTRS=FALSE)
grid <- grid[sample.int(nrow(grid), cfg$candidate_count), , drop=FALSE]
changed <- d
changed$response[fold == 1] <- 999999
fit <- function(frame) reproduction_forest(frame[fold != 1, ], features, "response",
                as.list(grid[1, ]), cfg, cfg$seed + 1001L, "category")
stopifnot(identical(fit(d)$predict_newdata(d[fold == 1, features])$response,
                    fit(changed)$predict_newdata(changed[fold == 1, features])$response))
# Arbitrary categorical names and entirely numeric configurations are supported.
numeric_result <- reproduction_search_forest(d, "x", fold, cfg, 1L)
stopifnot(length(numeric_result$response) == 60L)
reject <- function(expr) stopifnot(inherits(try(force(expr), silent=TRUE), "try-error"))
reject(reproduction_search_forest(d, c("x", "response"), fold, cfg, 1L))
reject(reproduction_search_forest(d, c("x", "x"), fold, cfg, 1L))
reject(reproduction_search_forest(d, "missing", fold, cfg, 1L))
reject(reproduction_search_forest(d, features, fold[-1], cfg, 1L, "category"))
reject(reproduction_search_forest(d, features, rep(1, 60), cfg, 1L, "category"))
reject(reproduction_search_forest(d, features, fold + 0.1, cfg, 1L, "category"))
bad <- cfg; bad$candidate_count <- 21L
reject(reproduction_search_forest(d, features, fold, bad, 1L, "category"))
bad <- cfg; bad$num_trees <- 1001L
reject(reproduction_search_forest(d, features, fold, bad, 1L, "category"))
bad <- cfg; bad$sample_fractions <- list(0.01)
reject(reproduction_search_forest(d, features, fold, bad, 1L, "category"))
reject(reproduction_forest(d, features, "response", list(mtry=3, min.node.size=1,
                          sample.fraction=1), cfg, 1L, "category"))
unseen <- d; unseen$category <- as.character(unseen$category)
unseen$category[fold == 1] <- "held_out_only"
reject(reproduction_search_forest(unseen, features, fold, cfg, 1L, "category"))
''', tmp_path)


def test_project_synthetic_self_test_uses_shared_library(tmp_path):
    run_r('''source(file.path(dirname(Sys.getenv("AIRMOSAIC_R_ENTRYPOINT")), "prediction_checks.R"))''',
          tmp_path, {"AIRMOSAIC_R_ENTRYPOINT": str(PROJECT / "prediction_checks.R")})


@pytest.mark.parametrize("failure", ["verification", "source_mutation", "code_mutation", "seal", "existing_terminal", "success"])
def test_successful_child_records_postprocessing_outcome(tmp_path, monkeypatch, failure):
    """Exercise the complete launcher on private synthetic files and a mocked child."""
    import csv
    import importlib.util
    import json
    import sys

    spec = importlib.util.spec_from_file_location("synthetic_paper_launcher", PROJECT / "run_prediction.py")
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    fake_repo = tmp_path / "repository"
    here = fake_repo / "project"
    here.mkdir(parents=True)
    for name in ("prediction.R", "prediction_checks.R", "run_prediction.py", "prediction.json", "prediction_prompt.md", "prediction_prompt_ZH.md"):
        (here / name).write_text("synthetic source", encoding="utf-8")
    for relative in ("skills/model/shared/machine_learning_model/scripts/r/common/io.R",
                     "skills/model/shared/machine_learning_model/scripts/r/models/reproduction.R",
                     "skills/model/shared/machine_learning_model/SKILL.md", "skills/model/shared/machine_learning_model/frameworks/r/mlr3/SKILL.md"):
        path = fake_repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic shared source", encoding="utf-8")
    roots = {key: tmp_path / folder for key, folder in (
        ("AIRMOSAIC_ASSETS_DIR", "assets"), ("AIRMOSAIC_CONFIG_DIR", "config"),
        ("AIRMOSAIC_AUTH_DIR", "auth"))}
    for path in roots.values():
        path.mkdir()
    data = roots["AIRMOSAIC_ASSETS_DIR"] / "data"
    data.mkdir()
    source = data / "input.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    dictionary = data / "dictionary.csv"
    with dictionary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["column_name", "unit"])
        writer.writeheader()
        writer.writerows([{"column_name": "x", "unit": "u"}, {"column_name": "y", "unit": "u"}])
    cfg = {"input": "data/input.csv", "dictionary": "data/dictionary.csv",
           "input_sha256": launcher.digest(source), "dictionary_sha256": launcher.digest(dictionary),
           "target": "y", "target_unit": "u", "feature_sets": {"model_1": ["x"]},
           "project_id": "synthetic_receipt", "experiment_id": "synthetic_receipt", "folds": 2,
           "candidate_count": 1}
    library = tmp_path / "library"
    library.mkdir()
    monkeypatch.setenv("AIRMOSAIC_R_LIBRARY", str(library))
    monkeypatch.setattr(launcher, "HERE", here)
    monkeypatch.setattr(launcher, "REPO", fake_repo)
    monkeypatch.setattr(launcher, "load_protocol", lambda: cfg)
    monkeypatch.setattr(launcher, "separated_roots", lambda repo: roots)
    monkeypatch.setattr(launcher, "_inside_git", lambda path: False)
    monkeypatch.setattr(launcher.tool_r, "r_executable", lambda: Path("synthetic_Rscript"))
    monkeypatch.setattr(launcher.tool_r, "environment", lambda *args: {})
    monkeypatch.setattr(launcher, "child_environment", lambda *args: {})
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_receipt/receipt_failure"

    def successful_child(*args):
        assert Path(args[2]["AIRMOSAIC_REPRODUCTION_LIB"]) == output / "source_snapshot/reproduction.R"
        (output / "synthetic-result.txt").write_text("preserved result", encoding="utf-8")
        if failure == "source_mutation":
            source.write_text("x,y\n1,999\n", encoding="utf-8")
        if failure == "code_mutation":
            (here / "prediction.R").write_text("changed synthetic source", encoding="utf-8")
        if failure == "existing_terminal":
            (output / "execution.json").write_text('{"status":"external_receipt"}', encoding="utf-8")
        return 0, "completed", False, b"EXPERIMENT completed\n"

    monkeypatch.setattr(launcher, "execute", successful_child)

    def verify(*args):
        if failure == "verification":
            raise ValueError("private source path must never enter receipt")
        return {"status": "passed", "independent_metrics": {}}

    monkeypatch.setattr(launcher, "verify_output", verify)
    original_write = launcher.write_json

    def write_json(path, value):
        if failure == "seal" and path.name == "artifact-sha256.json":
            raise OSError("private filesystem diagnostic")
        return original_write(path, value)

    monkeypatch.setattr(launcher, "write_json", write_json)
    monkeypatch.setattr(sys, "argv", ["run_prediction.py", "--batch-id", "receipt_failure", "--execute"])
    expected = {"verification": "output_verification_failed", "source_mutation": "source_integrity_failed",
                "code_mutation": "source_integrity_failed", "seal": "artifact_sealing_failed",
                "existing_terminal": "terminal_receipt_failed", "success": None}[failure]
    if failure == "success":
        launcher.main()
    else:
        with pytest.raises(ValueError, match=expected):
            launcher.main()
    start = json.loads((output / "execution-start.json").read_text(encoding="utf-8"))
    terminal_text = (output / "execution.json").read_text(encoding="utf-8")
    terminal = json.loads(terminal_text)
    assert start["status"] == "running"
    assert (output / "synthetic-result.txt").read_text(encoding="utf-8") == "preserved result"
    assert "private" not in terminal_text
    if failure == "success":
        assert terminal["status"] == "completed"
        manifest = json.loads((output / "artifact-sha256.json").read_text(encoding="utf-8"))
        assert manifest["execution.json"] == launcher.digest(output / "execution.json")
        assert all(launcher.digest(output / name) == value for name, value in manifest.items())
    elif failure == "existing_terminal":
        assert terminal == {"status": "external_receipt"}
    else:
        assert terminal["status"] == "failed"
        assert terminal["error"] == expected
        assert terminal["return_code"] == 0
        assert terminal["finished_at"]
