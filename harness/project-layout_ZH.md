# 项目布局与迁移

<!-- README-I18N:START -->

[English](project-layout.md) | **中文**

<!-- README-I18N:END -->

仓库顶层统一为一个可安装的 Python 项目，程序包为 `airmosaic/`；公开命令和已注册工具编号保持不变。

```text
airmosaic-ai-core/
├── pyproject.toml
├── airmosaic/
│   ├── cli.py
│   ├── mcp_server.py
│   └── services/
├── methods/
├── skills/
├── catalog/
├── workflows/
├── assets/
│   ├── data/<stage>/<dataset-name>/<version>/
│   └── results/<toy-project>/<reference-run>/<stage>/
├── config/examples/
└── harness/
    ├── checks/
    └── usage/
```

| 位置 | 职责 |
|---|---|
| `methods/` | 面向人的科学解释、假设、质量标准和完整计算路径叙述 |
| `skills/` | 电脑操作、软件准备、参数和操作检查 |
| `catalog/` | 共用声明；`tools/*.yaml` 仍是唯一工具注册来源 |
| `airmosaic/` | CLI、MCP 通信与公共执行、数据服务 |
| `workflows/` | 可执行路径定义区；编排引擎及可运行路径尚未实现 |
| `assets/` | 仅公开合成输入和参考结果 |
| `config/examples/` | 可复用的非秘密参数、项目和路径模板 |
| `harness/` | 安装、协作、代理边界和自动检查 |

```sh
python -m pip install -e '.[dev]'
python -m airmosaic.cli list-tools
python -m airmosaic.cli list-datasets
python -m pytest -q -p no:cacheprovider
```

## 迁移对应

移除原外层包装目录：程序包移到 `airmosaic/`，安装信息移到顶层 `pyproject.toml`，工作流定义移到 `workflows/`，检查移到 `harness/checks/`。参数示例移到 `config/examples/run-tool/`，MCP 连接检查位于 `harness/checks/mcp_smoke.py`，不再保留独立的顶层测试或示例树。迁移后重新进行可编辑安装，旧模块导入需要同步更新。

## 资产边界

仓库内 [assets](../assets/README_ZH.md) 只读清单声明的演示资产。真实数据与新结果使用 Git 外的私人 `AIRMOSAIC_ASSETS_DIR`；个人 CONFIG_DIR、AUTH_DIR 继续独立。私人根沿用相同的数据、结果结构，不再提供另一套工作区模式或旧缓存自动回退。[资产规范](assets_ZH.md)规定引用和人工复核。

CLI 和 MCP 共用同一注册表与执行器，不新增第二套清单。数据声明继续使用技能内 `datasets.yaml`，目录详情保留现有回退；目录迁移不合并这些声明，也不产生资产编号解析器。科学脚本与工具编号保留。当前仍需完整源码及可编辑安装，独立资源发行尚未实现。

四步导航及跨阶段共享能力保留，第二步继续仅方法。新说明使用英文默认文件和 `_ZH.md` 中文版。参见[编写规范](skill-authoring_ZH.md)、[运行说明](usage/runtime_ZH.md)和[存储约定](storage-and-credentials_ZH.md)。
