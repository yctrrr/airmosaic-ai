---
name: csmar-downloader
description: CSMAR local capability; full implementation requires explicit local extension
  selection.
metadata:
  access: local_private
---

# CSMAR local capability

**English** | [中文](SKILL_ZH.md)

Complete methods, operating instructions, configuration and dedicated code live in a separate local private extension. This public entry is a summary only.

Select the [local capability configuration](../../../../harness/usage/local-capabilities.md) explicitly; the default state is `private_extension_required`. No implementation is read or downloaded automatically.

When selected, `csmar_browser_download` remains a browser-workflow reference; `csmar_process_company_info` retains its existing local-processing interface. Institutional data access and user login remain separate requirements.
