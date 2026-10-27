---
name: health-impact-analysis
description: 将 PM2.5 健康影响计算和绘图模板适配至对齐的浓度、人口、基线死亡率与相对风险数据；没有可直接运行的健康模型。
---

# PM2.5 健康影响分析

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


> 调用状态：`pm25_hia_calculate_template` 与 `pm25_hia_visualize_template` 是执行器禁用的 R 模板，需要输入适配及独立科学验证。

## 工作目录与认证

遵守[存储约定](../../../../harness/storage-and-credentials_ZH.md)和[执行指南](../../../../harness/usage/run-tool.md)。`AIRMOSAIC_LOCAL_WORKSPACE` 存数据与结果，`AIRMOSAIC_CONFIG_DIR` 存非秘密参数，`AIRMOSAIC_AUTH_DIR` 存浏览器状态；三根已存在、相互独立且在仓库外。凭据留在秘密管理器，不读取或分享凭据及浏览器配置内容。仓库命令从根目录使用安装项目的解释器运行，可执行适配器自动分配输出；个人配置不自动加载。直接运行脚本绕过检查，执行器不是操作系统沙箱。

## 用途

使用人群归因分值框架准备 PM2.5 归因死亡分析。本技能提供方法和可适配的计算、绘图模板，不是端到端可执行服务。

## 方法

### 核心公式

逐格计算使用以下归因分值公式，保留计算标识：

```
Attributable Deaths = Population x PAF Mortality Rate

PAF Mortality Rate = sum over (endpoint, sex, age):
    AgeStruc(age, sex) x BaselineMortRate(endpoint, sex, age) / 100,000 x PAF(conc, endpoint, age)

PAF(conc, endpoint, age) = (RR(conc, endpoint, age) - 1) / RR(conc, endpoint, age)
```

其中：

- `RR`：浓度响应曲线给出的相对风险。
- `BaselineMortRate`：GBD 分病因死亡率，单位为每十万人。
- `AgeStruc`：对应年龄、性别组人口份额。
- `concentration`：年均 PM2.5，单位 µg/m³；模板按曲线最大浓度截断。

### 浓度响应曲线

模板涉及两类曲线：

| 曲线 | 方法 | 来源 | 病因 |
|---|---|---|---|
| GEMM-5COD | 五病因全球暴露死亡模型 | Burnett 等，2018、2022 | 慢阻肺、肺癌、下呼吸道感染、缺血性心脏病、卒中 |
| IER | 综合暴露响应模型 | GBD 2010/2013 | 同上 |

查找表字段为 `curve_name, endpoint, concentration, agegroup, RR`。浓度按 0.1 µg/m³ 分箱，超出曲线最大范围的值按模板截断。

### 年龄处理

- 示例使用年龄标签 0、5、10 至 75、80+。
- 将 80+ 开口组与更细死亡年龄组合并时，需要显式人口分母及审核后的映射。检查模板处理，不将率相加或旧编号当作已验证的汇总。

## 所需输入

### 1. PM2.5 浓度栅格

- CSV 字段：`X_Lon, Y_Lat, concentration`。
- 分辨率按分析设计，例如 0.1°；单位为年均 µg/m³。
- 来源示例为 TAP、卫星估计或化学输送模式输出。

### 2. 人口栅格

- RDS 或 CSV 字段：`X_Lon, Y_Lat, GridID, Year, urarea, Pop`。
- 与浓度网格一致，来源可为 WorldPop、GPW 或 LandScan。

### 3. 年龄结构份额

- RDS 或 CSV 字段：`X_Lon, Y_Lat, GridID, Year, sex, agegroup, AgeStruc`。
- 示例要求每格每性别的年龄份额和为一；使用前核对人口分母及模板契约。
- 可由年龄、性别人群产品推导。

### 4. 基线死亡率

- CSV 字段：`location_name, Year, metric, endpoint, sex, agegroup, MortRate`。
- 单位为每十万人死亡数，来源为国家或次国家 GBD 结果。

### 5. 相对风险查找表

- CSV 字段：`curve_name, endpoint, concentration, agegroup, RR`。
- 浓度用于匹配时为保留一位小数的字符。
- 在曲线明确的参考浓度核对 `RR = 1`，不统一假设参考浓度为零。

## 输出

### 格点结果

`pm25_premature_death_grid_{curve}_{year}.csv`

| 字段 | 含义 |
|---|---|
| X_Lon, Y_Lat | 格点中心坐标 |
| GridID | 唯一格点编号 |
| Year | 年份 |
| urarea | 城乡或总体分类 |
| Pop | 人口人数 |
| curve_name | 使用的响应曲线 |
| concentration | PM2.5 浓度，µg/m³ |
| MortRate_PM25 | 归因死亡率 |
| Mort | 归因过早死亡人数 |

### 汇总统计

`pm25_premature_death_summary_{curve}_{year}.csv`，按 `Year, curve_name, urarea` 汇总总人口、总死亡数及人口加权浓度。

### 绘图

- 死亡人数分箱：<1、1–5、5–10、10–25、25–50、50–75、75–100、100–150、>150。
- 使用反向光谱配色，单位为每格死亡人数。
- 示例叠加中国边界和南海插图。

## 人工适配与科学边界

用 `describe-tool` 查询两个真实模板的位置和要求；两者均不可由执行器运行，没有可直接使用的健康服务。

复制所需模板到新任务目录，适配浓度、人口年龄分母、基线死亡率、风险曲线、年份、年龄性别映射、缺失及全部输出路径。加载 R 文件会执行处理，不能当作安全的帮助查询。死亡率年份及年龄协调等固定假设需要领域审核。先验证简单案例和分组总量，再进行真实分析；模板存在或退出码为零不证明流行病学有效性。环境变量和检查点见[模型指南](../../../../harness/usage/model-analysis.md)。

## 显式配置

没有自动配置加载器。适配任务显式设置 `PM25_HIA_CONC_DIR`、`PM25_HIA_POP_DIR`、`PM25_HIA_MORT_FILE`、`PM25_HIA_RR_FILE`、`PM25_HIA_OUTPUT_DIR`、`PM25_HIA_YEARS`、`PM25_HIA_CURVE`；绘图另用 `PM25_HIA_POP_FILE`、`PM25_HIA_SHP_DIR`。新结果放仓库外，保留原件，分享前脱敏日志。

## 参考资料

- `references/methodology.md`：归因分值、曲线比较及不确定性。
- `references/data_requirements.md`：字段与预处理说明。

## 模板

- `templates/calculate_pm25_deaths.R`：格点归因死亡计算。
- `templates/visualize_pm25_deaths.R`：死亡地图绘制。

## 示例

- `examples/workflow_pm25_hia.R`：从输入到绘图的适配示例。
