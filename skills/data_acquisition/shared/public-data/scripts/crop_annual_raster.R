# Crop on the source lattice and independently compare the persisted pixels.
args <- commandArgs(TRUE)
stopifnot(length(args) == 7L)
suppressPackageStartupMessages(library(terra))
src_path <- normalizePath(args[1], winslash = "/", mustWork = TRUE)
out_dir <- normalizePath(args[2], winslash = "/", mustWork = TRUE)
script <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))
repo <- normalizePath(file.path(dirname(script), "../../../../.."), winslash = "/")
stopifnot(!startsWith(paste0(tolower(out_dir), "/"), paste0(tolower(repo), "/")))
receipt <- jsonlite::read_json(args[3], simplifyVector = TRUE)
sha <- function(x) digest::digest(x, algo = "sha256", file = TRUE)
stopifnot(identical(receipt$sha256, sha(src_path)))
bounds <- as.numeric(args[4:7])
stopifnot(all(is.finite(bounds)), bounds[1] < bounds[2], bounds[3] < bounds[4])
source <- rast(src_path)
native <- as.vector(ext(source))
stopifnot(nlyr(source) == 1L, is.lonlat(source), same.crs(source, "EPSG:4326"),
          all(native[c(1, 3)] <= bounds[c(1, 3)]), all(native[c(2, 4)] >= bounds[c(2, 4)]))
extent <- ext(bounds)
signature <- digest::digest(list(receipt, bounds, sha(script)), algo = "sha256")
target <- file.path(out_dir, signature)
if (dir.exists(target)) {
  existing <- jsonlite::read_json(file.path(target, "source.json"), simplifyVector = TRUE)
  # Identical TIFF bytes can occur in different annual releases.
  identity_fields <- intersect(c("product", "doi", "year", "version", "file_id"), names(receipt))
  stopifnot(identical(existing[identity_fields], receipt[identity_fields]),
            identical(existing$input_sha256, receipt$sha256),
            identical(existing$sha256, sha(file.path(target, "crop.tif"))))
} else local({
  subset <- crop(source, extent, snap = "out")
  staging <- tempfile(".crop-", tmpdir = out_dir)
  stopifnot(dir.create(staging))
  on.exit(unlink(staging, recursive = TRUE))
  tif <- file.path(staging, "crop.tif")
  storage <- datatype(source)
  stopifnot(length(storage) == 1L, nzchar(storage))
  writeRaster(subset, tif, datatype = storage, gdal = "COMPRESS=DEFLATE")
  output <- rast(tif)
  stopifnot(compareGeom(output, subset, stopOnError = FALSE),
            all(abs(res(output) - res(source)) < 1e-11),
            all(abs(origin(output) - origin(source)) < 1e-9))
  first <- cellFromXY(source, xyFromCell(output, 1L))
  offset <- rowColFromCell(source, first)[1L, ]
  readStart(source)
  readStart(output)
  on.exit({ readStop(source); readStop(output) }, add = TRUE)
  missing <- 0
  for (row in seq.int(1, nrow(output), by = 128L)) {
    count <- min(128L, nrow(output) - row + 1L)
    restored <- readValues(output, row = row, nrows = count)
    original <- readValues(source, row = offset[1] + row - 1L, nrows = count,
                           col = offset[2], ncols = ncol(output))
    stopifnot(identical(is.na(restored), is.na(original)), all(restored[!is.na(original)] == original[!is.na(original)]))
    missing <- missing + sum(is.na(original))
  }
  stopifnot(ncell(output) > missing)
  readStop(source)
  readStop(output)
  on.exit(unlink(staging, recursive = TRUE))
  receipt$input_sha256 <- receipt$sha256
  receipt$sha256 <- sha(tif)
  receipt$path <- "crop.tif"
  receipt$extent <- as.vector(ext(output))
  receipt$resolution <- res(output)
  receipt$rows <- nrow(output)
  receipt$columns <- ncol(output)
  receipt$compared_pixels <- ncell(output)
  receipt$missing_pixels <- missing
  receipt$verified <- TRUE
  jsonlite::write_json(receipt, file.path(staging, "source.json"), auto_unbox = TRUE, pretty = TRUE, digits = NA)
  stopifnot(file.rename(staging, target))
})
cat(target, "\n")
