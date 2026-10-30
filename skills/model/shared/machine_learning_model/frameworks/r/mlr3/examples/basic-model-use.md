# Basic mlr3 use with synthetic inputs

**English** | [中文](basic-model-use_ZH.md)

These independently authored R examples demonstrate Task → development CV → fit → new-data prediction. They require mlr3/rpart and only use in-memory synthetic data. CV scores are development evidence, while the new rows illustrate prediction APIs without final-test labels.

## Regression

```r
stopifnot(requireNamespace("mlr3", quietly = TRUE))
stopifnot(requireNamespace("rpart", quietly = TRUE))
set.seed(20261023)

development = data.frame(x1 = rnorm(120), x2 = runif(120))
development$target = 2 * development$x1 - development$x2 + rnorm(120, sd = 0.2)
task = mlr3::TaskRegr$new(
  id = "synthetic_regression", backend = development, target = "target"
)
stopifnot("regr.rpart" %in% mlr3::mlr_learners$keys())
learner = mlr3::lrn("regr.rpart")

cv_result = mlr3::resample(
  task$clone(deep = TRUE), learner$clone(deep = TRUE),
  mlr3::rsmp("cv", folds = 3)
)
print(cv_result$aggregate(mlr3::msr("regr.rmse")))

fitted = learner$clone(deep = TRUE)
fitted$train(task$clone(deep = TRUE))
new_data = data.frame(x1 = c(-0.5, 0.5), x2 = c(0.2, 0.8))
stopifnot(identical(sort(names(new_data)), sort(task$feature_names)))
prediction = fitted$predict_newdata(new_data)
stopifnot(length(prediction$response) == nrow(new_data))
print(prediction$response)
```

## Binary classification

```r
stopifnot(requireNamespace("mlr3", quietly = TRUE))
stopifnot(requireNamespace("rpart", quietly = TRUE))
set.seed(20261024)

development = data.frame(x1 = rnorm(120), x2 = runif(120))
label = rep("negative", nrow(development))
label[development$x1 + development$x2 > 0.5] = "positive"
development$target = factor(label, levels = c("negative", "positive"))
task = mlr3::TaskClassif$new(
  id = "synthetic_classification", backend = development,
  target = "target", positive = "positive"
)
stopifnot("classif.rpart" %in% mlr3::mlr_learners$keys())
learner = mlr3::lrn("classif.rpart", predict_type = "prob")

cv_result = mlr3::resample(
  task$clone(deep = TRUE), learner$clone(deep = TRUE),
  mlr3::rsmp("cv", folds = 3)
)
print(cv_result$aggregate(mlr3::msr("classif.ce")))

fitted = learner$clone(deep = TRUE)
fitted$train(task$clone(deep = TRUE))
new_data = data.frame(x1 = c(-0.5, 0.5), x2 = c(0.2, 0.8))
prediction = fitted$predict_newdata(new_data)
stopifnot(nrow(prediction$prob) == nrow(new_data))
stopifnot(all(abs(rowSums(prediction$prob) - 1) < 1e-8))
print(prediction$prob)
```

Check available dictionary/parameter names against the installed version. Real tasks add appropriate splits and fitted preprocessing as described in [operations](../references/workflow.md). The [registered regression skill](../../../../SKILL.md) provides the controlled execution route; this example does not register classification or tuning tools.

Primary APIs: [TaskRegr](https://mlr3.mlr-org.com/reference/TaskRegr.html), [TaskClassif](https://mlr3.mlr-org.com/reference/TaskClassif.html), [Learner](https://mlr3.mlr-org.com/reference/Learner.html), [resample](https://mlr3.mlr-org.com/reference/resample.html).
