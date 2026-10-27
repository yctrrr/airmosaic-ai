# AirMosaic AI 代理操作规范

<!-- README-I18N:START -->

[English](AGENTS.md) | **中文**

<!-- README-I18N:END -->


从仓库根目录开始，使用或修改流程前先阅读相关技能。本页只规定通用行为；具体产品名称、依赖与调用细节放在技能和分类说明中。

## 必须遵守的边界

- 说明维护与常规工程检查只用相关文档、接口和合成输入，不读取原始数据。真实获取、检查或计算需要限定任务。第二步仅列概念方法，不含具体数据、参数值、实现代码、项目脚本名或源码指纹。
- 遵守对象、年份、地区和操作范围。持续完成必要、已授权、可逆的工作，不重复询问；只补充关键缺失信息或授权。
- 先检查分支和工作区，保留原件、结果及他人修改。流程说明不授权批量下载、额外计算、安装、发布或发消息。
- 私人身份、密码、密钥、会话、浏览器配置、私人主机、签名链接和机器专用路径不得进入共享内容。疑似秘密只报告位置和类别。
- 数据结果放 `AIRMOSAIC_LOCAL_WORKSPACE`，非秘密设置放 `AIRMOSAIC_CONFIG_DIR`，浏览器状态放 `AIRMOSAIC_AUTH_DIR`。三根已存在、相互独立且在仓库外。凭据留在秘密管理器，或明确授权的官方客户端既有保护机制中，不读取或导出秘密。
- 外部发行包留在仓库外，新产物使用 `output/<run_id>/<tool>/`。没有明确授权不迁移旧结果或复制会话。
- 区分源码审查、合成或小样检查、真实集成与科学验证，不将计划或跳过内容描述为完成。
- 遵守[行为边界](harness/agent-boundaries_ZH.md)和[存储约定](harness/storage-and-credentials_ZH.md)。行为说明不构成操作系统隔离。

## 文档导航

按[四步流程](harness/four-step-workflow.md)、[技能导航](skills/README_ZH.md)和[方法映射](methods/README.md)选择入口。通用规则不列举具体能力，实际清单放分类导航与目录。

| 任务 | 说明 |
|---|---|
| 协作与交接 | [总体说明](harness/README_ZH.md) |
| 查找能力与状态 | [目录](harness/tool-catalog.md)、[查询](harness/usage/tool-registry.md) |
| 执行已审查适配器 | [统一执行](harness/usage/run-tool.md) |
| 准备本地根目录 | [存储约定](harness/storage-and-credentials_ZH.md)、[示例](config/examples/README.md) |
| 核心服务 | [基础使用](harness/usage/core.md) |
| 获取或整理数据 | [数据获取](harness/usage/data-acquisition.md) |
| 分析已有结果与适配模板 | [模型分析](harness/usage/model-analysis.md) |
| 使用专项流程 | [分类导航](skills/model/README_ZH.md) |
| 新增或注册能力 | [编写](harness/skill-authoring_ZH.md)、[注册](harness/tool-registration_ZH.md) |

通用规范、技能入口和分类导航有独立中英文版，历史专业参考可能保留既有语言。仅阅读当前任务需要的资料。

## 环境与发现

使用 Python 3.10+ 的项目环境，通过 `python -m pip install -e '.[dev]'` 安装。会话根显式配置，`.env` 不自动加载。缓存检查需要工作区变量或明确的调用参数；个人配置根与认证根是调用约定，不是自动加载器。

```sh
python -m airmosaic_core.cli --help
python -m airmosaic_core.cli list-tools --format json
python -m airmosaic_core.cli describe-tool airmosaic_list_datasets
python -m airmosaic_core.cli check-tool airmosaic_list_datasets
python -m airmosaic_core.cli list-datasets
```

`list-datasets` 读取声明，不列出已下载文件。`check-availability` 只检查文件存在性，不证明内容或科学有效性，输出中的私人路径需脱敏。规划命令只给模板。服务类包括 `DataCatalogService`、`DataAccessService`、`CausalDesignService`、`ToolRegistryService`、`ToolRunnerService`。

默认 `SKILL.md` 是入口，中文版是译本。宿主发现需要实际支持的位置或安装。`agents/openai.yaml` 只配置展示。保留历史技能与数据集编号差异，不按文件夹猜测。

工具登记来源为 `catalog/tools/*.yaml`。只读列表、详情与状态检查不运行脚本、不加载个人配置、不读取凭据。认证或依赖未验证时明确标记。

## 执行顺序

1. 明确范围，选择已实现入口。
2. 检查输入、版本、依赖、认证要求和输出位置。
3. 交接前核对单位、年份、时空对齐、缺失及科学假设。
4. 对已审查适配器先预检，核对 `can_execute` 与 `blockers`，再按授权执行。
5. 检查进程与真实产物内容，记录结果和限制。
6. 交付脱敏摘要或执行授权共享前检查隐私。

已启用适配器提供参数、路径检查、新输出、最小子进程环境和脱敏记录。联网与已有浏览器访问需要声明的授权标志。部分依赖仅在执行时检查。直接脚本不继承保护，模板、参考及未支持串联不能执行。执行器不是操作系统沙箱、凭据代理或工作流编排器，具体行为见分类说明。

## 贡献检查

- 遵守[编写规范](harness/skill-authoring_ZH.md)，区分技能发现、宿主展示、数据集、方法映射和执行工具。
- 通用规则不列举具体模型、框架或技术类别。名称、依赖、编号和用法放在对应技能及分类导航。
- 默认文件为英文，`_ZH.md` 为中文，各有一组切换链接并同步更新。标识和命令保持原样，不声称未处理资料已翻译。
- 接口示例、元数据与真实实现一致，新增说明不创建工具。
- 来源、误差、规范化与质量规则唯一正文放分阶段方法库或共享方法，技能链接正文；操作参考保存接口与验证示例。不把某来源门槛套到其他产品。
- 常规检查使用合成输入；行为改变时运行相应测试，纯说明修改不读取原始数据或运行模型。真实记录留在本地。
- 检查差异、新文件、日志及附件，数据归档不包含个人配置或认证目录。
- 当前任务授权提交推送后才执行，先完成检查，区分无关工作和已授权前置改动；不强制推送或改写历史。角色和路线图不授予权限。
