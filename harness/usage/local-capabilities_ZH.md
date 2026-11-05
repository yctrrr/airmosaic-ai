# 本地私有能力

[English](local-capabilities.md) | **中文**

平台专用的方法、操作说明、脚本和模板可以保存在独立的本地目录中，无须创建 GitHub 私有仓库、上传文件或联网。公开仓库只保留概述和稳定标识。

## 存储与显式选择

私有能力目录放在公开仓库之外，与数据、结果、个人配置和认证分别保存。其 `methods/`、`skills/` 沿用公开项目的研究阶段布局。`capabilities.json` 声明有限文件清单，公开源码中的 `catalog/local-capabilities.json` 规定可选择的位置；不能借此导入任意插件。

在成员自己的外部配置目录中创建非秘密 JSON，将 `root` 替换为本地绝对路径：

```json
{"schema_version": 1, "root": "<absolute local private capability directory>"}
```

占位符须在本地替换。实际映射、密码、令牌、会话和私人路径均不进入 Git。只有显式传入配置才会加载；单独设置 CONFIG_DIR 不会自动生效。选择能力不读取凭据或浏览器配置。

在已安装公开项目的环境中调用：

```powershell
python -m runtime.cli list-tools --skill csmar-downloader
python -m runtime.cli --local-capabilities-config "$env:AIRMOSAIC_CONFIG_DIR/local-capabilities.json" list-tools --skill csmar-downloader
python -m runtime.cli --local-capabilities-config "$env:AIRMOSAIC_CONFIG_DIR/local-capabilities.json" describe-capability skill csmar-downloader
python -m runtime.cli --local-capabilities-config "$env:AIRMOSAIC_CONFIG_DIR/local-capabilities.json" validate-capabilities
```

全局选项放在子命令前。SDK 可向 `ToolRegistryService` 传入 `local_config`，再将该注册服务传给能力目录、执行器或 MCP 网关。具体任务参数和操作示例保存在所选私有技能内。

## 可用状态与执行

未启用时，四个保留的工具 ID 均返回 `private_extension_required`，不能运行。启用后保留实际状态：已有本地处理器使用原执行适配器；浏览器获取仍是参考流程；年鉴操作仍是需人工适配的模板。没有新增下载适配器或计算逻辑。

选定的注册服务在私有根内解析已声明的源码文件；输入、输出和运行记录仍遵守执行器既有的独立根约定。缺文件、错误映射和越界路径均拒绝。注册查询不返回配置值或私人绝对路径。私有代码以调用者的操作系统权限运行，不隔离同一用户的其他进程。

## MCP

为授权使用单独启动本地实例：

```powershell
python -m runtime.mcp_server --local-capabilities-config "$env:AIRMOSAIC_CONFIG_DIR/local-capabilities.json"
```

这是启动选项，MCP 调用参数不能选择其他根。默认执行仍为空跑，真实执行、网络和浏览器会话继续遵守原有授权。该实例会向连接客户端提供选定的私有说明，只连接授权客户端；不传此选项的实例仅提供公开概述。没有部署远程 MCP 或新增认证代理。

## 分享边界

私有目录和实际配置不进入公开仓库、导出包或发行产物；授权数据和认证仍独立保管。迁走当前文件不能删除 Git 历史中的旧内容；本次设置不重写历史，也不自动发布。
