# TimeXer 使用方法

本页介绍固定版本的外部研究代码如何使用，以及 AirMosaic 任务必须补齐什么。命令是供准备好环境后执行的示例；本轮只完成静态检查，没有运行训练。

## 1. 准备代码和独立环境

从 [UPSTREAM.md](../UPSTREAM.md)指定的官方仓库/提交准备一份仓库外源码。使用本地配置中的 `TIMEXER_SOURCE_DIR` 指向它；核对源码不在 AirMosaic checkout、数据输入、个人 config 或 auth 目录内。数据源授权、源码更新和训练是独立操作，不因阅读本说明而自动发生。

上游 [requirements.txt](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/requirements.txt)列出的版本包括 torch 2.0.0、numpy 1.23.5、pandas 1.5.3、scikit-learn 1.2.2，以及 einops、reformer-pytorch、sktime 等。原始 run.py 会导入多种实验/模型，即使只选 TimeXer，也不能只检查 torch。Python、PyTorch、CUDA/驱动和平台 wheel 必须一起核对；不要在 AirMosaic 核心虚拟环境直接覆盖版本。

目录条目的 Python >=3.10 表示 AirMosaic 查询环境要求，不是本次验证过的 TimeXer 运行版本；模型环境仍须单独核对。

需要安装时，在专用环境审查依赖后按固定 requirements 安装，并记录实际锁定版本。上游仍使用 np.Inf 等旧 API，不能把任意新版本视为等价替换。此页面没有自动安装器，也没有保证某个 Python/CUDA 组合已实测。

## 2. 数据契约

使用 `--data custom` 的基准入口时，CSV 采用下面的列结构；几行仅示意格式，远不足以训练。示例中的列名/值均为合成内容：

```csv
date,covariate_a,covariate_b,target
2024-01-01 00:00:00,1.0,2.0,10.0
2024-01-01 01:00:00,1.1,2.2,10.2
2024-01-01 02:00:00,1.2,2.1,10.1
```

- `date` 可解析、升序、无重复，采样频率和 `freq` 一致；频率参数不会自动补齐或重采样。
- `target` 为数值预测目标，其余特征也须数值化、无未处理缺失；删去身份字段和不允许建模的列。
- Custom loader 按原行序切成前 70% 训练、接着约 10% 验证、后 20% 测试；会把指定 target 移到最后，scaler 只拟合训练段。这里并非任务普适的划分方案。
- 验证/测试读取前 seq_len 行历史上下文；这不等于用未来标签训练。须核对每个窗口的标签时间属于对应分段，训练段至少有 seq_len + pred_len 行，验证/测试各至少有 pred_len 行，且前方上下文足够。
- 多实体、指定日期边界、滚动回测或未来已知协变量，需要自己的数据适配器。不要直接拼接实体或用全量数据拟合 scaler。

行为依据：[Dataset_Custom](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/data_provider/data_loader.py)及 [data_factory](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/data_provider/data_factory.py)。

## 3. 参数与合成训练示例

| 参数 | 本例 | 含义与检查 |
|---|---|---|
| task_name / model / data | long_term_forecast / TimeXer / custom | 上游基准也用该 task_name 做短窗口预测；名称不代表限定预测小时数 |
| features / target | MS / target | 多变量输入、单目标输出 |
| enc_in / dec_in / c_out | 3 / 3 / 1 | 输入为两个协变量加一个目标；dec_in/c_out 是通用 CLI 字段，TimeXer 的输出还由 features 决定 |
| seq_len / pred_len | 168 / 24 | 输入 168 个采样点，预测后 24 点；不是脱离频率的固定天数 |
| patch_len / label_len | 24 / 48 | 7 个目标 patch；label_len 用于通用 decoder 输入构造，当前 TimeXer 不消费 decoder 输入 |
| d_model / n_heads / e_layers / d_ff | 64 / 4 / 2 / 128 | 小型工程示例；维度须兼容，不能作为推荐科学超参数 |
| train_epochs / batch_size / itr | 2 / 16 / 1 | 仅合成冒烟检查预算；不代表模型收敛 |
| num_workers | 0 | 小例子避免额外加载进程；正式资源按任务设定 |
| inverse | 开启 | 测试输出逆变换到原数据尺度；须核对目标单位和 scaler |

