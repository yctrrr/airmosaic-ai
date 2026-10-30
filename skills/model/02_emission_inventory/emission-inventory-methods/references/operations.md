# Configure and run activity–technology–control accounting

**English** | [中文](operations_ZH.md)

The [method](../../../../../methods/02_emission_inventory/emission_accounting.md) explains scientific choices. The direct [script](../scripts/calculate_inventory.py) needs Python 3.10+ and the standard library only. It is not a registered tool; do not call `run-tool emission-inventory-methods`.

## Prepare one explicit input

Use the complete [synthetic JSON](../examples/inventory.synthetic.json) first. The root declares `schema_version=1`, `dataset_kind` (`synthetic` or `prepared_inventory`), public-safe `inventory_id`, pollutant names and the four tables below. `dataset_kind` is a caller declaration, not proof of synthetic provenance or access authorization. No real data are discovered or embedded automatically.

| Table | Required fields |
|---|---|
| `activities` | `activity_id`, `region`, `year`, `sector`, `process`, `amount`, `unit`, `activity_basis`, `source_ref` |
| `technologies` | `activity_id`, `technology_id`, `activity_share`, `source_ref` |
| `factors` | `activity_id`, `technology_id`, `pollutant`, `value`, `mass_unit`, `activity_unit`, `activity_basis`, `control_basis`, `source_ref` |
| `control_routes` | `activity_id`, `technology_id`, `pollutant`, `route_id`, `route_share`, `operating_fraction`, `capture_fraction`, `removal_efficiency`, `source_ref` |

All proportions are fractions in `[0,1]`, not percentages. Technology shares sum to one within an activity. Control route shares sum to one within a technology/pollutant, including the explicit uncontrolled route. No silent share renormalization occurs. Every technology needs one factor and a complete route partition for every declared pollutant. Duplicate keys, unknown rows, missing/nonfinite values, negative amounts/factors and controls already in factors are refused.

Activity/denominator units: `kg`, `tonne`, `GJ`, `TJ`, `MWh`, `unit_product`; factor numerator: `g`, `kg`, `tonne`. Only same-dimension conversions are allowed, with `1 tonne=1000 kg`, `1 TJ=1000 GJ`, `1 MWh=3.6 GJ`. `activity_basis` must agree exactly between factor and activity: units alone cannot establish physical equivalence. No heating value, density or chemical-species conversion is inferred. All output masses are kg. Table fields are exact; real-data field mapping and extra metadata belong in a separately reviewed preparation step.

Keep actual references, product/process definitions and source versions in the prepared input. Every factor and share in the bundled example is labeled synthetic. For real work, replace the sources and values deliberately after approval; do not treat example factors as defaults. The JSON is limited to 1 MiB and each table to 10,000 rows; this first route is a bounded accounting helper, not a national-scale streaming engine.

## Run from repository root

Choose an already authorized external result parent. For example, after the existing ASSETS root is configured, create a dedicated project directory:

```powershell
$inventoryOutputRoot = Join-Path $env:AIRMOSAIC_ASSETS_DIR "results/inventory_example"
New-Item -ItemType Directory -Path $inventoryOutputRoot -Force | Out-Null
python skills/model/02_emission_inventory/emission-inventory-methods/scripts/calculate_inventory.py --input-root skills/model/02_emission_inventory/emission-inventory-methods/examples --input-json inventory.synthetic.json --output-root "$inventoryOutputRoot" --dry-run
python skills/model/02_emission_inventory/emission-inventory-methods/scripts/calculate_inventory.py --input-root skills/model/02_emission_inventory/emission-inventory-methods/examples --input-json inventory.synthetic.json --output-root "$inventoryOutputRoot"
```

`--input-json` is a relative JSON name under the explicit `--input-root`; absolute inputs and parent traversal are refused. The script rejects linked/reparse ancestors, common credential-directory names and output roots inside any Git repository. These are scoped checks, not a complete authorization or OS isolation mechanism. It does not inspect configuration, authentication files or environment secrets.

Dry-run reads and validates the entire selected input and calculates its numeric result in memory, checking the prospective output path without creating output. Success returns `status=validated`, `output_created=false`. Actual execution creates a fresh child named `<UTC YYYYMMDDHHmm>_<inventory_id>`. Optionally pass a new public-safe `--run-name` to identify an independent trial. A same-minute/name collision fails rather than overwrites; check the original result before retrying. `status=succeeded` identifies a completed engineering calculation, not scientific acceptance.

## Check the output

| File | Check |
|---|---|
| `emissions.csv` | Activity/technology/pollutant allocated activity and uncontrolled/emitted/removed kg |
| `route_emissions.csv` | Route shares, operation/capture/removal and each route's kg contribution |
| `totals.csv` | Region/year/sector/pollutant aggregates; never an undefined sum across pollutants |
| `quality.json` | Share, unit/basis, emission mass-balance and aggregate checks; scientific acceptance remains `not_assessed` |
| `record.json` | Input SHA-256, method, UTC recording time, Python version and no-network/no-credential actions; no absolute paths |
| `artifacts.json` | Final success marker and hashes of the other five files |

Verify all recorded file hashes and independently sum detail rows by pollutant. For the toy input, SO₂ is 24,664 kg emitted and NOx 30,960 kg; SO₂ before controls is 92,000 kg and removed mass 67,336 kg. Preserve the exact input in its original authorized location and verify its hash remains unchanged. Failure may leave partial local files without a final success index; preserve and investigate them rather than accepting a CSV's presence as completion.

The actual 21 synthetic tests cover expected numbers, route/detail/aggregate agreement, zero operation/capture/removal, full removal, zero activity, compatible mass/energy units, bad shares/units/bases/factor coverage, nonfinite values, non-overwrite, Git outputs, duplicate JSON keys and linked inputs. Run them with the project's test environment:

```sh
python -m pytest harness/checks/test_emission_inventory.py -q
```

Store real inputs/results under approved external assets and private path mappings under CONFIG_DIR; credentials remain in a protected mechanism. Detailed output identifiers can still be sensitive. Review before sharing or promoting a new asset version. No downloader, spatial allocation, serial-device-state inference, uncertainty propagation or runner/MCP adapter is implemented here.
