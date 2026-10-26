# ERA5 与 CAMS：获取方式和下载步骤

复核日期：2026-10-26。本文是人工操作参考，提供 3 份非秘密请求示例；没有新增工具注册、数据声明或 run-tool 下载适配器。`list-tools`/`list-datasets` 不会因新增文档而出现 ERA5/CAMS；官方 dataset ID 也不是工具 ID。

从 [ERA5 skill](../../skills/data_acquisition/03_atmospheric_transport/era5/SKILL.md)或 [CAMS skill](../../skills/data_acquisition/03_atmospheric_transport/cams/SKILL.md)进入。方法维护只查看接口、说明及合成输入，不读取原始数据；实际下载另需明确变量、地区、时段、目标目录与允许的网络操作。

## 1. 先选对产品和门户

| 需求 | 官方 dataset ID | 门户和时间含义 | 示例 |
|---|---|---|---|
| 近地表/单层气象 | `reanalysis-era5-single-levels` | CDS；所选日期和时次 | [单层请求](../../config/examples/copernicus/era5-single-levels.request.json) |
| 指定气压层气象 | `reanalysis-era5-pressure-levels` | CDS；额外选择 pressure_level | 当前网页生成，不直接复用单层请求 |
| 历史全球大气成分 | `cams-global-reanalysis-eac4` | ADS；再分析日期和时次 | [EAC4 请求](../../config/examples/copernicus/cams-eac4.request.json) |
| 全球大气成分预报 | `cams-global-atmospheric-composition-forecasts` | ADS；起报日期/时次 + leadtime_hour | [预报请求](../../config/examples/copernicus/cams-forecast.request.json) |

