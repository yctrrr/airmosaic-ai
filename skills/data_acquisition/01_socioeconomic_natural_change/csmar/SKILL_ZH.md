---
name: csmar-downloader
description: CSMAR local capability; full implementation requires explicit local extension
  selection.
metadata:
  access: local_private
---

# CSMAR 本地私有能力

[English](SKILL.md) | **中文**

完整方法、操作说明、配置及专用代码保存在独立的本地私有扩展中。公开项目仅提供能力概述。

通过[本地能力配置](../../../../harness/usage/local-capabilities_ZH.md)显式启用；默认状态为 `private_extension_required`，不会自动读取或下载实现。

启用后，`csmar_browser_download` 仍是浏览器流程参考；`csmar_process_company_info` 保留已有本地处理接口。机构数据授权和本人登录仍须分别核对。
