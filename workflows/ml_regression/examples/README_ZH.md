# 生成材料与执行检查示例

[English](README.md) | **中文**

[具体请求](request_ZH.md)把工作流[提示词](../prompt_ZH.md)应用到本任务。经审查的[控制器](generated_regression.py)调用注册回归技能及[公共合成配置](../../../config/examples/ml-regression/workflow-synthetic.json)。运行时重放代理编写的代码，不调用大模型生成接口。

真实数据在生成代码前如何按文献制定方案，可查看 [AQ-Bench 坐标配对设计](aq_bench_coordinate_comparison/README_ZH.md)与[依据到代码的审查表](aq_bench_coordinate_comparison/code-review_ZH.md)。该案例仍是待审设计和任务草案，没有执行空间验证；下述合成重放保留自身范围。

在仓库根目录，按[技能说明](../../../skills/model/shared/machine_learning_model/SKILL_ZH.md)显式准备分离的存储根和 R 包库，然后执行：

```sh
python workflows/ml_regression/examples/generated_regression.py --task-name synthetic_regression
python workflows/ml_regression/examples/generated_regression.py --task-name synthetic_regression --utc-offset +08:00 --execute
```

预检不拟合、不创建结果目录。执行时排他创建 `workflows/ml_regression/results/<YYYYMMDDHHmm>_<task-name>/`。名称显示到分钟，显式时差默认 +08:00。内部 `--run-id` 只用于关联回执，不再作为可见目录名。任务名必须为可公开的小写标识；重名或已有内部回执会被拒绝。

每次结果包含：

- `gen_script/run.py`、`task.json`、提示词/请求副本、成对的 `generation*.md` 及结构化 `generation.json`；
- `gen_script/dependencies.json`、`dependencies.patch`，标识复用公共代码并保存相对 Git 基准的改动和新增内容，不复制完整源码树；
- 带时间的 `events.jsonl`、独立执行器回执、模型/预测/解释产物及独立 `verification.json`；
- 成对的 `retrospective*.md`、总体终态 `workflow.json` 和 `delivery-sha256.json`。

新运行不生成 `source_snapshot/`，也不复制输入数据。被忽略的结果树保留全部本地产物；历史目录不自动改名或删除；经明确授权并核对后可清理冗余合成批次。[当前验证回执](verification.json)保存保留批次的脱敏检查摘要；经授权删除的旧合成批次另在清理清单中记录。

生成依据是计算前保存的显式设计说明，不是补写的历史思考轨迹。事件记录实际控制器边界，预检先缓冲、取得目录后写入；不自动采集完整宿主代理会话、生成代码修改历史或 R 内部操作。回顾摘要明确标注事后整理。遵循[统一过程记录规范](../../../harness/usage/workflow-handoff_ZH.md)。

重放时使用已保存代码的相对位置，替换下面的示例目录：

```sh
python workflows/ml_regression/results/<timestamp>_<task>/gen_script/run.py --task-name synthetic_replay --execute
```

重放使用保存的任务和生成材料，核对当前依赖哈希，并创建全新结果目录。依赖变化时需审查后重建或适配，不自动应用补丁。补丁保留统一换行的公共文本，并分别记录字节和标准换行哈希；覆盖空新增文件及缺少末尾换行的情况。

除独立进程回执外，应检查总体 `workflow.json` 和交付哈希。R 进程成功不等于工作流完整交付。固定合成检查包含验证/测试键与观测一致、所选模型及训练均值基线指标独立重算、模型重载一致，以及测试 RMSE 低于合成基线。负向工程检查覆盖路径、私人/外部输入、记录、依赖恢复及核验/封存失败。这些检查不批准科学结论，也不代表新真实数据上的性能。