ERA5 单层大气再分析通常为逐小时、0.25°；EAC4 为每 3 小时、0.75°。具体变量和产品另核对，不能外推到海浪、集合或其他 CAMS 产品。EAC4 从 2003 年起，全球预报目录从 2015 年起；结束日期随更新变化，以当前表单为准。见 [ERA5 产品页](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview)、[EAC4 产品页](https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4?tab=overview)及[预报产品页](https://ads.atmosphere.copernicus.eu/datasets/cams-global-atmospheric-composition-forecasts?tab=overview)。

ERA5-Land、ERA5 日统计、模式层和欧洲区域 CAMS 均须从各自产品页重新生成请求；本文不提供它们的现成下载模板。

### 与 PM2.5 站点技能的分工

| 资料 | 本项目入口与用途 | 向下游交接时必须保留 |
|---|---|---|
| ERA5 气象网格 | 本指南及 ERA5 skill；气象背景/协变量，不能当站点污染观测 | 变量、单位、瞬时/累计语义、UTC 时次、层次和网格 |
| CAMS 大气成分网格 | 本指南及 CAMS skill；再分析或预报，不能标为原始站点实测 | 产品类型、单位、垂直坐标、网格；预报另保留起报时间、时效和有效时间 |
| PM2.5 站点记录 | [站点技能](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md)；观测获取、整理与质控 | 来源、站号、站点表有效期、原时区/小时标签、平均时段和加工标记 |

三者主目录均在 03，04 按需引用，不复制流程。后续若匹配网格与站点，须另有明确的数据读取/处理范围，并说明空间匹配、坐标参考、时间区间、单位转换、缺失和代表性；不把网格插值值改称站点实测，也不默认可直接输入健康模型。站点来源的时区尚需核验，不能沿用 ERA5 的 UTC 假设。

## 2. 账号、依赖与三类存储

1. 成员本人分别打开 CDS/ADS，确认可登录并在目标数据集页面接受条款。能网页登录不表示已完成 API 授权；许可未接受也会阻止 API 请求。[CDS API 指南](https://cds.climate.copernicus.eu/how-to-api)、[ADS API 指南](https://ads.atmosphere.copernicus.eu/how-to-api)。
2. 网页下载不要求安装 Python。API 路线需独立、已审查的 Python 环境和 `cdsapi`；按当前官方指南安装 `cdsapi>=0.7.7`，并在任务记录中固定实际版本。本次未安装依赖。
3. NetCDF 验收可用 xarray 加 netCDF4/h5netcdf；GRIB 验收可用 ecCodes/cfgrib。这些不是下载本身的必要依赖，也未加入核心依赖。
4. 使用[统一路径约定](../storage-and-credentials.md)，先确认三类根存在、互不包含且位于所有 Git checkout 外，检查符号链接/目录联接解析后的实际位置。不要把认证目录或配置目录当下载目标。

| 内容 | 位置与管理 |
|---|---|
| 非秘密请求、个人路径和批次计划 | `AIRMOSAIC_CONFIG_DIR/copernicus/`，只显式读取本次文件 |
| 新下载文件 | `AIRMOSAIC_LOCAL_WORKSPACE/output/<run_id>/era5/` 或 `.../cams/` |
| 验收后获准发布的缓存 | `AIRMOSAIC_LOCAL_WORKSPACE/data_cache/era5/` 或 `.../cams/`，不自动搬运 |
| 本地请求/验收摘要 | `AIRMOSAIC_LOCAL_WORKSPACE/runs/<run_id>/`，不写认证秘密或签名链接 |
| 网页认证会话（如使用专用浏览器） | `AIRMOSAIC_AUTH_DIR/browser_profiles/copernicus-cds/` 或 `copernicus-ads/` |
| API 访问令牌 | 系统/团队秘密管理器；API 运行时按需传入，不写 CONFIG_DIR、AUTH_DIR 的明文秘密文件或仓库 |

官方教程展示 `.cdsapirc` 方式，但项目规则不允许自动创建明文秘密文件。本项目采用显式 endpoint 和运行时令牌：CDS 为 `https://cds.climate.copernicus.eu/api`，ADS 为 `https://ads.atmosphere.copernicus.eu/api`，不沿用旧 `/api/v2` 或旧 UID 拼接方式。不要扫描已有 `.cdsapirc`。明确传入 URL 和 key 可避免该客户端因缺参回退读取默认凭据文件，见 [cdsapi 实现](https://github.com/ecmwf/cdsapi/blob/master/cdsapi/api.py)。

令牌由本人在自己的终端输入，或由另行审查的秘密管理器集成注入内存；不要在聊天、命令行参数、请求 JSON、环境配置模板或日志中提供值。项目尚未实现自动凭据代理；环境变量也不是加密存储。

## 3. 网页下载：适合首次核对

1. 从上表进入对应数据集的 Download 页面。
2. 选择变量、日期、时次、区域和格式。气压层加层次；CAMS 预报加起报时次和预报时效。区域顺序核对为 **北、西、南、东**，不是经纬度交错；跨日期变更线的范围单独设计。
3. 展开 **Show API request code**，保存其中的非秘密 dataset/request 到个人配置。与公开示例对照，检查是否无意选择了全球、全部层次或全部年份。
4. 在获授权的下载任务中提交表单，等待服务处理后将文件保存到本次任务输出目录；如浏览器落在系统下载目录，核对文件后再按授权移动，不扫描其他下载。
5. 不分享账户页面截图、下载签名 URL 或浏览器状态。完成下文验收后再扩大请求。

示例只选公开的演示日期、区域和少量时次，不代表用户研究范围。ERA5/EAC4 示例都只有一个时次，不能据此计算日均。CAMS 预报历史请求可能进入慢速归档队列；不要因等待而反复提交同一任务。

## 4. Python API：人工适配示例

先将选中的 `config/examples/copernicus/*.request.json` 复制到个人 `CONFIG_DIR/copernicus/`，不覆盖已有文件；按当前网页核对内容。文件只包含官方 request，不包含 endpoint、令牌或输出路径，也不是 `run-tool --params-file` schema。

以下代码供成员在已审查的个人任务脚本中使用，**运行会提交下载并写文件，没有 dry-run**。不是仓库中的下载器；执行前必须完成上述路径和范围检查。示例按提供的 GRIB 请求编写，修改格式时要同步目标扩展名和验收方式。

```python
import json
import os
import warnings
from getpass import GetPassWarning, getpass
from pathlib import Path
from uuid import uuid4

import cdsapi

selection = "era5-single-levels"  # 或 cams-eac4 / cams-forecast
choices = {
    "era5-single-levels": (
        "https://cds.climate.copernicus.eu/api",
        "reanalysis-era5-single-levels", "era5"
    ),
    "cams-eac4": (
        "https://ads.atmosphere.copernicus.eu/api",
        "cams-global-reanalysis-eac4", "cams"
    ),
    "cams-forecast": (
        "https://ads.atmosphere.copernicus.eu/api",
        "cams-global-atmospheric-composition-forecasts", "cams"
    ),
}
endpoint, dataset, source = choices[selection]

def inside_git(path):
    return any((parent / ".git").exists() for parent in (path, *path.parents))

# 只核对路径及文件元数据，不读取个人配置目录或认证目录的内容。
try:
    roots = [Path(os.environ[name]).resolve(strict=True) for name in (
        "AIRMOSAIC_CONFIG_DIR", "AIRMOSAIC_LOCAL_WORKSPACE", "AIRMOSAIC_AUTH_DIR"
    )]
except (KeyError, OSError, RuntimeError, ValueError):
    raise SystemExit("Three existing, explicitly configured roots are required") from None
if any(not root.is_dir() or inside_git(root) for root in roots):
    raise SystemExit("Roots must be directories outside Git checkouts")
if any(left.is_relative_to(right) or right.is_relative_to(left)
       for i, left in enumerate(roots) for right in roots[i + 1:]):
    raise SystemExit("Workspace, settings and authentication roots must be separate")
config_root, workspace, auth_root = roots
request_file = (config_root / "copernicus" / f"{selection}.request.json").resolve(strict=True)
if not request_file.is_relative_to(config_root) or inside_git(request_file):
    raise SystemExit("Request must remain inside settings and outside Git checkouts")
request = json.loads(request_file.read_text(encoding="utf-8"))
if not isinstance(request, dict) or request.get("data_format") != "grib":
    raise SystemExit("This example requires a reviewed GRIB request")

run_id = uuid4().hex
target_dir = (workspace / "output" / run_id / source).resolve()
if not target_dir.is_relative_to(workspace) or inside_git(target_dir):
    raise SystemExit("Output must remain inside workspace and outside Git checkouts")
target_dir.mkdir(parents=True, exist_ok=False)
target = target_dir / "download.grib"

# 仅由本人在终端输入；无法隐藏输入时失败，不回退到回显。
warnings.simplefilter("error", GetPassWarning)
access_token = getpass("Personal access token for the selected service: ").strip()
if not access_token:
    raise SystemExit("No token supplied")
try:
    client = cdsapi.Client(url=endpoint, key=access_token, verify=True, quiet=True, debug=False)
    client.retrieve(dataset, request, str(target))
except Exception:
    raise SystemExit("Download failed; inspect the service status privately before retrying") from None
finally:
    del access_token
print("Transfer returned; verify the file before using or publishing it")
```

这段示例检查三根存在且互不包含、解析后的请求/输出位置，以及祖先目录的 `.git` 标记；这些预检不能防止检查后的路径替换，也不提供 OS 隔离、请求业务验证、完整超时策略、续传或脱敏回执。删除变量不保证从进程内存清除令牌；客户端还可能持有它。`quiet=True` 不是日志脱敏保证，不把原始客户端输出、异常堆栈或本机路径直接发布。无需凭据的检查只能验证合成流程，不能证明登录、条款、排队或下载可用。

不要把这一方式用于绕过现有工具失败。ERA5/CAMS 当前没有 runner 适配器，人工参考与统一执行入口是分开的能力；未来接入时需先实现凭据获取、参数 schema、路径校验、受控重试和脱敏回执。

## 5. 请求参数和旧脚本迁移

| 项目 | 核对规则 |
|---|---|
| ERA5 单层 | `product_type`、`variable`、`year/month/day`、`time`、`area`；压力变量另选气压层数据集和 `pressure_level` |
| EAC4 | `variable`、`date`、`time`、`area`；多层变量额外选所需层次，单层 PM2.5 示例不加层字段 |
| CAMS 预报 | 在日期/时次上增加 `type: ["forecast"]` 和 `leadtime_hour`；有效时间 = 起报时间 + 时效，保留两者 |
| 文件格式 | 本次公开表单中三者都用 `data_format`；ERA5 支持 `grib/netcdf` 和独立 `download_format`，两个 CAMS 产品支持 `grib/netcdf_zip`。不要把旧 `format: netcdf` 机械复制过去 |
| 批量范围 | 先以少量变量、一天或更小范围验证，再按日期/变量/层次分批；使用日历生成日期，避免无效日期组合 |
| 重试与续传 | 先看门户任务状态再处理超时；429/服务拥塞按官方提示退避，不无界并发。记录待办/完成/失败批次，验证已存文件后再决定重下 |

本地历史脚本曾用 R 按固定行号替换日期来生成 Python 文件。可复用的是日期分批思路，不能复用硬编码行号、旧凭据设置或专用路径；应将日期作为请求字段并保存批次清单。本次没有运行或迁移旧下载脚本，也没有据旧 NRT 命名推断实际 CAMS 数据集。

表单字段依据公开目录元数据的 `form` 链接核对：[ERA5 目录元数据](https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-single-levels)、[EAC4 目录元数据](https://ads.atmosphere.copernicus.eu/api/catalogue/v1/collections/cams-global-reanalysis-eac4)、[CAMS 预报目录元数据](https://ads.atmosphere.copernicus.eu/api/catalogue/v1/collections/cams-global-atmospheric-composition-forecasts)。表单和组合约束会变化；这些公开 GET 不是下载请求，也未验证账户对某个组合的访问权限。

## 6. 下载后验收与常见问题

1. **文件完整性**：核对文件签名和实际容器，排除错误 HTML、零字节和未完成传输；ZIP 先检查成员路径后在任务目录解压，不向上层写入。不仅看扩展名或成功退出。
2. **维度完整性**：核对变量、日期/时次数量、层次、区域和网格坐标，保留缺失与重复报告。不要假定时间坐标总叫 `time`，也不要默认维度顺序固定。
3. **物理含义**：读取变量自身单位和累计时段。PM2.5 的质量浓度、气体混合比、柱总量和 AOD 分开；不能把所有 CAMS 变量统一乘同一换算系数。ERA5 的瞬时量和累计量分开处理。
4. **时间口径**：保留 UTC；本地日平均明确时区、跨日边界及覆盖。CAMS 预报同一有效时间可能对应多次起报，先确定选择规则，不把重叠记录直接平均。
5. **交接与记录**：保存非秘密请求副本、dataset ID、获取日期、客户端版本、工作区相对文件名、大小/校验摘要、验收结论与限制。预报记录起报/时效和产品版本信息；ERA5 近期数据记录初步/最终发布状态。清单不得包含令牌、授权头、签名 URL、私人用户名或绝对路径。此处为人工记录约定，不会自动生成 `run-tool` 回执。

| 现象 | 处理顺序 |
|---|---|
| 401/403 | 本人检查门户、令牌和所选数据集条款；不打印令牌，也不反复尝试账户 |
| dataset/字段不存在 | 确认 CDS 与 ADS 地址、dataset ID 和当前表单；更新请求，不盲目删字段 |
| 请求过大、排队或超时 | 检查服务/已有任务状态，按允许限制拆批；磁带归档可能较慢，不能以重复提交代替等待 |
| NetCDF 读取失败 | 检查是否实际为 ZIP/GRIB/错误页面；必要时使用单独 GRIB 请求或更小转换批次，不简单改后缀 |
| TLS/代理问题 | 由环境维护者修复证书或代理；不关闭 TLS 校验，不记录代理口令 |
| 无法直接给 GEOS-Chem/健康模型使用 | 分别适配网格、层次、物种、单位、时间及模型版本；下载成功不等于模型输入合格 |

补充依据：[ERA5 官方下载说明](https://confluence.ecmwf.int/spaces/CKB/pages/129135000/How+to+download+ERA5+from+the+Climate+Data+Store+CDS)、[ERA5 日统计说明](https://confluence.ecmwf.int/spaces/CKB/pages/462888259/ERA5+family+post-processed+daily+statistics+documentation)、[ECMWF CAMS 教程](https://github.com/ecmwf-training/cams-training/blob/main/da-read-write.ipynb)。教程中的历史参数和输出只作理解参考，本文示例按复核时的公开表单编写。
