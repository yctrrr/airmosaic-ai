# 数据工作区、个人配置与登录凭据

每位成员共享代码和操作规范，分别管理数据、实际路径与认证状态。本文是所有 skill 的统一路径约定；具体脚本仍以其真实参数为准。

## 1. 四部分分别存放

```text
<local-root>/                         每个成员自行选择，位于 Git 仓库外
  <repository>/                       Git 跟踪的代码、skill、通用说明和配置模板
    config/examples/                  可公开的配置示例
  config/                             个人非秘密路径映射与偏好
    environment.ps1                   已审查的个人 PowerShell 配置
  local_workspace/                    数据与运行产物
    data_cache/<source>/              原始导出、缓存及来源元数据
    output/<run_id>/<tool>/            派生表、图、任务用模型配置副本
    runs/<run_id>/                    本地运行记录与验收结果
    temp/<run_id>/                    可清理的任务临时文件
  auth/                               受限的个人认证状态
    browser_profiles/csmar/            成员自己的 CSMAR 会话
    browser_profiles/ihme-gbd/         成员自己的 IHME 会话
```

目录名是示例，不包含机器专用路径。共享服务器上仍按成员划分 `config/`、`auth/` 和可写输出；公共数据可放到另一个经授权的只读数据根。代码仓库包含的 `config/examples/` 与仓库外的个人 `config/` 是不同位置。

| 根变量 | 存什么 | 谁读取 | 禁止存什么 |
|---|---|---|---|
| `AIRMOSAIC_LOCAL_WORKSPACE` | 数据、结果和本地运行记录 | 核心缓存服务；相关脚本参数/模块变量 | 登录状态、密码、密钥 |
| `AIRMOSAIC_CONFIG_DIR` | 私人路径映射、运行偏好 | 经成员审查后显式加载的配置/调用方 | 密码、token、cookie |
| `AIRMOSAIC_AUTH_DIR` | 必须落盘的专用浏览器 profile 等认证状态 | 已授权的浏览器工具或本地适配器 | 原始数据、计算结果、共享说明 |
| `GCAM_RELEASE_DIR` | 单独安装的模型发行包与既有模型输出 | GCAM 领域脚本 | 通用账号/凭据 |

后三类配置不由核心服务自动加载。设置 `AIRMOSAIC_AUTH_DIR` 不会启动浏览器或完成登录；设置 `GCAM_RELEASE_DIR` 不代表获准修改模型。核心 `.env` 文件也不会自动加载。

## 2. 首次配置和日常使用

1. 选定个人本地根，检查仓库与外层目录，保留已有数据和配置。
2. 按[配置示例](../config/examples/README.md)复制个人环境文件到仓库外，审查后显式加载。示例不保存密码，不自动覆盖既有个人配置。
3. 检查三类根彼此分开，且均不在任何 Git checkout 内。路径可不同于示例布局；不要将数据根设为认证目录的父目录。
4. 为每次执行选择唯一 `run_id`，将工具的 `--out-dir` 或模块输出变量显式映射到 `output/<run_id>/<tool>/`。配置文件名称不赋予执行权限。
5. 按来源检查认证状态；需要登录时由成员完成。工具只返回 `ready / needs_auth / permission_denied` 等状态和脱敏结果，不回传 cookie、token 或密码。这是接口约定，统一认证适配器尚未实现。
6. 共享前检查 diff、日志和附件；只交付经授权且脱敏的内容。个人完整记录可以保留本机路径，永远不应记录认证秘密。

Linux/macOS 的同等路径配置示例（在个人会话执行）：

```sh
export AIRMOSAIC_LOCAL_WORKSPACE="${XDG_DATA_HOME:-$HOME/.local/share}/airmosaic-ai/workspace"
export AIRMOSAIC_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/airmosaic-ai"
export AIRMOSAIC_AUTH_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/airmosaic-ai/auth"
mkdir -p "$AIRMOSAIC_LOCAL_WORKSPACE" "$AIRMOSAIC_CONFIG_DIR" "$AIRMOSAIC_AUTH_DIR"
chmod 700 "$AIRMOSAIC_AUTH_DIR"
```

Windows 的认证目录使用个人账户目录权限，并按实际协作需要限制其他账户访问；不要为所有成员授予读写。操作系统目录权限和秘密存储分别管理；同一系统身份下的 agent 通常拥有相同文件权限。

## 3. 不同凭据分别管理

