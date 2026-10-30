# 共享维护操作

[English](README.md) | **中文**

| 能力 | 入口 | 当前支持 |
|---|---|---|
| 新增或修订技能 | [技能编写](skill_authoring/SKILL_ZH.md) | 人工/代理操作流程及有界直接静态校验器；未接入 run-tool |
| 复核指定任务证据 | [Autoskill](autoskill/SKILL_ZH.md) | 显式记录词项匹配及已提供草案的格式化；不执行来源、不自动纳入或注册 |

助手不读取研究数据或凭据。测试检查归 `harness/checks/`，源码/结构审查、合成执行和科学验收分别说明。
