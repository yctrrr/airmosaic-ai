# Shared maintenance operations

**English** | [中文](README_ZH.md)

| Capability | Entry | Current support |
|---|---|---|
| Author or revise a skill | [Skill authoring](skill_authoring/SKILL.md) | Human/agent workflow plus a bounded direct static validator; no run-tool adapter |
| Review selected task evidence | [Autoskill](autoskill/SKILL.md) | Explicit-record lexical matching and supplied proposal formatting; no source execution, promotion or registered adapter |

The helpers do not read research data or credentials. Test checks live in `harness/checks/`. Source/schema review, synthetic execution and scientific acceptance remain separate.
