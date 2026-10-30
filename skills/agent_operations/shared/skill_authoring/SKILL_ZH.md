---
name: skill-authoring
description: 新建或修订 AirMosaic 操作技能，在交付审查前静态检查元数据、本地引用和 Python 资源。
compatibility: Python 3.10+ standard library; AirMosaic repository checkout
metadata:
  version: "1.0.0"
---

# 技能编写

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->

新建或修订操作技能时，以[编写规范](../../../../harness/skill-authoring_ZH.md)为权威正文。根据证据选择维护方向时，使用 [autoskill](../autoskill/SKILL_ZH.md) 和[改进契约](../../../../harness/skill-improvement_ZH.md)。科学定义归方法，组合归工作流。本入口不增加科学方法，也不从任务日志推断方法。

阅读相关入口和当前任务范围，保留既有标识与无关工作，然后同步编写英文入口和中文译本。仅增加确有用途的脚本和参考。准确的元数据格式和检查范围见[检查器操作](references/operations_ZH.md)。

从仓库根运行：

```sh
python skills/agent_operations/shared/skill_authoring/scripts/validate_skill.py --repo-root . --skill skills/agent_operations/shared/skill_authoring
python -m pytest harness/checks/test_skill_authoring.py -q
```

预期 JSON 包含 `valid: true`、空诊断列表和 `execution_verified: false`。修复静态缺陷并审查差异、操作边界、双语一致性及有效合成检查。静态通过不证明依赖安装、宿主发现、工具就绪或科学验收。扩大数据访问、执行或发布范围前，应核对当前授权；已接受的动作在原范围内持续有效，无需重复确认。

本技能是人工编写流程和已实现的直接静态检查辅助脚本，没有注册工具编号，`run-tool` 不支持调用。仓库文件和展示元数据不等于宿主安装。仓库目录 `skill_authoring` 与规范名称 `skill-authoring` 有意区分；单独获得安装授权时，宿主打包可复制到符合名称要求的目录，不应顺带重命名既有仓库目录。
