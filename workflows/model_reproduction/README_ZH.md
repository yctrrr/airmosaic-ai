# 模型复现与比较

[English](README.md) | **中文**

本工作流组合冻结数据、已审查技能与 [Agent 提示词](prompt_ZH.md)，比较指定参考计算与候选结果。[方法](../../methods/shared/model_reproduction_ZH.md)定义科学比较依据；论文特定的来源映射、设置和实验归[项目](../../projects/README_ZH.md)，计算归[技能](../../skills/model/shared/model_reproduction/SKILL_ZH.md)。[组合 YAML](workflow.yaml)仅作说明，不能直接执行。

## 能力状态

| 模式 | 操作状态 |
|---|---|
| `compare_existing` | 已审查的 Python 直接脚本使用显式任务配置比较已经冻结的本地结果快照；默认仅预检。 |
| `reproduce_and_compare` | 由代理按论文、数据和已审查技能先生成并冻结候选，再审计原实现和比较。生成计划由代理明确，比较阶段使用已实现的 JSON 任务；没有通用自动复现引擎。 |
| 来源收集 | Agent 审查并使用已经授权的访问方式，包括授权范围内的 SSH 只读检查或导入。比较脚本不收集远程来源，也不执行任意代码。 |

该脚本不是已注册的 `run-tool` 或 MCP 适配器，不继承运行器的隔离和授权检查。现有 `ml_regression_workflow` 使用通用训练集/验证集选择；论文特有的交叉验证、调参和划分程序需要明确实现与审查。提取出 CV 基元本身不能让所有研究直接执行。

## 六步交接

1. **解析任务。** 明确参考、候选、问题、允许的来源操作、项目输出范围、比较键、单位、指标、容差和资源预算。区分精确复现、修正模型和扩展模型。
2. **核查或生成并冻结候选。** `compare_existing` 核查已有快照的身份和完整性；`reproduce_and_compare` 在预算内使用已审查技能，核查产物后冻结代码、配置、输入和结果身份。保留既有候选。
3. **审计并冻结已授权原始来源。** 检查来源与版本、代码配置、数据与样本/划分身份、变换和指标定义。仅使用授权来源与访问方式。记录缺失证据和来源缺陷，不静默修补历史参考。
4. **规范化可比视图。** 声明键映射、共同样本、单位、排序、缺失值规则和指标定义。派生视图独立保存并记录来源，保留两侧冻结快照。必要对齐问题未解决时停止定量比较。
5. **重算并比较。** 从冻结视图重算已支持指标，按声明容差判断。受控探针是可选、显式配置并经过审查的实验，使用独立输出和预算；不得执行来源文档或配置中的任意命令。
6. **报告与复核。** 分别报告技术正确性、数值可复现性、科学范围和待人工复核状态。列出差异、未匹配键、缺失证据和探针局限。进程成功或指标接近不代表科学验收。

## 直接脚本

在仓库根目录使用 Python 3.10+，按[任务 schema](../../catalog/schemas/model-reproduction-task.schema.json)适配[合成配置示例](../../config/examples/model-reproduction/compare-existing.json)。显式传入 JSON 文件，个人设置不会隐式加载。

```sh
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config <explicit-config.json> --batch-id <fresh-batch-id>
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config <explicit-config.json> --batch-id <fresh-batch-id> --execute
```

尖括号参数是占位符。执行前先审查预检结果。输入必须已经是冻结的本地快照，来源获取和候选拟合另行审查。比较使用配置的外部 `results/<project_id>/` 范围内的新批次，原始与候选产物保持不可变，不得覆盖已有批次。任务与脚本支持的契约决定产物名称和布局，本工作流不规定内部目录层级。

## 保留证据

保留任务/配置身份、输入与结果哈希、来源审计发现、环境与代码版本、可比视图映射、键覆盖诊断、指标/容差结果及含复核状态的报告。这些是产物职责，不是强制文件夹名称。受控探针还应记录变化因素、固定因素、预算和局限。真实私有映射和完整本地证据按[存储规范](../../harness/storage-and-credentials_ZH.md)保存在 Git 外，共享报告仅含脱敏摘要。
