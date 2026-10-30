# 公开数据与合成资产

[English](README.md) | **中文**

`assets/` 作为经人类科学审核后选定成果的复用入口，实验及其结果归属对应项目。内部组织方式留待后续确定，下列已有公开示例保持原状。

| 输入类型 | 声明 | 用途 |
|---|---|---|
| 已发表数据 | [public-data-manifest.json](public-data-manifest.json) | 审查来源、许可、署名、准确文件大小及哈希，作为只读输入 |
| 合成示例 | [toy-manifest.json](toy-manifest.json) | 明确的合成输入与参考 CSV，作为只读输入 |

[AQ-Bench v1](data/03_atmospheric_transport/AQ-Bench/v1/README_ZH.md) 是当前获授权的公开数据副本，保留 CC BY 4.0 许可及来源署名。外部工作副本和仓库副本采用相同数据集、版本布局，CSV 哈希一致。此次明确的公开镜像不授权复制其他私人数据、来源映射、凭据或科学结果。尚无自动同步；变更需明确审查并采用新版本。

执行器仅接收清单指定且哈希匹配的 CSV，拒绝未登记、变化或路径不安全的文件。上述清单是输入允许列表，不是获取工具、自动数据目录注册或科学验收；真实公开数据与合成示例分开登记。

可从[合成演示](../harness/usage/toy-demo_ZH.md)或[仓库输入回归预检](../config/examples/run-tool/aq-bench-repository.json)开始。四行合成示例采用无量纲数值，参考加权均值为 40/3，继续与观测数据区分。

实验结果和审核记录保留在对应[项目](../projects/README_ZH.md)。当前执行器保留已实现的外部输出位置，不回退到本目录写入未经审核的结果。是否纳入资产与是否公开发布分别审核。本轮不移动现有文件，见[结果与审核约定](../harness/assets_ZH.md)。