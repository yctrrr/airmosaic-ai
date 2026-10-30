# TimeXer 环境、命令与输出检查

[English](usage.md) | **中文**

使用[上游记录](../UPSTREAM.md)中的已审查外部源码。以下是研究代码的直接操作，不是 AirMosaic 执行适配器。

## 环境与输入

用 `TIMEXER_SOURCE_DIR` 指向本仓库外的固定源码，使用独立环境。已跟踪依赖包括 torch 2.0.0、numpy 1.23.5、pandas 1.5.3、scikit-learn 1.2.2 及其他导入模型依赖。审查平台、Python 和 CUDA 兼容性，记录实际版本；源码使用 `np.Inf` 等旧接口，AirMosaic 的 Python 要求不是已验证的模型环境规格。

自定义 CSV 包含可解析的 `date`、数值协变量和数值目标，时间有序、不重复、没有未处理缺失。加载器将指定目标放到最后；`MS` 预测该目标，`M` 预测全部数值变量。频率参数不补缺或重采样。

固定提交的自定义加载器按时间约 70%/10%/20% 划分训练、验证、测试，缩放器只在训练段拟合。验证和测试包含此前历史上下文，应检查标签属于预期分段、训练至少有 `seq_len+pred_len` 行，评估段标签与上下文足够。多实体、指定日期和滚动设计需要数据适配。

## 配置并调用

以下为小规模合成训练示例：历史 168 点、预测 24 点、片段 24、两个协变量加目标、模型维度 64、四个注意力头、两层和两轮。这些是计算示例；先在输入目录生成足够长的合成 `series.csv`，命令不创建数据。

在模型环境运行，`assets/results/example_forecast/` 下的新目录集中保存上游相对路径输出：

```powershell
if (-not $env:AIRMOSAIC_ASSETS_DIR -or -not $env:TIMEXER_SOURCE_DIR) {
    throw 'Configure the asset root and reviewed source directory first.'
}
$runId = [guid]::NewGuid().ToString('N')
$taskDir = Join-Path $env:AIRMOSAIC_ASSETS_DIR "results/example_forecast/$runId"
$inputDir = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'data/01_socioeconomic_natural_change/ExampleTimeSeries/v1'
$entry = Join-Path $env:TIMEXER_SOURCE_DIR 'run.py'
if (-not (Test-Path -LiteralPath $entry -PathType Leaf) -or
    -not (Test-Path -LiteralPath (Join-Path $inputDir 'series.csv') -PathType Leaf)) {
    throw 'Reviewed source or synthetic input is missing.'
}
New-Item -ItemType Directory -Path $taskDir -ErrorAction Stop | Out-Null
Push-Location -LiteralPath $taskDir
try {
    python -B -u $entry `
        --task_name long_term_forecast --is_training 1 `
        --model_id synthetic_example --model TimeXer --data custom `
        --root_path $inputDir --data_path series.csv `
        --features MS --target target --freq h `
        --seq_len 168 --label_len 48 --pred_len 24 --patch_len 24 `
        --enc_in 3 --dec_in 3 --c_out 1 `
        --d_model 64 --n_heads 4 --e_layers 2 --d_ff 128 `
        --train_epochs 2 --patience 2 --batch_size 16 --itr 1 `
        --num_workers 0 --des synthetic --inverse --checkpoints ./checkpoints `
        *> ./training.local.log
    if ($LASTEXITCODE -ne 0) { throw 'TimeXer failed; inspect the local log.' }
} finally {
    Pop-Location
}
```

另行记录完整参数。`label_len`、`dec_in`、`c_out` 是通用 CLI 字段，实际 TimeXer 输出由特征模式决定。`seq_len` 应能被 `patch_len` 整除，避免丢弃目标尾部点。模型使用历史输入，传入未来 decoder 协变量不会自动增加未来信息通道。

## 核对固定源码行为

| 项目 | 实际影响 |
|---|---|
| 设备 | 源码按 CUDA 可用性重设 GPU，`--use_gpu False` 不能可靠强制 CPU；需经审查的启动环境或任务副本适配。 |
| 随机性 | 全局初始化固定为 2021，`--seed` 不控制全部随机性，多种子研究需适配。 |
| 评估 | 每轮计算验证和测试损失，正式留出评估需阻止开发决策使用测试结果。 |
| 权重身份 | setting 名称缺少部分参数，包括片段长度，应保存完整配置。 |
| 仅测试模式 | `--is_training 0` 使用带标签测试、重建数据与缩放，并从当前目录的 `./checkpoints/<setting>/checkpoint.pth` 加载，不沿用自定义权重根。 |

## 读取结果

| 相对产物 | 含义与检查 |
|---|---|
| `checkpoints/<setting>/checkpoint.pth` | 最佳验证轮状态字典；缩放器和输入契约另存 |
| `results/<setting>/pred.npy`、`true.npy` | 带标签测试窗口预测与观测；检查形状、起点和目标列 |
| `results/<setting>/metrics.npy` | 顺序为 MAE、MSE、RMSE、MAPE、MSPE，检查尺度及接近零的分母 |
| `test_results/<setting>/*.pdf` | 部分窗口图 |
| `result_long_term_forecast.txt` | 工作目录中追加的指标记录 |

使用 `--inverse` 时显式核对逆变换单位。比较简单基线及提前量、实体误差，检查有限输出并保留失败窗口。原始训练日志含参数和路径，留在本地。

## 适配部署推理

新历史调用需要加载可信配置和权重，复用已拟合训练缩放器、时间编码及特征顺序，在不要求未来标签的条件下提供最新历史。使用 `model.eval()` 和 `torch.no_grad()`，将输出对应到预测起点、提前量、实体和单位。MS 输出应为 `[B,pred_len,1]`，M 为 `[B,pred_len,C]`。注册执行适配器前独立测试该路径。

来源契约：[自定义加载器](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/data_provider/data_loader.py)、[模型](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/models/TimeXer.py)、[训练与测试](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/exp/exp_long_term_forecasting.py)。现有验证为源码与语法审查，不是已通过训练或推理。
