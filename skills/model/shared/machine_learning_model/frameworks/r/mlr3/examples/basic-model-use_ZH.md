# 使用合成输入练习 mlr3

[English](basic-model-use.md) | **中文**

以下独立编写的 R 示例展示 Task → 开发期交叉验证 → 拟合 → 新数据预测，需要 mlr3/rpart，只使用内存合成数据。交叉验证成绩属于开发证据，新行只演示无最终测试标签的预测接口。

## 回归

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

## 二分类

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

按安装版本核对字典和参数名。真实任务按[操作说明](../references/workflow.md)增加合适划分和拟合型预处理；[注册回归技能](../../../../SKILL_ZH.md)提供受控执行入口，本示例不注册分类或调参工具。

一手接口：[TaskRegr](https://mlr3.mlr-org.com/reference/TaskRegr.html)、[TaskClassif](https://mlr3.mlr-org.com/reference/TaskClassif.html)、[Learner](https://mlr3.mlr-org.com/reference/Learner.html)、[resample](https://mlr3.mlr-org.com/reference/resample.html)。
