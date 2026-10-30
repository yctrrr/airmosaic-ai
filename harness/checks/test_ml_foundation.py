"""DAG identification, cross-fitting, training-only selection and flexible outputs."""

from copy import deepcopy
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from runtime.services import ToolRunnerService, ToolRegistryService, ToolExecutionError
from runtime.services.causal_dag import DAGError, check_adjustment
from runtime.services.mlr3_workflow import output_path, validate_configuration
from runtime.services.ml_execution_paths import MLExecutionPaths, SKILL_RESULTS
from test_ml_regression_workflow import configuration, require_r_packages, task, execute_task, REPO, TOOL


FORK = {"nodes": ["x", "d", "y"], "edges": [["x", "d"], ["x", "y"], ["d", "y"]]}


def test_backdoor_confounder_must_be_adjusted():
    assert check_adjustment(FORK, "d", "y", ["x"])["acyclic"]
    with pytest.raises(DAGError, match="open_backdoor"):
        check_adjustment(FORK, "d", "y", [])


def test_mediator_is_not_a_total_effect_adjustment_variable():
    dag = {"nodes": ["d", "m", "y"], "edges": [["d", "m"], ["m", "y"]]}
    assert check_adjustment(dag, "d", "y", [])["causal_path_declared"]
    with pytest.raises(DAGError, match="descendant"):
        check_adjustment(dag, "d", "y", ["m"])


def test_conditioning_on_collider_or_descendant_opens_path():
    dag = {"nodes": ["d", "a", "b", "c", "z", "y"],
           "edges": [["a", "d"], ["a", "c"], ["b", "c"], ["b", "y"], ["c", "z"]]}
    assert check_adjustment(dag, "d", "y", [])["acyclic"]
    for adjustment in (["c"], ["z"]):
        with pytest.raises(DAGError, match="open_backdoor"):
            check_adjustment(dag, "d", "y", adjustment)


@pytest.mark.parametrize("dag", [
    {"nodes": ["d", "y"], "edges": [["d", "y"], ["y", "d"]]},
    {"nodes": ["d", "y"], "edges": [["d", "y"], ["d", "y"]]},
    {"nodes": ["d", "y"], "edges": [["d", "y"]], "latent": ["d"]},
    {"nodes": ["u", "d", "y"], "edges": [["u", "d"], ["u", "y"], ["d", "y"]], "latent": ["u"]},
])
def test_invalid_or_unidentified_graphs_are_not_accepted(dag):
    with pytest.raises(DAGError):
        check_adjustment(dag, "d", "y", [])


@pytest.mark.parametrize("paths", [
    {"metrics": "REPORT.json", "provenance": "report.json"},
    {"metrics": "stats.json", "provenance": "STATS.json/provenance.json"},
    {"model": "../model.rds"}, {"status": "auth/status.json"}, {"artifacts": "renamed.json"},
])
def test_artifact_aliases_and_traversal_are_rejected(paths):
    cfg = configuration(); cfg["output_files"] = paths
    with pytest.raises(ToolExecutionError):
        validate_configuration(cfg, REPO)


@pytest.mark.parametrize("marker_is_file", [False, True])
def test_artifact_subdirectory_rejects_nested_git_without_rejecting_owning_checkout(tmp_path, marker_is_file):
    checkout = tmp_path / "checkout"
    (checkout / ".git").mkdir(parents=True)
    output = checkout / "ignored_skill_results" / "trial"
    nested = output / "unrelated_checkout"
    nested.mkdir(parents=True)
    marker = nested / ".git"
    if marker_is_file:
        marker.write_text("gitdir: synthetic-metadata")
    else:
        marker.mkdir()
    assert output_path(output, "statistics/metrics.json") == output / "statistics/metrics.json"
    with pytest.raises(ToolExecutionError, match="nested_git_in_artifact_output"):
        output_path(output, "unrelated_checkout/statistics/metrics.json")


