# TimeXer setup, command and output checks

**English** | [中文](usage_ZH.md)

Use the reviewed external source from [UPSTREAM.md](../UPSTREAM.md). These are direct research-code operations, not an AirMosaic runner adapter.

## Setup and input

Set `TIMEXER_SOURCE_DIR` to the fixed source outside this checkout and use a separate environment. The tracked requirements include torch 2.0.0, numpy 1.23.5, pandas 1.5.3 and scikit-learn 1.2.2, plus other imported model dependencies. Review platform/Python/CUDA compatibility and record actual versions; the source uses older APIs such as `np.Inf`. AirMosaic's Python requirement is not a validated model-environment specification.

The custom CSV has a parsed `date` column, numeric covariates and numeric target, ordered without duplicate timestamps or untreated missing values. The loader moves the named target last. `MS` predicts that target; `M` predicts all numeric variables. Frequency settings do not fill gaps or resample.

At the tracked commit, the custom loader uses approximately 70%/10%/20% chronological train/validation/test and fits its scaler on training. Validation/test include preceding historical context. Check that labels belong to the intended segment, training has at least `seq_len+pred_len` rows and evaluation segments have enough labels/context. Multi-entity, date-specific and rolling designs need a custom data adaptation.

## Configure and call

The following is a small synthetic training example: 168 historical points, 24 forecast points, patch length 24, two covariates plus target, model dimension 64, four heads, two layers and two epochs. These are computation examples. First generate enough synthetic `series.csv` rows in the indicated input directory; the command does not create data.

Run in the selected model environment. A new directory under `assets/results/example_forecast/` keeps upstream relative outputs together:

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

Record all arguments separately. `label_len`, `dec_in` and `c_out` are generic CLI fields; the actual TimeXer output follows its feature mode. `seq_len` should be divisible by `patch_len` to avoid silently dropped target-tail points. The model consumes historical inputs; passing future decoder covariates does not add a future-information channel.

## Check the tracked source behavior

| Item | Practical consequence |
|---|---|
| Device | The source resets GPU use from CUDA availability; `--use_gpu False` does not reliably force CPU. Use a reviewed launch environment or adapt a task copy. |
| Randomness | Global initialization is fixed to 2021; `--seed` does not control all randomness. Multi-seed studies need adaptation. |
| Evaluation | Training computes validation and test loss each epoch; formal held-out evaluation must prevent development decisions from using test results. |
| Checkpoint identity | The generated setting name omits some arguments, including patch length; preserve full configuration. |
| Test-only mode | `--is_training 0` uses labeled test data, rebuilds data/scaling and loads the current directory's `./checkpoints/<setting>/checkpoint.pth`, regardless of a custom checkpoint root. |

## Read results

| Relative artifact | Meaning and check |
|---|---|
| `checkpoints/<setting>/checkpoint.pth` | Best-validation state dictionary; separately preserve scaler and input contract |
| `results/<setting>/pred.npy`, `true.npy` | Labeled test-window predictions/truths; check shape, origins and target columns |
| `results/<setting>/metrics.npy` | MAE, MSE, RMSE, MAPE, MSPE in that order; verify scale and near-zero denominators |
| `test_results/<setting>/*.pdf` | Selected window plots |
| `result_long_term_forecast.txt` | Appended metric record in the working directory |

With `--inverse`, verify inverse-transformed units explicitly. Compare simple baselines and horizon/entity errors, inspect finite outputs and retain failed windows. Raw training logs contain arguments/paths and remain local.

## Adapt deployment inference

A new-history caller must load a trusted configuration/checkpoint, reuse the fitted training scaler and time encoding, preserve feature order and provide the latest history without future labels. Run `model.eval()` and `torch.no_grad()`, then map outputs to forecast origin/horizon, entity and units. Expected output is `[B,pred_len,1]` for MS or `[B,pred_len,C]` for M. Test this path independently before registering an execution adapter.

Source contracts: [custom data loader](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/data_provider/data_loader.py), [model](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/models/TimeXer.py), [training/test implementation](https://github.com/thuml/TimeXer/blob/76011909357972bd55a27adba2e1be994d81b327/exp/exp_long_term_forecasting.py). Existing validation is source/syntax review, not a successful training or inference run.