| 类型 | 推荐保管与调用 | 维护方式 |
|---|---|---|
| GitHub HTTPS 登录 | Git Credential Manager；Windows 后端为系统凭据管理器 | 成员本人认证，个人 Git 环境使用；不放工作区 |
| GitHub SSH 登录 | 个人 SSH 私钥存储与 ssh-agent；远端只登记公钥 | 密钥按设备/用途区分，私钥不复制给协作者 |
| 网站密码与多因素认证 | 本人的密码管理器和交互式登录 | 不让 agent 收集密码、恢复码或批量尝试账号 |
| CSMAR / IHME 登录态 | `${AIRMOSAIC_AUTH_DIR}/browser_profiles/<service>/` | 每成员/服务独立；账号变化或会话过期时重新登录，不共享 profile |
| API key / token | 系统或团队秘密管理服务；工具运行时按需读取/注入 | 限定权限、用途和有效期；撤销/轮换由有权限者执行 |
| GitHub Actions 自动化秘密 | Repository / Environment / Organization Secrets | 使用适合自动化的身份和最小授权，不上传个人浏览器会话 |

环境变量是传递方式，不是加密保管方式。不得在 shell 命令、配置示例、`AGENTS.md`、`SKILL.md`、测试快照或日志中写出秘密值。确实只能使用本地秘密文件时，由维护者另行确定受限路径、权限和读取方式；不自动新增 `secrets.json` 或把密码写进 `.env`。

浏览器 profile 也属于敏感认证材料。专用会话只访问任务所需站点，不复用包含个人邮箱、网盘等无关账号的日常浏览器配置；调试端点仅在本机授权会话中使用，不对外开放。程序退出不等于认证状态已销毁。

参考：[GitHub 凭据缓存](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git)、[Actions Secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)、[浏览器认证状态风险](https://playwright.dev/docs/auth)。

## 4. 各 skill 的映射

| Skill | 输入/缓存 | 输出及配置 | 认证 |
|---|---|---|---|
| WorldPop | 工作区 `data_cache/worldpop/`；脚本显式 `--root` | 元数据/原始下载在该缓存；派生分析进任务输出 | 公开发现通常无需个人凭据 |
| CSMAR | 工作区 `data_cache/csmar/` | 企业处理器显式 `--out-dir`；个人路径映射在配置根 | 认证根 `browser_profiles/csmar/` |
| 工业年鉴 | 工作区 `data_cache/industrial_yearbook/` 或授权只读源 | 模板需适配输出；任务配置副本在本次输出目录，长期私人路径映射在配置根 | 无统一在线登录实现 |
| IHME GBD | 工作区 `data_cache/gbd_health/` | `--out` 指定原始 CSV；认证状态不写 sidecar；派生计算进任务输出 | 认证根 `browser_profiles/ihme-gbd/`，已有脚本连接该浏览器的本机 CDP |
| GCAM 总入口 | `GCAM_RELEASE_DIR` 只读引用 | 按子 skill 显式映射输出 | 当前本地分析不要求网站凭据 |
| GCAM 输出结构 | 模型已有数据库布局 | 显式 `--output-dir`，使用任务输出 | 无 |
| GCAM 配置 | 模型原始配置只读参考 | 修改写入任务副本；不要覆盖发行包 | 无 |
| GCAM 提取 | 模型已有数据库布局 | `--out-dir` / `UNIT_PRICE_OUT_DIR` 指向任务输出 | 无 |
| 健康影响 | 浓度、人口、基线死亡率、风险曲线分别映射 | `PM25_HIA_*` 输入变量与 `PM25_HIA_OUTPUT_DIR`；长期路径放个人配置 | 数据获取认证交给相应 acquisition skill |

已有模板可能默认把文件写回输入树，或在 source 时重设变量，不能只改目录名就直接执行。年鉴的 YAML 是待适配配置示例，并非自动加载器；GCAM 部分脚本有工作目录回退，新调用必须显式给出输出目录。完整限制见[数据获取](usage/data-acquisition.md)和[模型分析](usage/model-analysis.md)。

## 5. 旧目录与多人交付

- 既有 `outputs/`、`logs/`、`temp/` 不自动移动或删除。新任务使用 `output/<run_id>/`、`runs/<run_id>/`、`temp/<run_id>/`，旧任务的恢复仍引用原位置。
- 旧的工作区 `secrets/`、`.browser_profiles/` 停止作为新认证存储。若确有既有会话，先关闭所属浏览器并确认范围，由本人选择重新登录；不让 agent 复制整个 profile 或打印凭据来迁移。空占位目录无需删除。
- 数据备份仅包含获准的数据和结果；认证目录不进入数据归档、Issue、PR、共享网盘或跨成员同步。秘密备份使用专门加密方案，不混入普通配置备份。
- `.gitignore` 是防误提交措施，不提供加密或访问限制；已跟踪文件仍需单独处理。疑似泄漏只报告位置与类别，真实秘密须撤销/轮换；不擅自改写历史。
- 工具查询已对声明的路径进行只读前置检查，并只输出逻辑路径；不会读取认证文件。新增 [run-tool](usage/run-tool.md) 对已审查适配器实施任务路径前置检查、环境白名单与脱敏记录。个人根目录只做元数据检查，不把 CONFIG_DIR/AUTH_DIR 或凭据传给子进程；GBD 通过已有本机授权会话工作。原脚本直接调用不经过这些检查，凭据代理和 OS 沙箱尚未实现。
