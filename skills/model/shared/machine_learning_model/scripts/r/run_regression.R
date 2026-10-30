# Controlled capability entry; reusable scientific reasoning lives in methods/.
base <- dirname(Sys.getenv("AIRMOSAIC_R_ENTRYPOINT"))
for (module in c("common/io.R","common/target.R","common/select.R","common/prepare.R","models/fit.R","common/evaluate.R","contribution/explain.R","causal/causal.R")) source(file.path(base,module),local=TRUE)
main <- function() {
  args <- commandArgs(TRUE)
  if (length(args)!=6L || anyDuplicated(args[c(1,3,5)]) || !setequal(args[c(1,3,5)],c("--input-csv","--task-config","--out-dir"))) fail("invalid_workflow_arguments")
  values <- stats::setNames(as.list(args[c(2,4,6)]),args[c(1,3,5)])
  context <- new.env(parent=environment())
  context$input <- values[["--input-csv"]]
  context$cfg <- jsonlite::fromJSON(values[["--task-config"]],simplifyVector=FALSE)
  state$out <- values[["--out-dir"]]
  state$cfg <- context$cfg
  context$seed <- function(offset=0) {
    group <- if (state$current %in% c("prepare","select")) "sampling" else if (state$current=="fit") "model" else if (state$current=="causal") "causal" else "explanation"
    set.seed((as.double(context$cfg$seeds[[group]])+offset) %% 2147483000+1)
  }
  ml_target(context)
  ml_prepare(context)
  if (context$cfg$analysis=="prediction") { ml_fit(context); ml_evaluate(context); ml_explain(context) } else ml_causal(context)
  packages <- sort(loadedNamespaces())
  versions <- as.list(stats::setNames(vapply(packages,function(name) as.character(utils::packageVersion(name)),character(1)),packages))
  write_json(list(R=as.character(getRversion()),platform=R.version$platform,packages=versions,seeds=context$cfg$seeds,
    threads=1,input_md5=unname(tools::md5sum(context$input)),entrypoint_md5=unname(tools::md5sum(Sys.getenv("AIRMOSAIC_R_ENTRYPOINT"))),
    reload_predictions_equal=if (context$cfg$analysis=="prediction") context$reload_equal else NULL,
    cohort=context$cohort,scientific_review="pending"),"reproducibility")
  state$current <- "completed"; write_status("completed")
  roles <- required_roles(context$cfg)
  write_json(list(schema_version=1,analysis=context$cfg$analysis,files=context$cfg$output_files[roles]),"artifacts")
}
tryCatch(main(),error=function(error) {
  if (!is.null(state$out) && !is.null(state$cfg)) try(write_status("failed",if (inherits(error,"workflow_error")) error$code else "capability_execution_failed"),silent=TRUE)
  stop("capability_failed",call.=FALSE)
})