以下仅对**自己生成的足量合成 series.csv**运行。先确认三类根独立且位于 Git 外，输入在工作区内，源码路径已核对。激活 TimeXer 专用环境，在新的任务输出目录启动，让上游相对路径产物留在本地；`--checkpoints` 单独指定并不能覆盖其他输出位置。

```powershell
if (-not $env:AIRMOSAIC_LOCAL_WORKSPACE -or -not $env:TIMEXER_SOURCE_DIR) {
    throw 'Configure the local workspace and reviewed source directory first.'
}
$runId = [guid]::NewGuid().ToString('N')
$taskDir = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "output/$runId/timexer_workflow"
$inputDir = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE 'data_cache/timexer_example'
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

该示例不是路径安全执行器；实际任务仍须按[项目边界](../../../../../harness/agent-boundaries.md)核对路径、链接、环境和权限。原始日志含参数及路径，保持本地，分享前脱敏。`-B` 避免 Python 向源码写 bytecode；不代表隔离其他副作用。

两个 CLI 陷阱已从 [run.py](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/run.py)核对：此版本根据 CUDA 可用性重新设置 use_gpu，`--use_gpu False` 不能可靠强制 CPU；需要 CPU 时在独立启动环境屏蔽 CUDA，或在审查过的任务副本修正开关。全局随机数初始化写死为 2021，`--seed` 并不控制全部训练随机性；多种子试验需显式适配并记录。

## 4. 评估与产物

上游训练每轮计算 validation 和 test loss，早停依据 validation，但人看到反复输出的 test loss 后仍可能据此选模型。正式任务需要在任务副本移除开发期 test 访问，冻结方案后再做约定评估；上面合成冒烟例不作为独立测试集验收。

| 当前脚本产物 | 含义 |
|---|---|
| checkpoints/<setting>/checkpoint.pth | 最佳验证轮的 state_dict；不包含完整输入契约和训练期 scaler |
| results/<setting>/pred.npy、true.npy | 带标签测试窗口的预测/真实值；不是未来日期的部署预测表 |
| results/<setting>/metrics.npy | 顺序为 MAE、MSE、RMSE、MAPE、MSPE；是否原单位取决于 inverse |
| test_results/<setting>/*.pdf | 部分测试窗口图 |
| result_long_term_forecast.txt | 当前工作目录中的追加指标记录 |

源代码：[训练与测试](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/exp/exp_long_term_forecasting.py)、[权重保存](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/utils/tools.py)。setting 由多项 CLI 参数生成，但并不包含所有模型配置（如 patch_len）；不能仅凭目录名判断模型兼容，应独立保存完整配置。

## 5. 已有权重与未知未来预测

`--is_training 0` 会读取 test loader，并从当前工作目录的 `./checkpoints/<setting>/checkpoint.pth` 加载；该分支未沿用自定义 checkpoints 根。它仍要求测试标签、会重新构造数据/scaler，不能用“只有最近历史”的新 CSV 直接代替部署输入。重新测试时必须核对训练配置、同一数据划分和本地 checkpoint 对应关系，避免覆盖旧结果。

部署推理需人工实现以下契约：

1. 从可信的本地训练产物加载配置和权重；核对源码、结构、特征次序和版本，不加载来源不明的序列化对象。
2. 复用保存的训练期 scaler 和时间特征规则；新批次不能重新拟合 scaler。准备最近 seq_len 点，MS 目标列最后，不要求未来目标标签。
3. 调用 `model.eval()`，在 `torch.no_grad()` 下对历史 x_enc 和对应 x_mark_enc 前向计算；当前模型的 decoder 参数可为 None。必要的输入处理不是自动完成的。
4. 将输出逆变换为正确目标单位，并绑定预测起点、提前量、时间戳和实体 ID；核对 `[B, pred_len, 1]` 或 `[B, pred_len, C]`，检查数值、适用范围和缺失。
5. 将上述准备、模型调用、输出与失败处理封装并测试后，才能申请接入 run-tool。当前没有可复用的 AirMosaic 推理命令或自动脱敏运行记录。
