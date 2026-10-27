---
name: gcam-output-structure
description: 通过已注册 R 工具检查 GCAM 输出节点和单位；查询顺序固定，自定义情景或部门查询需要适配。
---

# GCAM 输出结构检查

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


> 调用状态：`gcam_inspect_output_structure` 是已实现并接入执行器的 R 脚本。查询顺序固定，不提供自由动作、情景或地区查询接口。

## 工作目录与认证

遵守[共享存储约定](../../../../../harness/storage-and-credentials_ZH.md)和[执行指南](../../../../../harness/usage/run-tool.md)。仓库外三个已存在根目录相互独立：`AIRMOSAIC_LOCAL_WORKSPACE` 存数据与结果，`AIRMOSAIC_CONFIG_DIR` 存非秘密设置和显式任务参数，`AIRMOSAIC_AUTH_DIR` 存浏览器状态。密码和令牌留在秘密管理器，不读取或分享凭据及浏览器配置内容。命令从仓库根目录使用安装项目的解释器运行；执行器自动分配 `output/<run_id>/<tool_id>/`，没有需要时省略输出参数。个人配置不自动加载。直接运行脚本会绕过检查；执行器不是操作系统沙箱。

## 用途

提取价格、数量和技术记录前，检查数据库中可用的情景、地区、部门、子部门、技术及内部节点，不要求预先构建部门登记表。

## 工作方式

模型以 XML 存入 BaseX 数据库，结构如下：

```text
collection()
  -> scenario
    -> world
      -> region
        @type = "region"
        @name = "AH" / "BJ" / ... / "China"
        -> supplysector / pass-through-sector
          -> subsector
            -> technology
              -> output-primary / output / physical-output
              -> input / demand-physical
```

地区查询常用入口：

```xquery
collection()/scenario/world/*[@type="region"]
```

全国汇总节点入口：

```xquery
collection()/scenario/world/*[@type="region" and @name="China"]
```

## 依赖及数据库布局

需要 R、声明的包、Java/BaseX，以及显式 `GCAM_RELEASE_DIR`。当前脚本读取 `${GCAM_RELEASE_DIR}/output/database_basexdb` 和 `${GCAM_RELEASE_DIR}/database_R/Prov_code_china.csv`，不同于 Python 提取器的分情景布局；其他结构需在授权任务副本适配。

参数为 `max_memory`，默认 `1g`，例如 `512m`，以及可选 `output_dir`。模型根只来自已检查的环境配置，不接受 `release_dir` 参数，并忽略调用方 `GCAM_BASEX_MAX_MEMORY`。没有 `action`、`scenario`、`region` 或 `sector` 参数。原脚本旗标是实现细节。

## 常用任务

- 核对布局和范围后，用注册工具检查固定情景、节点和部门查询；工具不接受查询选择器。
- 自定义部门、省份查询：按 `references/xquery-csv-templates.md` 适配任务副本。
- XML 树：`references/xpath-structure-guide.md`。
- 单位：`references/output-price-quantity-units.md`。
- 省份映射：`references/province-region-mapping.md`。

## 统一执行边界

使用[公开参数](../../../../../examples/run-tool/gcam-inspect.json)及项目解释器：

```powershell
python -m airmosaic_core.cli describe-tool gcam_inspect_output_structure
python -m airmosaic_core.cli run-tool gcam_inspect_output_structure --params-file examples/run-tool/gcam-inspect.json --dry-run
python -m airmosaic_core.cli run-tool gcam_inspect_output_structure --params-file examples/run-tool/gcam-inspect.json --timeout 600
```

Rscript 使用 `--vanilla`、任务专用主目录和临时目录，不加载个人启动、浏览器配置或包库设置。data.table 和 rgcam 安装在所选 R 的标准库；Java 使用 rgcam 类路径，兼容性仍需核对。查询和预检不启动 R，因此不证明包能加载；实际执行先检查命名空间，失败记录 `r_dependency_unavailable`。

执行器分配输出，要求以下四份文件均非空：`inspect_scenarios.csv`、`inspect_province_top_level.csv`、`inspect_industrial_sector_tree.csv`、`inspect_industrial_cost_nodes.csv`。原脚本在部分查询失败后仍继续，因此缺少产物记为 `expected_outputs_missing`，不记成功。内容另核，空查询或文件存在不构成科学验证。

自定义查询和分情景布局需适配。保留原模型及已有输出，路径或参数被拒绝不能作为绕过执行器的理由；直接脚本调用保留旧默认值且绕过保护。

## 参考资料

- `references/xpath-structure-guide.md`：节点树与路径。
- `references/xquery-csv-templates.md`：查询模板。
- `references/output-price-quantity-units.md`：价格与数量单位兼容性。
- `references/province-region-mapping.md`：省份与全国节点映射。
