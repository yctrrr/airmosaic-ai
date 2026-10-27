# 企业财务、年报与环境披露

**状态**：本地存在不同来源的采集/处理脚本，近期有省级披露续采和主体识别试点记录；本次只读核对，不启动采集或宣称全部省份已完成。

| 来源 | 数据与入口边界 | 登录/依赖 |
|---|---|---|
| CSMAR / RESSET | 授权数据库表；基础信息、财务、子公司关系按表区分 | 本人机构权限；本地处理需要相应 Python/R 依赖 |
| 上市公司公告 | 年报、半年报、ESG 等正文与附件；与数据库财务表分别留来源 | 公开页面或任务授权会话；按具体站点核对 |
| 省级环境披露平台 | 企业年度/临时报告、结构化正文及附件 | requests 或浏览器；各省接口、权限和限流独立 |

## 操作步骤

1. 固定省份、年份、企业范围与所需报告类型。主体 ID、企业年、报告版本分别标识。
2. 先取得列表，再取详情/正文/附件；只有列表或附件链接时保留对应状态，不计为完整报告。
3. 网络采集保留可恢复队列和每次尝试记录，区分未发现、权限限制、暂时错误、已取得和已验证。出现访问挑战时停在该状态，交由已授权的人工或现有支持流程处理，不规避访问限制。
4. 验证报告中的企业、期间、正文和附件一致；保存原件摘要/哈希，避免重复版本覆盖。
5. 只对有证据的结果更新中心索引。已有队列由所属流程维护，不手工批量改数据库或重新入队全部企业。

## AirMosaic 与本地项目的区别

- `csmar_browser_download` 是参考流程；`csmar_process_company_info` 可通过 run-tool 处理已下载的企业基础信息 ZIP，不能替代所有财务表读取或省级披露爬虫。见 [CSMAR skill](../../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL.md)。
- 本次检查了省级项目说明、`fetch_nonlisted_env_disclosure_hainan_public_api.py` 的局部入口，以及其他省份/上市报告脚本的存在性。没有把某省样本成功推广为其他省可用。
- 当前省份进度应以所属任务的队列和最近验收为准；旧 README 和历史聊天中的数量不作为本库当前进度。
- 企业名称、地址、识别证据、原始报告及签名下载 URL 留在工作区，不进入共享方法卡。采集权限不等于把内容发往外部模型服务的权限。

身份合并、生产量提取和财务校准见[企业面板方法](enterprise_panels.md)。

## 阶段与 Skill 映射

主目录：01_socioeconomic_natural_change；适用阶段：01_socioeconomic_natural_change。对应 [csmar](../../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL.md)、[enterprise-disclosure](../../skills/data_acquisition/01_socioeconomic_natural_change/enterprise-disclosure/SKILL.md)。执行状态以本文及真实工具 manifest 为准；没有 tool_id 的方法只供指导。