def test_preview_rejects_artifact_nested_checkout_before_creating_a_run(task):
    roots, source, cfg_file = task
    output = roots["AIRMOSAIC_ASSETS_DIR"] / "results/synthetic_regression/chosen_experiment"
    (output / "nested/.git").mkdir(parents=True)
    cfg = configuration()
    cfg["output_files"] = {"prepared_data": "nested/prepared.csv"}
    cfg_file.write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(ToolExecutionError, match="nested_git_in_artifact_output"):
        ToolRunnerService().run(TOOL, {"input_csv": str(source), "task_config": str(cfg_file), "out_dir": str(output)},
                                project_id="synthetic_regression", dry_run=True)
    assert not (output / "nested/prepared.csv").exists()
    assert not (output.parent / ".airmosaic").exists()


def test_training_filter_and_shapley_ice_contract(task):
    require_r_packages()
    _, source, cfg_file = task
    rows = list(csv.DictReader(source.open(newline="", encoding="utf-8")))
    for row in rows:
        row.update(duplicate=row["x"], constant=1)
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer=csv.DictWriter(handle, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    cfg=configuration(); cfg["features"]=["x","duplicate","constant","category"]
    cfg["feature_selection"]={"mode":"train_filter","max_abs_correlation":0.95}
    cfg["explanation"].update(methods=["permutation","pdp","ice","shap"],shap_rows=3,shap_permutations=4)
    cfg_file.write_text(json.dumps(cfg), encoding="utf-8")
    result, output=execute_task(task)
    assert result["status"]=="succeeded", result
    audit=list(csv.DictReader((output/"feature-selection.csv").open()))
    assert {row["feature"] for row in audit if row["retained"]=="TRUE"}=={"x","category"}
    pdp=list(csv.DictReader((output/"pdp.csv").open()))
    ice=list(csv.DictReader((output/"ice.csv").open()))
    for row in pdp:
        predictions=[float(item["prediction"]) for item in ice if item["feature"]==row["feature"] and item["value"]==row["value"]]
        assert sum(predictions)/len(predictions)==pytest.approx(float(row["mean_prediction"]))
    shap=list(csv.DictReader((output/"shap.csv").open()))
    for key in {row["sample_id"] for row in shap}:
        values=[row for row in shap if row["sample_id"]==key]
        assert sum(float(row["contribution"]) for row in values)+float(values[0]["baseline"])==pytest.approx(float(values[0]["prediction"]))


def causal_task(task):
    roots, source, cfg_file=task
    source.write_bytes((REPO/"assets/data/03_atmospheric_transport/SyntheticCausal/v1/rows.csv").read_bytes())
    cfg=json.loads((REPO/"config/examples/ml-regression/synthetic-causal.json").read_text())
    cfg_file.write_text(json.dumps(cfg),encoding="utf-8")
    return cfg


def test_cross_fitted_plr_recovers_known_slope_and_excludes_test(task):
    require_r_packages(); causal_task(task)
    result, first=execute_task(task)
    assert result["status"]=="succeeded",result
    effect=json.loads((first/"causal-effect.json").read_text())
    assert effect["coefficient"]==pytest.approx(2,abs=0.25)
    assert effect["confidence_interval_95"][0]<2<effect["confidence_interval_95"][1]
    assert effect["n"]==500 and effect["cross_fitted"]
    _, source, _=task
    rows=list(csv.DictReader(source.open(newline="",encoding="utf-8")))
    for row in rows:
        if row["dataset"]=="test": row["outcome"]=1000000
    with source.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    repeated, second=execute_task(task)
    assert repeated["status"]=="succeeded",repeated
    assert (first/"causal-effect.json").read_bytes()==(second/"causal-effect.json").read_bytes()
    residuals=list(csv.DictReader((first/"causal-residuals.csv").open()))
    assert len(residuals)==500 and {row["fold"] for row in residuals}=={"1","2","3"}


def test_numeric_group_keys_remain_in_one_fold(task):
    require_r_packages(); cfg=causal_task(task)
    cfg["features"].append("group_id"); cfg["causal"]["adjustment_set"].append("group_id")
    cfg["causal"]["dag"]["nodes"].append("group_id")
    cfg["causal"]["dag"]["edges"] += [["group_id","treatment"],["group_id","outcome"]]
    cfg["causal"]["resampling"]={"mode":"group","group_column":"group_id"}
    task[2].write_text(json.dumps(cfg),encoding="utf-8")
    result, output=execute_task(task)
    assert result["status"]=="succeeded",result
    folds=list(csv.DictReader((output/"causal-folds.csv").open()))
    for group in {row["group_id"] for row in folds}:
        assert len({row["fold"] for row in folds if row["group_id"]==group})==1
    effect=json.loads((output/"causal-effect.json").read_text())
    assert effect["clusters"]==30 and effect["variance_method"]=="independent_cluster_influence_score"


def test_causal_covariates_and_assumptions_are_not_automatically_selected(task):
    cfg=causal_task(task)
    for changed in ("feature_selection","assumption","mediator"):
        value=deepcopy(cfg)
        if changed=="feature_selection": value["feature_selection"]={"mode":"train_filter"}
        elif changed=="assumption": value["causal"]["assumptions"]["overlap"]=False
        else:
            value["causal"]["dag"]["edges"].append(["treatment","x1"])
        with pytest.raises(ToolExecutionError): validate_configuration(value,REPO)


def test_custom_project_artifacts_are_free_and_existing_files_are_preserved(task):
    require_r_packages(); roots,source,cfg_file=task
    cfg=configuration(); cfg["output_files"]={"metrics":"statistics/evaluation.json","model":"models/selected.rds"}
    cfg_file.write_text(json.dumps(cfg),encoding="utf-8")
    output=roots["AIRMOSAIC_ASSETS_DIR"]/"results/synthetic_regression/research_notes/trial-A"
    output.mkdir(parents=True); (output/"keep.txt").write_text("preserve")
    params={"input_csv":str(source),"task_config":str(cfg_file),"out_dir":str(output)}
    first,_=execute_task(task,params)
    assert first["status"]=="succeeded",first
    assert (output/"statistics/evaluation.json").is_file() and (output/"models/selected.rds").is_file()
    assert (output/"keep.txt").read_text()=="preserve"
    before=(output/"statistics/evaluation.json").read_bytes()
    second,_=execute_task(task,params)
    assert second["status"]=="failed" and second["reason"]=="artifact_already_exists"
    assert (output/"statistics/evaluation.json").read_bytes()==before
    assert str(output) not in json.dumps(first)
    with pytest.raises(ToolExecutionError,match="project_output_outside_project_root"):
        execute_task(task,{**params,"out_dir":str(roots["AIRMOSAIC_ASSETS_DIR"]/"results/other_project")})


def test_generic_scope_uses_only_git_ignored_skill_results(task,tmp_path):
    require_r_packages(); _,source,cfg=task
    repo=tmp_path/"checkout"; repo.mkdir()
    for name in ("runtime","catalog/schemas","skills/model/shared/machine_learning_model"):
        shutil.copytree(REPO/name,repo/name,ignore=shutil.ignore_patterns("__pycache__","results"))
    (repo/"catalog/tools").mkdir(parents=True)
    shutil.copyfile(REPO/"catalog/tools/ml_regression_workflow.yaml",repo/"catalog/tools/ml_regression_workflow.yaml")
    (repo/".gitignore").write_text('/'+SKILL_RESULTS+'/\n')
    subprocess.run(["git","init","-q",str(repo)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    runner=ToolRunnerService(ToolRegistryService(repo))
    record=runner.run(TOOL,{"input_csv":str(source),"task_config":str(cfg)},timeout=120)
    assert record["status"]=="succeeded" and record["result_scope"]=="skill",record
    output=repo/SKILL_RESULTS/record["run_id"]
    assert (output/"model.rds").is_file()
    assert subprocess.run(["git","check-ignore","-q",str(output/"model.rds")],cwd=repo).returncode==0
    (repo/".gitignore").write_text('')
    with pytest.raises(ToolExecutionError,match="skill_results_must_be_git_ignored"):
        runner.run(TOOL,{"input_csv":str(source),"task_config":str(cfg)},dry_run=True)
