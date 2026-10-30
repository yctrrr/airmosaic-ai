# TimeXer 来源跟踪

此文件记录本地使用说明对应的论文和代码版本，用于按需复核；没有自动拉取、安装、训练或定时监控。

| 项目 | 本次依据 |
|---|---|
| 官方仓库 | [thuml/TimeXer](https://github.com/thuml/TimeXer) |
| 论文 | [TimeXer: Empowering Transformers for Time Series Forecasting with Exogenous Variables，arXiv v4](https://arxiv.org/abs/2402.19072v4)，NeurIPS 2024 |
| 核对日期 | 2026-10-23 |
| 分支与提交 | main；[76011909357972bd55a27adba2e1be994d81b327](https://github.com/thuml/TimeXer/tree/76011909357972bd55a27adba2e1be994d81b327)，通过 git ls-remote 核对 |
| 代码许可 | 本次固定提交的根目录未见 LICENSE/COPYING；[许可询问](https://github.com/thuml/TimeXer/issues/17)尚无明确授权说明。记录此事实，不替作者推定许可 |
| 本地内容 | 独立编写的方法、使用说明、命令示例和非执行目录条目；未将上游源码、数据或权重纳入 AirMosaic |

本目录跟踪独立 TimeXer 仓库。Time-Series-Library 或其他库中的同名实现可能有不同接口、提交与许可，不能混用命令或将其许可直接套到本版本。后续需要复制/发布上游源码时，先核对适用授权；本轮说明编写不依赖复制源码。

## 核对范围

| 文件 | 本地关注点 |
|---|---|
| models/TimeXer.py、layers/Embed.py | MS/M、历史与未来输入、patch、归一化、输出形状 |
| data_provider/data_loader.py、data_factory.py | Custom CSV、目标列、时间切分、scaler、滑窗 |
| run.py、scripts/forecast_exogenous/EPF/TimeXer.sh | 真实参数、任务名称、GPU/seed 行为、训练和测试分支 |
| exp/exp_basic.py、exp_long_term_forecasting.py | 导入依赖、测试集访问、checkpoint 和输出路径 |
| requirements.txt、utils/tools.py | 依赖版本、旧 API、权重保存范围 |

## 更新步骤

1. 对比上游新提交与本次 SHA，先审查上述文件的变更；不要自动替换个人任务代码。
2. 分别检查方法、数据契约、CLI 和产物变化；方法论文与代码接口不一致时分别记录。
3. 在独立环境用合成输入验证导入、最小训练、checkpoint 复用和纯推理；不能用静态检查替代运行。
4. 同步本目录、机器学习分类和 catalog；实现审查过的执行适配器前保留 reference / not_executable。
5. 对共享差异做隐私检查，记录依赖、测试范围、日期与 SHA，只共享脱敏摘要。

## 本轮验证范围

已完成论文/源码阅读、CLI 参数和合成示例语法核对。当前 AirMosaic 检查环境缺少 torch、einops、reformer-pytorch、sktime 等模型依赖，且 numpy/pandas 不等于上游固定版本；未修改该环境、未执行上游模块、未安装模型依赖或训练模型。实际模型表现、GPU 兼容、checkpoint 推理和环境研究用途均未验收。
