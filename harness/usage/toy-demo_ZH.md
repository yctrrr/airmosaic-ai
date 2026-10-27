# 运行合成汇总示例

[English](toy-demo.md) | **中文**

本离线示例使用已有 `gcam_aggregate_provinces` 工具，计算逻辑保持不变，不下载数据或启动模型。先按[配置说明](../../config/examples/README_ZH.md)准备独立的私人资产、设置和认证根；演示生成的文件同样写在 Git 外。

从仓库根目录运行：

```sh
python -m pip install -e '.[dev,tools]'
python -m airmosaic.cli run-tool gcam_aggregate_provinces --project-id toy_example --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/toy-aggregate.json --dry-run
python -m airmosaic.cli run-tool gcam_aggregate_provinces --project-id toy_example --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/toy-aggregate.json
```

公开[输入](../../assets/data/01_socioeconomic_natural_change/ExampleMarketRows/v1/rows.csv)包含四行合成记录。[参考结果](../../assets/results/toy_example/reference/01_socioeconomic_natural_change/gcam_aggregate_provinces/province_aggregate.csv)只有一行：weighted_price = 40/3、quantity_sum = 3、province_count = 2。比较解析后的数值，CSV 编码和浮点显示格式可以不同。

新结果位于 `${AIRMOSAIC_ASSETS_DIR}/results/toy_example/<run_id>/01_socioeconomic_natural_change/gcam_aggregate_provinces/`，过程回执位于同次运行的 `records/`。每次调用使用新的运行编号。执行器不覆盖公开输入或参考文件，也不会将结果自动登记为可复用数据；人工复核与入库单独进行。
