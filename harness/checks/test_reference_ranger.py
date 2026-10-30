"""Synthetic recovery checks; never load historical or real-data models."""
from pathlib import Path
import os
import subprocess
from types import SimpleNamespace

import pytest

from runtime.services import tool_r
from runtime.services.tool_process import child_environment

REPO = Path(__file__).resolve().parents[2]


def test_saved_forest_recovery_handles_numeric_null_vocab_and_categories(tmp_path):
    executable = tool_r.r_executable()
    library = os.environ.get("AIRMOSAIC_R_LIBRARY")
    if executable is None or not library:
        pytest.skip("Explicit R runtime unavailable")
    temp = tmp_path / "temp"
    temp.mkdir()
    entry = temp / "recover.R"
    entry.write_text('''library(ranger)
source(Sys.getenv("AIRMOSAIC_REFERENCE_RANGER"),local=TRUE)
set.seed(4)
d <- data.frame(x=1:60,category=factor(rep(c("a","b","c"),20)),y=sin(1:60)+1:60)
m <- ranger(y~.,data=d,num.trees=8,num.threads=1,seed=3)
wrapped <- list(model=m)
expected <- predict(m,data=d,num.threads=1)$predictions
stopifnot(identical(reference_ranger_predict(reference_ranger_model(wrapped),d),as.numeric(expected)))
stopifnot(identical(reference_ranger_predict(reference_ranger_model(m),d),as.numeric(expected)))
info <- reference_ranger_metadata(m)
stopifnot(!info$training_performed,is.null(info$call),is.null(info$environment))
bad <- d;bad$category<-"unknown"
stopifnot(inherits(try(reference_ranger_predict(m,bad),silent=TRUE),"try-error"))
bad <- d;bad$x[1]<-NA_real_
stopifnot(inherits(try(reference_ranger_predict(m,bad),silent=TRUE),"try-error"))
stopifnot(inherits(try(reference_ranger_model(list(model=list())),silent=TRUE),"try-error"))
''', encoding="utf-8")
    env = tool_r.environment(child_environment(SimpleNamespace(assets=tmp_path, output=tmp_path, temp=temp), None),
                             entry, ["ranger"], temp, None, Path(library))
    env["AIRMOSAIC_REFERENCE_RANGER"] = str(REPO / "skills/model/shared/model_reproduction/scripts/reference_ranger.R")
    result = subprocess.run([str(executable), "--vanilla", "-e", tool_r.R_GUARD],
                            env=env, cwd=temp, capture_output=True, timeout=60)
    assert result.returncode == 0, "Synthetic saved-forest recovery failed"
