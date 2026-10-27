# 运行程序、安装与检查

<!-- README-I18N:START -->

[English](runtime.md) | **中文**

<!-- README-I18N:END -->

`airmosaic/` 程序包提供公共 CLI、MCP 和执行服务，安装信息位于仓库顶层。工具编号及专业计算逻辑不变。

```sh
python -m pip install -e '.[dev]'
python -m airmosaic.cli list-tools
python -m airmosaic.cli list-datasets
python -m pytest -q -p no:cacheprovider
```

安装命令为 `airmosaic`、`airmosaic-mcp`。MCP 需要可选 `mcp` 依赖，专业适配器各自声明所需依赖。当前支持完整源码与可编辑安装，目录查询不依赖调用方工作目录。

检查统一位于 `harness/checks/`，验证接口、执行、隐私和合成行为；调用参数位于 `config/examples/`。两者职责不同，不是重复测试。MCP 连接检查为 `python harness/checks/mcp_smoke.py`。

参见[布局](../project-layout_ZH.md)、[执行](run-tool.md)、[MCP](mcp_ZH.md)、[演示流程](toy-demo_ZH.md)及[资产规范](../assets_ZH.md)。工作流编排、自动复核入库及通用科学验证器尚未实现。
