---
name: pm25-station-acquisition
description: Plan PM2.5 station observation acquisition and preparation, distinguish official exports, historical archives and homogenized products, and specify station/time quality checks and manual adaptation. Reference guidance only; no downloader or run-tool adapter.
---

# PM2.5 station monitoring: acquisition and preparation

<!-- README-I18N:START -->

**English** | [中文](SKILL_ZH.md)

<!-- README-I18N:END -->


**Status: reference.** Source selection, direct acquisition and preparation guidance. A public single-day hourly CSV/long-table example and a PANGAEA homogenized release/seven-day sample have been verified. No executable script, tool ID, dataset declaration or run-tool dry-run is provided. Skill/source/legacy-script names are not tool IDs.

Primary stage: **03_atmospheric_transport**, for concentration comparison, model evaluation and station observations. Stage 04 exposure/health work references the same [method](../../../../methods/03_atmospheric_transport/pm25_stations.md). No inventory implementation, automatic downloads, interpolation, training or health calculations.

## Define task boundaries first

- Documentation/source/interface work reads relevant descriptions, interfaces and file inventories, not original observations, coordinates or model results. File existence does not establish provenance, coverage or quality.
- Acquisition requires a defined network, dates, pollutants, station scope and destination. Follow existing authorization; reading this skill does not authorize bulk downloading.
- Preparation requires authorized inputs, output scope and statistics. Acquisition authorization does not automatically include aggregation, imputation or modeling.

## A. Acquisition

Select the product first:

- **Hourly published archive:** follow the [single-day example](references/single-day-example.md), checking types, missingness and original time labels.
- **Homogenized daily values:** read the [product method](../../../../methods/03_atmospheric_transport/pm25_homogenized.md), then the [PANGAEA example](references/homogenized-download-example.md). Preserve product IDs such as `S0001`; they are not original national station codes or evidence of valid-hour counts.

Both verified routes require no account/API key. Examples record procedures, results and times. Keep originally published values separate from adjusted/imputed daily products.

1. **Define the observation product:** network, station/city, hourly/daily support and original/quality-controlled/homogenized status. AQI is not PM2.5 concentration; gridded estimates are not station measurements.
2. **Choose provenance:** use the [source/format guide](../../../../methods/03_atmospheric_transport/pm25_stations_sources.md) for official publication, third-party archives or research products. Record producer, provider, version and license; do not infer provenance from local filenames.
3. **Prepare a non-secret plan:** batches, station-list version, units, time zone/labels, files, request counts, relative destinations, missingness and acceptance. Mark unknown fields; do not assume UTC or a fixed valid-hour threshold.
4. **Acquire/adapt the route:** start small within an authorized acquisition task, then expand based on checks. Use verified authorized websites/clients only. Record failures as failures; do not fill zeros, silently switch sources, weaken TLS or bypass access restrictions.
5. **Verify handoff:** response/file types, actual saved files, coverage and source manifests. Inspect contents only within scope; preserve originals read-only and distinguish download, format and scientific acceptance.

No downloader implements this procedure in AirMosaic. Direct website/client use does not inherit runner parameter, path or receipt protections.

## B. Preparation

Read the [data and normalization method](../../../../methods/03_atmospheric_transport/pm25_stations.md) for producer/archive provenance, instrument/acquisition/representativeness errors, concentration state, GB 3095's 20-hour daily rule and literature-specific scope. Do not aggregate daily means while time zone/hour-interval semantics remain unknown.

1. **Check interfaces:** review source fields and target contracts, then inspect actual schema, missing encodings and units only in the authorized task. Adapt mainland China, Taiwan, Canada and homogenized products separately.
2. **Normalize observations:** reshape station/hour fields as appropriate, retaining string IDs, original time and source. Select pollutant and averaging period explicitly. Preserve original quality flags; do not invent quality-control status.
3. **Join station history:** use explicit keys and validity periods, checking uniqueness, relocations and coordinate reference. Do not permanently match by column position/city or apply current coordinates to all history.
4. **Resolve overlap/aggregate:** define unique keys and duplicate/conflict handling before counting valid unique times. Apply dated standards and study-specific daily/annual completeness rules; row count is not valid hours.
5. **Validate handoff:** follow [quality/handoff guidance](../../../../methods/03_atmospheric_transport/pm25_stations_preparation.md) for long tables, station versions, coverage/missingness and methods. Imputation, clipping, relocation merging or homogenization requires its own method/authorization.

## Manual adaptation and present capability

Legacy ideas include reshaping, daily aggregation and coordinate joins, but fixed paths/years, interactive working directories, implicit keys and counting assumptions prevent treating old scripts as ready downloaders. See the [adaptation checklist](../../../../methods/03_atmospheric_transport/pm25_stations_preparation.md#人工适配清单).

Do not copy, directly invoke or register old scripts. Future adapters need explicit parameters/dependencies, read-only inputs, fresh outputs, failure states, path checks and sanitized receipts; synthetic/HTTP-substitute tests precede registration.

## Paths, credentials and agent boundaries

Follow the [storage contract](../../../../harness/storage-and-credentials.md) and [agent boundaries](../../../../harness/agent-boundaries.md):

- Plans/mappings: `AIRMOSAIC_CONFIG_DIR/pm25-stations/`; member-configured roots are not automatically loaded. Public examples contain no personal absolute paths.
- Downloads/derived outputs: `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/03_atmospheric_transport/pm25-stations/`, separating raw files, processed data, station metadata and quality summaries. Authorized reusable cache: `data/03_atmospheric_transport/PM25_Stations/<source>/<version>/`.
- Receipts: `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/records/<tool_id>/`; shared records contain logical sources, relative locations and sanitized states, not signed URLs or raw authentication logs.
- Browser sessions, when required: `AIRMOSAIC_AUTH_DIR/browser_profiles/<source>/`; credentials stay in a secret manager. Three roots remain separate/outside Git; directory conventions are not OS isolation.
- Remote inspection uses only authorized client/configuration/alias combinations, verifies the final compute endpoint and scopes directories. Do not read full SSH configurations, keys or unrelated logs, or process on management nodes. Personal connection mappings are excluded.

## Completion criteria

Documentation tasks deliver source choices, gaps and adaptation plans without claiming acquisition. Acquisition/preparation tasks deliver authorized artifacts and evidence separately. Leave unresolved source, time, scope or permission questions explicit rather than guessing.

Follow the [asset layout and review contract](../../../../harness/assets.md): share data by stage, actual dataset name and version; group results by project and run. Reference the same data across stages; registration for reuse requires human approval.
