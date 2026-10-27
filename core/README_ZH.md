# AirMosaic 核心程序

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->

本 Python 子项目提供公共能力查询和受控的单工具执行。专业计算实现保留在技能目录。[仓库布局](../harness/project-layout_ZH.md)区分人类方法、操作技能、声明与执行。

## 安装与检查

在仓库根目录使用选定的项目解释器：

```sh
python -m pip install -e './core[dev]'
python -m airmosaic_core.cli list-tools
python -m pytest core/tests -q -p no:cacheprovider
```

在当前 `core/` 目录中：

```sh
python -m pip install -e '.[dev]'
python -m airmosaic_core.cli list-tools
python -m pytest tests -q -p no:cacheprovider
```

安装信息位于 `pyproject.toml`。`airmosaic_core/` 是可导入程序包，中间没有 `src/` 层。模块仍按本源码检出定位仓库的目录信息和技能资源，不依赖调用方当前目录。当前支持完整源码检出及可编辑安装；独立 wheel 尚不包含仓库的专业资源。

## 已实现边界

命令行和开发接口共用现有注册及执行服务。工具编号、适配器策略和科学计算保持不变。仅为所选任务安装可选依赖。处理数据或运行工具前遵循[执行指南](../harness/usage/run-tool.md)与[存储约定](../harness/storage-and-credentials_ZH.md)。

MCP 通信、工作流编排、产物登记服务和通用科学校验器尚未实现。[工作流定义区](workflows/README_ZH.md)明确保留，未声明可执行路径。测试使用合成输入，不代表科学验收。
