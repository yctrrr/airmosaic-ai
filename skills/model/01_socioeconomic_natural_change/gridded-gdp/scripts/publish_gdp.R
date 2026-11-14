# Publish an accepted candidate to an external release root with verified backups.
args <- commandArgs(TRUE)
stopifnot(length(args) %in% c(3L, 4L))
script_dir <- dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))))
source(file.path(script_dir, "gdp_common.R"))
repo <- normalizePath(file.path(script_dir, "../../../../.."), winslash = "/")
config <- normalizePath(args[1L], winslash = "/")
cfg <- read_json(config)
candidate <- normalizePath(args[2L], winslash = "/", mustWork = TRUE)
tag <- args[3L]
action <- if (length(args) == 4L) args[4L] else "plan"
require_ok(action %in% c("plan", "publish", "rollback"), "Use plan, publish, or rollback")
require_ok(grepl("^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$", tag), "Invalid release tag")
require_ok(cfg$mode %in% c("synthetic", "authorized"), "Explicit release mode required")
for (path in c(config, candidate, cfg$work_root, cfg$release_root)) outside_repo(path, repo)
require_ok(!is.null(cfg$release_root) && nzchar(cfg$release_root), "External release_root required")
candidate_root <- normalizePath(file.path(cfg$work_root, "candidates"), winslash = "/", mustWork = TRUE)
require_ok(identical(dirname(candidate), candidate_root), "Select a candidate generated in the configured work root")
receipt <- read_json(file.path(candidate, "receipt.json"))
years <- sort(years_from(cfg$output_years))
require_ok(identical(receipt$status, "accepted") && identical(receipt$mode, cfg$mode) &&
             identical(sort(years_from(receipt$years)), years) && identical(receipt$unit, cfg$gdp_unit),
           "Candidate is incompatible with this release request")
boundary <- resolve_input(cfg$data_root, cfg$inputs$boundary)
outside_repo(boundary, repo)
check_county_source(boundary)
require_ok(isTRUE(all.equal(receipt$geo, cfg$geo)) &&
             identical(receipt$boundary_sha256, file_hash(boundary)),
           "Candidate geometry or county boundary differs from this release request")
verify_files(candidate, receipt$file_hashes, recursive = TRUE)
paths <- names(receipt$file_hashes)
file_patterns <- c(
  "^Grid_interpolate_0[.]01g/(Grid_XGBoost_GDP_pc_0[.]01g_[0-9]{4}[.]tif|Grid_to_county_XGBoost_GDP_pc_[0-9]{4}[.]csv)$",
  "^County_interpolate/(County_XGBoost_GDP_pc_[0-9]{4}(-[0-9]{4})?[.]csv|Province_GDP_pc_calibration_[0-9]{4}[.]csv|Xgboost_GDP_model_[0-9]{4}-[0-9]{4}[.]json)$"
)
payload <- paths[Reduce("|", lapply(file_patterns, grepl, x = paths))]
require_ok(length(payload) >= 4 * length(years), "Candidate annual payload incomplete")
require_ok(setequal(setdiff(paths, payload), c("grid_acceptance.csv", "validation_metrics.csv")), "Unexpected candidate files")
for (year in years) {
  expected <- c(sprintf("Grid_interpolate_0.01g/Grid_XGBoost_GDP_pc_0.01g_%d.tif", year),
                sprintf("Grid_interpolate_0.01g/Grid_to_county_XGBoost_GDP_pc_%d.csv", year),
                sprintf("County_interpolate/County_XGBoost_GDP_pc_%d.csv", year),
                sprintf("County_interpolate/Province_GDP_pc_calibration_%d.csv", year))
  require_ok(all(expected %in% payload), "Missing annual files")
}

