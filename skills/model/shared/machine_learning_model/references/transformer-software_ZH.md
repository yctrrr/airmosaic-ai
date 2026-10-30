# 运行和检查 Transformer 软件案例

[English](transformer-software.md) | **中文**

科学选择归[方法说明](../../../../../methods/shared/machine_learning_model/models/transformer/README_ZH.md)及其[数据说明](../../../../../methods/shared/machine_learning_model/models/transformer/data_ZH.md)。本参考提供具体软件操作和实际验证范围。

## 1. 选择软件和环境

直接示例使用 Python 3.11+、PyTorch 2.6+ 和本仓库。选择可信环境，确认 `python` 对应这些依赖。2026-10-30 已在 Python 3.14.4、PyTorch 2.13.0+cpu 上检查 CPU 执行。这是环境记录，不要求其他环境统一升级；其他版本和平台需自行核验。

缺少依赖时，按任务的安装授权，通过[官方 PyTorch 选择器](https://pytorch.org/get-started/locally/)准备独立环境。助手不会安装包、索取凭据、下载数据或权重，也不选择 GPU。这些示例不需要 Lightning 或 Hugging Face 依赖。

| 软件参考 | 可借鉴的操作 | 适配边界 |
|---|---|---|
| [PyTorch Lightning 技能](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/pytorch-lightning/SKILL.md) | 分离数据、训练、验证、检查点和预测阶段 | 其分类模板不是数值回归模型，使用前需更换数据约定、输出层、损失和指标 |
| [Transformers 技能](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/transformers/SKILL.md) | 核对模型版本、本地权重及支持的推理或微调接口 | 文本分词及语言模型 Trainer 示例不定义大气数值输入约定 |
| [TimeXer 操作](../models/time_series/timexer/references/usage_ZH.md) | 使用真实上游环境、命令和输入约定 | 自定义划分、训练期访问测试集、缩放器持久化和纯历史推理仍需适配 |

本地助手借鉴第一项的职责分离，独立编写，没有复制分类脚本。这些来源链接于 2026-10-30 作为参考核对，不是自动安装或更新服务。

## 2. 选择有界案例和配置

使用[完整配置](../../../../../config/examples/machine-learning-model/python/transformer.synthetic.json)，并选择一个已声明案例：

| 案例 | 生成的输入，包含批量轴 `B` | 编码单元 |
|---|---|---|
| `tabular` | `static: [B, 4]` | 四个数值特征 |
| `sequence` | `history: [B, 8, 3]` | 八个历史时刻 |
| `grid` | `grid: [B, 1, 4, 4]` | 四个不重叠空间片段 |
| `fusion` | 上述三类输入 | 分别投影，加入身份和位置信息，拼接后共同进行自注意力 |

没有数据集或检查点输入参数。已知的合成标量目标由内部生成的三类来源共同构造，单路案例只接收其声明来源。这些示例检查软件机制，不构成模型族的科学排序。

JSON 显式控制 `samples`、`seed`、`d_model`、`heads`、`layers`、`epochs`、`batch_size`、`learning_rate`、`weight_decay` 和 `dropout`，并要求 `purpose=synthetic_software_demo`。数量控制独立生成的群体，不规定真实数据的划分。助手拒绝未知字段、注意力头维度不兼容、非有限设置以及超出小规模范围的预算。本 JSON 不是两个既有回归工具接受的任务。

## 3. 准备分离根目录并预检

选择所需 Python 环境后，从仓库根执行命令。按[存储设置](../../../../../config/examples/README_ZH.md)在 Git 外建立三个独立根，设置 `AIRMOSAIC_ASSETS_DIR`、`AIRMOSAIC_CONFIG_DIR`、`AIRMOSAIC_AUTH_DIR`。助手只读取 `config/examples/` 或个人配置根中显式选择的非秘密 JSON，不加载个人启动配置或检查认证文件。

选择尚不存在的外部结果目录。以下 PowerShell 示例使用项目的分钟命名约定：

```powershell
$amCase = 'fusion'
$amTaskLabel = (Get-Date -Format yyyyMMddHHmm) + '_' + $amCase
$amOutput = Join-Path $env:AIRMOSAIC_ASSETS_DIR ('results/transformer_software_demo/' + $amTaskLabel)
python skills/model/shared/machine_learning_model/scripts/python/run_transformer_demo.py --case $amCase --config-file config/examples/machine-learning-model/python/transformer.synthetic.json --out-dir $amOutput --dry-run
```

预期为 `can_execute=true`、`blockers=[]`、`external_input_supported=false`、`output_created=false`。预检校验路径、JSON 和已安装包元数据，不导入 Torch 或生成张量，也不证明 Torch 能成功初始化。缺少 Torch 时返回依赖阻塞项，不尝试安装。

## 4. 执行并检查结果

预检后，以相同案例和输出位置执行：

```powershell
python skills/model/shared/machine_learning_model/scripts/python/run_transformer_demo.py --case $amCase --config-file config/examples/machine-learning-model/python/transformer.synthetic.json --out-dir $amOutput
```

尝试其他案例时，先更换案例名称和全新的输出位置，再重复预检与执行。只修改案例但复用已有输出目录会失败，没有覆盖开关。输出须位于外部资产结果根内，至少包含任务目录及新的运行目录。文件系统链接、Git 祖先及认证或记录保留名称被拒绝。这些是直接调用的检查，不是操作系统隔离，也不提供执行器的最小子进程环境。

| 产物 | 检查内容 |
|---|---|
| `configuration.json`, `input-contract.json` | 实际案例、数量、形状、种子及仅训练期拟合的预处理 |
| `events.jsonl` | 按序且带时间的已完成轮次、验证准则、检查点选择及之后的测试评估 |
| `metrics.json`, `predictions.csv` | 有限且带样本键的预测，独立 RMSE/MAE/R² 及训练均值参照 |
| `checkpoint.pt` | 模型参数及训练期拟合的预处理；只重载本次新生成文件 |
| `checks.json`, `status.json` | 有限非零梯度、指标一致、重载一致、CPU/包版本及 `scientific_acceptance=false` |
| `artifacts.json` | 相对文件位置和校验值；未完成运行不生成 |

实现在训练输入上拟合预处理，只使用训练标签训练，以验证 MSE 选择检查点，之后才生成并评估测试群体。通过 `weights_only=True` 重载自己的检查点，不读取任意已保存模型。指标复用既有助手；网络成绩可能劣于均值参照，也必须如实保留。

事件记录带时区偏移的真实 UTC 时间，只覆盖软件动作和检查，不捕获宿主代理对话、研究的代码生成依据或回顾性科学审核；适用时按[工作流交接契约](../../../../../harness/usage/workflow-handoff_ZH.md)保留这些材料。

失败后保留部分输出，核查原因后使用新位置。常见代码为 `missing_separated_roots`、`demo_configuration_root`、`demo_budget_exceeded`、`demo_output_exists`、`demo_unsafe_output`；`missing_torch` 是预检阻塞项。不能把数据移入认证根或更换真实任务标签来适配示例。

## 5. 单独衔接真实研究

本助手不支持真实表格、观测、栅格文件、文本、缺失模态、不规则窗口、GPU/分布式训练或任意预训练权重。它没有 run-tool/MCP 注册，也没有科学计划批准门控，因为唯一允许的任务是内部合成演示。新科学研究仍需遵守[规划与审核](planning_ZH.md)，准备真实加载器、明确样本键、信息可得性及划分规则，并实现经审查的执行适配器。

通用代码归技能，科学设计归方法，工作流可以引用案例而不复制训练逻辑。项目结果仍使用外部 `assets/results/<project_id>/`，内部结构按任务选择。示例输出不会自动提升为共享数据或提交。
