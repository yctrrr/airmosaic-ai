# TimeXer 时序预测

[English](README.md) | **中文**

已跟踪模型通过目标历史和历史外生序列进行预测。区分预测起点可得的信息与未来观测，声明采样间隔、历史长度、预测长度、目标及协变量角色，并明确是回顾评估还是部署。采用时间顺序开发和单独保护的最终测试，与适用的持续值或季节性参照比较。

科学背景见[时序设计](../../../../time_series_forecasting_ZH.md)。

AirMosaic 当前提供外部 Python/PyTorch 参考，尚无受控训练或推理适配器。已知未来协变量、多实体及纯历史推理需明确适配。 配置、代码调用及当前检查见[对应技能](../../../../../../skills/model/shared/machine_learning_model/models/time_series/timexer/SKILL_ZH.md)。

使用[公共评估设计](../../../evaluation_ZH.md)，在生成实验代码前提交[建模计划](../../../../model_planning_ZH.md)。
