# GCAM Skill Data Boundary

## Belongs In This Skill

- XQuery/XPath templates and patterns
- Python/R scripts that query BaseX via parameterized calls
- Reference documentation about GCAM output structure, configuration, and input chain
- Flat parameter JSON for registered run-tool adapters, and clearly marked non-executable manual plans
- Unit and scenario naming conventions

## Does NOT Belong In This Skill

- GCAM model releases, executables, or Java binaries
- BaseX database directories or their contents
- Scenario output files (CSV, XML, PNG): keep in `${AIRMOSAIC_LOCAL_WORKSPACE}/output/<run_id>/<tool_id>/`
- Raw input CSV data used to build model scenarios
- Generated intermediate files (sector registries, method registries)
- Project-specific analysis outputs
- Large data archives (zip, tar, parquet)
- Personal browser profiles, cookies, or session tokens
- Private download URLs, API keys, or credentials
- Absolute local paths containing user home or workspace names

## Where Outputs Go

Enabled adapters allocate new files under:

```text
${AIRMOSAIC_LOCAL_WORKSPACE}/output/<run_id>/<tool_id>/
${AIRMOSAIC_LOCAL_WORKSPACE}/runs/<run_id>/record.json
```

The two registered GCAM R tools use run-tool task outputs and sanitized receipts; plotting receives a runner-owned `UNIT_PRICE_OUT_DIR`. Direct standalone calls bypass these protections. Keep all artifacts local; only reviewed summaries may be shared. No automatic cache promotion or file cleanup occurs.

## Where GCAM Release Package Lives

The GCAM release package (containing `exe/`, `input/`, `output/`, `libs/`) must be installed separately by the user. Use:

```powershell
$env:GCAM_RELEASE_DIR = "<path to release package>"
```

Store the private mapping in `${AIRMOSAIC_CONFIG_DIR}` and load it explicitly. Authentication state, if separately needed, belongs under `${AIRMOSAIC_AUTH_DIR}` or in a credential manager. This skill does not provide a credential loader.
