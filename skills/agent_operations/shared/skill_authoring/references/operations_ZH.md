# 静态编写检查器

<!-- README-I18N:START -->

[English](operations.md) | **中文**

<!-- README-I18N:END -->

`scripts/validate_skill.py` 仅使用标准库，读取 `--repo-root` 内明确选择的技能目录。最多检查 200 个选定资源，每个入口或 Python 脚本不超过 256 KiB；拒绝文件系统链接、重解析点和嵌套仓库，检查本地 Markdown 引用不越出所选仓库，解析 Python 语法而不导入或执行。越界引用、缺失引用和链接资源导致失败。不获取或验证 HTTP 链接和锚点。语法检查不证明脚本安全；其他语言脚本需要单独限定范围的检查。

新入口在两种语言中使用以下标量文件头：

```yaml
---
name: example-operation
description: Perform one bounded operation with reviewed inputs and checks.
compatibility: Python 3.10+; repository checkout
metadata:
  version: "1.0.0"
---
```

支持格式为单行字符串、可选的成对引号以及缩进两格的 `metadata` 映射。含冒号空格、类似注释或布尔值、数值的内容须加引号；有意拒绝复杂 YAML、别名、标签、重复键和多行标量。维护更复杂的既有格式时，另用完整 YAML 检查器。本检查器不迁移既有元数据，也不要求给整个仓库补填版本。

`name` 是稳定标识，新名称使用小写字母、数字和连字符，至多 63 字符；`metadata.version` 是语义版本，`compatibility` 声明运行和宿主条件。译本保持名称、版本及兼容说明一致。描述使用对应语言，为 15–1024 字符。每个入口需有一组互相切换的语言链接。目录名不必等于元数据标识。经明确审查的既有下划线标识，可用 `--published-name existing_id` 保留；这不授权重命名。

JSON 报告只含固定诊断码、资源数及 `execution_verified: false`，不含源码片段或私人路径。退出码 0 表示这些检查通过，2 表示拒绝或静态缺陷。参数解析失败也不回显未知参数内容。检查器只读，没有联网、导入、执行、注册或安装步骤，不是操作系统隔离或秘密检测器。仍需按编写契约单独审查隐私与语义，进行有效合成脚本测试，以及确有授权的集成检查。

```sh
python skills/agent_operations/shared/skill_authoring/scripts/validate_skill.py --repo-root . --skill skills/agent_operations/shared/skill_authoring
python skills/agent_operations/shared/skill_authoring/scripts/validate_skill.py --repo-root . --skill skills/agent_operations/shared/autoskill
python -m pytest harness/checks/test_skill_authoring.py harness/checks/test_autoskill.py -q
```
