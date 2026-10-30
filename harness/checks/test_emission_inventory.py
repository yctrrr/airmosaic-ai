"""Synthetic accounting/unit/path checks for the direct inventory helper."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skills/model/02_emission_inventory/emission-inventory-methods"
SCRIPT = SKILL / "scripts/calculate_inventory.py"
EXAMPLE = SKILL / "examples/inventory.synthetic.json"
spec = importlib.util.spec_from_file_location("inventory_helper", SCRIPT)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def example():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def emitted(result, pollutant):
    return sum(row["emitted_kg"] for row in result["totals"] if row["pollutant"] == pollutant)


def test_toy_numbers_routes_and_pollutant_separation():
    result = helper.calculate_inventory(example())
    assert emitted(result, "SO2") == pytest.approx(24664)
    assert emitted(result, "NOx") == pytest.approx(30960)
    for row in result["details"]:
        assert row["uncontrolled_kg"] == pytest.approx(row["emitted_kg"] + row["removed_kg"])
        selected = [r for r in result["routes"] if all(r[k] == row[k] for k in ("activity_id", "technology_id", "pollutant"))]
        assert sum(r["emitted_kg"] for r in selected) == pytest.approx(row["emitted_kg"])
    assert result["checks"]["scientific_acceptance"] == "not_assessed"


@pytest.mark.parametrize("field", ["operating_fraction", "capture_fraction", "removal_efficiency"])
def test_zero_effective_control_retains_uncontrolled_emissions(field):
    data = example()
    for route in data["control_routes"]:
        route[field] = 0
    result = helper.calculate_inventory(data)
    assert emitted(result, "SO2") == pytest.approx(92000)
    assert emitted(result, "NOx") == pytest.approx(36000)


def test_full_capture_operation_and_removal_and_zero_activity():
    data = example()
    for route in data["control_routes"]:
        for field in ("operating_fraction", "capture_fraction", "removal_efficiency"):
            route[field] = 1
    assert all(row["emitted_kg"] == 0 for row in helper.calculate_inventory(data)["details"])
    data["activities"][0]["amount"] = 0
    assert all(row["uncontrolled_kg"] == 0 for row in helper.calculate_inventory(data)["details"])


def test_mass_and_energy_unit_conversions_preserve_emissions():
    original = example()
    mass = deepcopy(original)
    mass["activities"][0]["amount"] *= 1000
    mass["activities"][0]["unit"] = "kg"
    for factor in mass["factors"]:
        factor["value"] *= 1000
        factor["mass_unit"] = "g"
    assert emitted(helper.calculate_inventory(mass), "SO2") == pytest.approx(24664)
    energy = deepcopy(original)
    energy["activities"][0]["unit"] = "GJ"
    for factor in energy["factors"]:
        factor["activity_unit"] = "TJ"
        factor["value"] *= 1000
    assert emitted(helper.calculate_inventory(energy), "SO2") == pytest.approx(24664)


@pytest.mark.parametrize("mutate,code", [
    (lambda x: x["activities"][0].update(amount=-1), "numeric_value_out_of_range"),
    (lambda x: x["technologies"][0].update(activity_share=0.7), "technology_shares_must_sum_to_one"),
    (lambda x: x["control_routes"][0].update(route_share=0.3), "control_route_shares_must_sum_to_one"),
    (lambda x: x["control_routes"][0].update(removal_efficiency=95), "numeric_value_out_of_range"),
    (lambda x: x["factors"][0].update(control_basis="controlled"), "factor_must_be_uncontrolled"),
    (lambda x: x["factors"][0].update(activity_unit="GJ"), "activity_factor_dimension_mismatch"),
    (lambda x: x["factors"][0].update(activity_basis="different_material"), "activity_factor_basis_mismatch"),
    (lambda x: x["factors"].pop(), "incomplete_pollutant_factor_coverage"),
    (lambda x: x["control_routes"].append(deepcopy(x["control_routes"][0])), "duplicate_control_route"),
    (lambda x: x["activities"][0].update(amount=float("nan")), "invalid_numeric_value"),
    (lambda x: x["activities"][0].update(amount=True), "invalid_numeric_value"),
    (lambda x: x.update(schema_version=True), "inventory_schema_mismatch"),
])
def test_invalid_inputs_are_rejected(mutate, code):
    data = example()
    mutate(data)
    with pytest.raises(helper.InventoryError, match="^" + code + "$"):
        helper.calculate_inventory(data)


def call(input_root, output_root, *extra):
    return subprocess.run([sys.executable, str(SCRIPT), "--input-root", str(input_root),
        "--input-json", "inventory.json", "--output-root", str(output_root),
        "--run-name", "synthetic_trial", *extra], text=True, capture_output=True, check=False)


def test_cli_dry_run_fresh_outputs_checksums_and_no_overwrite(tmp_path):
    inputs, outputs = tmp_path / "inputs", tmp_path / "outputs"
    inputs.mkdir(); outputs.mkdir()
    source = inputs / "inventory.json"
    source.write_bytes(EXAMPLE.read_bytes())
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    dry = call(inputs, outputs, "--dry-run")
    assert dry.returncode == 0
    assert json.loads(dry.stdout)["output_created"] is False
    assert not list(outputs.iterdir())
    actual = call(inputs, outputs)
    assert actual.returncode == 0
    assert json.loads(actual.stdout)["status"] == "succeeded"
    batch = outputs / "synthetic_trial"
    artifacts = json.loads((batch / "artifacts.json").read_text())
    for name, digest in artifacts["files_sha256"].items():
        assert hashlib.sha256((batch / name).read_bytes()).hexdigest() == digest
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert call(inputs, outputs).returncode == 2
    record = json.loads((batch / "record.json").read_text())
    assert record["network_used"] is False
    assert record["credentials_read"] is False
    assert str(tmp_path) not in (batch / "record.json").read_text()


def test_cli_rejects_git_outputs_and_duplicate_json_keys(tmp_path):
    inputs, outputs = tmp_path / "inputs", tmp_path / "outputs"
    inputs.mkdir(); outputs.mkdir()
    (inputs / "inventory.json").write_bytes(EXAMPLE.read_bytes())
    (outputs / ".git").mkdir()
    response = call(inputs, outputs)
    assert response.returncode == 2
    assert json.loads(response.stdout)["reason"] == "output_inside_git_refused"
    (inputs / "inventory.json").write_text('{"schema_version":1,"schema_version":1}')
    response = call(inputs, outputs)
    assert json.loads(response.stdout)["reason"] == "duplicate_json_key"


def test_cli_refuses_linked_input(tmp_path):
    inputs, outputs = tmp_path / "inputs", tmp_path / "outputs"
    inputs.mkdir(); outputs.mkdir()
    actual = inputs / "actual.json"
    actual.write_bytes(EXAMPLE.read_bytes())
    try:
        (inputs / "inventory.json").symlink_to(actual)
    except OSError:
        pytest.skip("Symlink creation unavailable to this Windows account")
    response = call(inputs, outputs)
    assert response.returncode == 2
    assert json.loads(response.stdout)["reason"] == "linked_path_refused"
