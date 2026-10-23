# 合成数据上的基本模型使用

以下是独立编写的 R 使用示例，展示 Task → 开发期 CV → 拟合 → 新数据预测。需要 mlr3 和 rpart；本轮只完成语法解析，当前检查环境缺少 mlr3，未实际训练。示例不是 run-tool 参数或自动入口。

只使用内存中的合成开发数据，无文件读写或联网。新样本没有真实标签，用于演示预测 API；CV 分数不是独立最终测试分数。数据均为完整数值列，因此本例不做拟合型预处理。真实任务需要按[工作流](../references/workflow.md)增加图内预处理及合适划分。

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

运行前按本机安装版本检查字典与参数。调参、选阈值或比较多模型应另定义开发方案；不要反复修改这些代码后把最好的一次 CV 当作独立性能证据。

API 依据：[TaskRegr](https://mlr3.mlr-org.com/reference/TaskRegr.html)、[TaskClassif](https://mlr3.mlr-org.com/reference/TaskClassif.html)、[Learner](https://mlr3.mlr-org.com/reference/Learner.html)、[resample](https://mlr3.mlr-org.com/reference/resample.html)。参考项目与本地版本记录见 [UPSTREAM.md](../UPSTREAM.md)。
