# 公开与私人资产

<!-- README-I18N:START -->

[English](assets.md) | **中文**

<!-- README-I18N:END -->

仓库内 `assets/` 是公开入口，只包含合成示例和参考结果。真实数据及新结果使用 `AIRMOSAIC_ASSETS_DIR` 指定的私人资产根；个人设置与认证继续独立。参见[公开入口](../assets/README_ZH.md)和[路径模板](../config/examples/asset-paths.example.json)。

```text
<private-assets-root>/
├── data/<stage>/<actual-dataset-name>/<version>/
└── results/<project_id>/<run_id>/
    ├── <stage>/<tool_id>/
    ├── records/<tool_id>/record.json
    └── temp/<tool_id>/
```

## 组织与引用

共享数据依次按四个阶段、实际稳定名称和固定版本保存。每份数据只有一处主要归属，可以服务多个阶段及项目；项目在私人配置中引用同一版本，不重复复制。执行器接受显式输入路径，规划模板不会自动解析资产编号。第二步继续仅方法。

结果先按项目、唯一运行编号归集，再按阶段及工具保存，记录和临时文件留在同次运行内。每次单工具调用独占新的运行编号，相关调用通过同一项目编号关联。自动多工具执行与恢复尚未实现。

公开演示输入使用仓库相对 `assets/` 路径，并须通过 `toy-manifest.json` 哈希核对，只读取本次选定且已声明的文件。演示文件保持只读。包括演示任务在内，所有新结果都写入私人根。该根须已存在、与 CONFIG_DIR/AUTH_DIR 分离且位于所有 Git 仓库外；拒绝嵌套 Git、链接及路径越界。不提供将真实输出回退写入公开目录的机制。

## 首版流程

1. **计算与检查：** 候选产物保存在项目结果目录，附输入版本、实际代码和参数、输出清单及相关验证摘要。脱敏过程回执不证明科学质量合格。
2. **人工复核：** 用户核对含义与验证结果，选择具体文件及批准用途。待确认的[复核模板](../config/examples/assets/review.example.json)不代表批准，代理不能自行批准自己的结果。
3. **选定数据入库：** 明确批准后再次核对哈希，将选定数据复制到新的数据名称及版本目录，保留来源项目、运行及原结果。不覆盖原始数据或已有版本；图表、报告和模型保留在结果目录，由引用关联。

原始、整理、插补、预测及模拟数据保留各自类型。新项目检查是否符合批准用途。此流程由人工完成，尚无自动项目加载器、审批服务、科学验证器、资产编号解析器或入库命令。

## 配置与迁移

使用[配置示例](../config/examples/README_ZH.md)及 [run-tool](usage/run-tool.md)。需要留存回执的 CLI/SDK/MCP 调用必须提供项目和阶段。旧工作区变量、另一套输出布局及旧缓存自动回退停止使用。既有私人文件保留原位，本次不迁移或删除。实际私人路径不进入 Git、演示元数据或公开回执。连接通过配置引用实现，不使用文件系统链接。

[数据注册库](https://doc.dvc.org/example-scenarios/data-registry)、[验证检查点](https://docs.greatexpectations.io/docs/core/trigger_actions_based_on_results/create_a_checkpoint_with_actions/)和[版本登记](https://mlflow.org/docs/latest/ml/model-registry/workflow/)提供设计参考；它们不是已安装依赖，也不代表已实现审批服务。