publish <- function() {
  if (!dir.exists(cfg$release_root)) require_ok(dir.create(cfg$release_root, recursive = TRUE), "Cannot create release root")
  release <- normalizePath(cfg$release_root, winslash = "/")
  work <- normalizePath(cfg$work_root, winslash = "/")
  data_root <- normalizePath(cfg$data_root, winslash = "/")
  overlaps <- function(a, b) startsWith(paste0(tolower(a), "/"), paste0(tolower(b), "/")) ||
    startsWith(paste0(tolower(b), "/"), paste0(tolower(a), "/"))
  require_ok(!overlaps(release, work) && !overlaps(release, data_root), "Use a separate release root")
  for (folder in c(release_folders, ".gdp-releases")) {
    path <- file.path(release, folder)
    if (file.exists(path) || dir.exists(path))
      require_ok(dir.exists(path) && identical(normalizePath(path, winslash = "/"), path), "Release path redirects")
    else require_ok(dir.create(path), "Cannot create release folder")
  }
  transaction <- file.path(release, ".gdp-releases", tag)
  lock <- file.path(release, ".gdp-releases", "lock")
  require_ok(dir.create(lock, showWarnings = FALSE), "Another release is in progress or needs recovery")
  on.exit(unlink(lock, recursive = TRUE))
  on.exit({
    if (exists("temporaries", inherits = FALSE)) unlink(temporaries)
  }, add = TRUE)
  destinations <- file.path(release, payload)
  sources <- file.path(candidate, payload)
  before <- vapply(destinations, function(path) {
    if (!file.exists(path)) return("")
    require_ok(!dir.exists(path) && identical(normalizePath(path, winslash = "/"), path), "Release target redirects")
    file_hash(path)
  }, "")
  after <- unname(vapply(receipt$file_hashes[payload], identity, ""))
  if (action == "rollback") {
    record <- read_json(file.path(transaction, "publication.json"))
    require_ok(identical(record$path, payload) && identical(record$after, after), "Release transaction differs")
    allowed <- before == record$after | before == record$before
    require_ok(all(allowed), "A later change conflicts with rollback")
    restore <- record$before != ""
    backup <- file.path(transaction, "backup", payload)
    require_ok(all(vapply(which(restore), function(i) file.exists(backup[i]) &&
                           file_hash(backup[i]) == record$before[i], logical(1))), "Backup checksum differs")
    for (i in which(restore & before != record$before)) {
      pending <- tempfile(".rollback-", tmpdir = dirname(destinations[i]))
      require_ok(file.copy(backup[i], pending) && file.rename(pending, destinations[i]) &&
                   file_hash(destinations[i]) == record$before[i], "Rollback restore failed")
    }
    # Newly added files move into the transaction for inspection rather than being discarded.
    for (i in which(!restore & before != "")) {
      retained <- file.path(transaction, "rolled-back", payload[i])
      dir.create(dirname(retained), recursive = TRUE, showWarnings = FALSE)
      require_ok(!file.exists(retained) && file.rename(destinations[i], retained), "Rollback move failed")
    }
    restored_hashes <- vapply(destinations, function(path) if (file.exists(path)) file_hash(path) else "", "")
    require_ok(identical(unname(restored_hashes), unname(record$before)), "Rollback readback failed")
    write_json(list(status = "rolled_back", tag = tag), file.path(transaction, "complete.json"))
    cat("ROLLED BACK", tag, "\n")
    return(invisible(NULL))
  }
  require_ok(!file.exists(transaction) && !dir.exists(transaction), "Release tag already exists")
  changed <- before != after
  if (!any(changed)) {
    cat("ALREADY PUBLISHED", tag, "\n")
    return(invisible(NULL))
  }
  temporaries <- vapply(dirname(destinations), function(parent) tempfile(".publish-", tmpdir = parent), "")
  pending_tx <- tempfile(".transaction-", tmpdir = dirname(transaction))
  require_ok(dir.create(pending_tx), "Cannot stage transaction")
  on.exit(unlink(pending_tx, recursive = TRUE), add = TRUE)
  for (i in which(changed)) {
    require_ok(file.copy(sources[i], temporaries[i]) && file_hash(temporaries[i]) == after[i], "Staged payload mismatch")
  }
  for (i in which(before != "")) {
    existing <- file.path(pending_tx, "backup", payload[i])
    dir.create(dirname(existing), recursive = TRUE, showWarnings = FALSE)
    require_ok(file.copy(destinations[i], existing) && file_hash(existing) == before[i], "Backup readback mismatch")
  }
  write_json(list(path = payload, before = unname(before), after = after, years = years, mode = cfg$mode,
                  acceptance_sha256 = file_hash(file.path(candidate, "receipt.json"))),
             file.path(pending_tx, "publication.json"))
  for (name in c("receipt.json", "grid_acceptance.csv", "validation_metrics.csv"))
    require_ok(file.copy(file.path(candidate, name), pending_tx), "Cannot retain acceptance receipt")
  require_ok(file.rename(pending_tx, transaction), "Cannot retain rollback transaction")
  # In case of a process or host interruption the transaction is already durable.
  for (i in which(changed)) {
    require_ok((file.exists(destinations[i]) && file_hash(destinations[i]) == before[i]) ||
                 (!file.exists(destinations[i]) && before[i] == ""), "Target changed after backup")
    require_ok(file.rename(temporaries[i], destinations[i]), "Promotion failed. Use rollback.")
  }
  require_ok(all(vapply(destinations, file_hash, "") == after), "Publication readback failed. Use rollback.")
  write_json(list(status = "published", tag = tag), file.path(transaction, "complete.json"))
  cat("PUBLISHED", tag, "\n")
}

if (action == "plan") {
  print(data.table(path = payload, sha256 = unlist(receipt$file_hashes[payload], use.names = FALSE)))
} else {
  publish()
}
