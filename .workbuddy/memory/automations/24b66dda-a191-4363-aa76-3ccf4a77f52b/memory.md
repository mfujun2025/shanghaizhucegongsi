# 日更自动化执行记录

## 2026-09-28（首次执行）
- 状态：✅ 全流程成功（校验/构建/自检/打包/部署/提交推送 一次通过）
- 选题：`daiban-fee-market`，core「上海注册公司代办一般多少钱」，簇 fee，角度「代办费为什么差这么多+识别报价陷阱」
- 产出：`_content/daiban-fee-market.md`，正文 2433 中文字，7 个 H2，6 条 FAQ，2 张对照表
- 主词「上海注册公司」出现 2 次，密度 0.468%（阈值 0.3–0.9%，无告警）
- 部署：Cloudflare Pages ✅ https://b703cbff.shanghaizhucegongsi.pages.dev ；线上文章页 HTTP 200
- 提交：`cd12373` 已推送 main
- 选题池：已用 2 / 共 70，待用 68；下一篇 `annual-cost`「上海注册公司每年要交什么钱」
- 备注：无异常、无失败步骤；config.local.json 未进入 git 暂存区（gitignore 正常）

## 2026-09-29（第 2 次执行）
- 状态：✅ 发布链路全流程成功（校验/构建/自检/打包/部署/提交推送 一次通过）
- 选题：`annual-cost`，core「上海注册公司每年要交什么钱」，簇 fee，角度「年检/记账/报税的刚性支出构成」
- 产出：`_content/annual-cost.md`，正文 3118（len），8 个 H2，7 条 FAQ，2 张对照表，4 个引用块
- 主词「上海注册公司」出现 4 次，密度 0.770%（阈值 0.3–0.9%，无告警）
- 部署：Cloudflare Pages ✅ https://758d3e28.shanghaizhucegongsi.pages.dev ；线上文章页 HTTP 200
- 提交：`40b5c4c` 已推送 main
- 选题池：已用 3 / 共 70，待用 67；下一篇 `zero-declaration-cost`「上海注册公司零申报要花钱吗」
- 经验（已沉淀到 .workbuddy/memory/MEMORY.md）：`_len` 含 HTML 标签开销，≈ 实际字数 ×1.37；
  单个主词 ≈ 12 个 `_len`；长文主词上限 ≈ `0.00075 × _len`；**删正文会反向抬高密度**，只能减主词次数
- ⚠️ 未解决（非本次任务失败，属既有配置缺口）：主域 `xn--5nqv0mk2lgd.com` 经阿里/腾讯 DoH 判定为
  **NXDOMAIN（com. 注册局层面无 NS 委派）**，站点当前仅 pages.dev 可访问。已记入项目 MEMORY.md 待老孟配置
  〔2026-10-02 更正：**此结论作废**，`xn--5nqv0mk2lgd` 是记错的 punycode，实际域名见文末〕
- 备注：config.local.json 未进入 git 暂存区（gitignore 正常）；无失败步骤

## 2026-09-30（第 3 次执行）
- 状态：✅ 发布链路全流程成功（校验/构建/自检/打包/部署/提交推送 一次通过）
- 选题：`zero-declaration-cost`，core「上海注册公司零申报要花钱吗」，簇 fee，角度「零申报的费用与风险双向说明」
- 产出：`_content/zero-declaration-cost.md`，正文 ≈3250（len）/ 约 2370 实际中文字，8 个 H2，3 张对照表，3 个引用块，6 条 FAQ
- 主词「上海注册公司」出现 4 次，密度 ≈0.738%（阈值 0.3–0.9%，无告警）
- 部署：Cloudflare Pages ✅ https://312d7f99.shanghaizhucegongsi.pages.dev ；线上文章页 HTTP 200
- 提交：`2f5f898` 已推送 main
- 选题池：已用 4 / 共 70，待用 66；下一篇 `刻章收费`「上海注册公司刻章要收费吗」
- 备注：config.local.json 未进入 git 暂存区（gitignore 正常）；无失败步骤
- ⚠️ 仍待老孟处理（既有缺口，非本次失败）：主域 `xn--5nqv0mk2lgd.com` 注册局层面无 NS 委派，站点当前仅 pages.dev 可访问
  〔2026-10-02 更正：**此结论作废**，原因同上，实际域名见文末〕

## 2026-10-02（第 6 次执行；注：2026-10-01 曾跑过一轮但未写记忆、未提交）
- 状态：✅ 发布链路全流程成功（校验/构建/自检/打包/部署/提交推送 一次通过）
- 选题：`capital-paid-in`，core「上海注册公司注册资本要实缴吗」，簇 fee，角度「认缴制怎么理解+认缴额的责任含义」
- 产出：`_content/capital-paid-in.md`，`_len` 3095（≈2259 实际中文字），7 个 H2，3 张对照表，3 个引用块，6 条 FAQ
- 主词「上海注册公司」出现 3 次，密度 **0.582%**（理想区间 0.3–0.6，零 warning）
- 部署：Cloudflare Pages ✅ https://96f1b5b7.shanghaizhucegongsi.pages.dev ；文章页 HTTP 200
- 提交：`ddcedf3` 已推送 main（25 files changed）
- 选题池：已用 6 / 共 70，待用 64；下一篇 `bank-account-fee`「上海注册公司银行开户要多少钱」
- 异常处理：开工时发现上一轮（10-01）的 `seal-fee.md` + `articles/seal-fee/` 停留在工作区未提交 → 本轮 `git add -A` 一并提交入库
- 备注：config.local.json 未进入 git 暂存区（gitignore 正常）；~~主域 DNS 缺口仍待老孟处理~~（见下条更正）
- 校准补充：任务书里写的「主词 6–12 次」与代码实测公式冲突（6 次 ≈1.16% 会触发偏高告警）。
  以 `build_articles.py` 的 `count×6/_len×100` 为准：`_len`≈3100 时正确区间是 **2–3 次**（本轮用 3 次，落在理想带内）

## 2026-10-02 追加：域名误判更正（老孟指出）
- 老孟指出域名是「上海注册公司.com」，不是此前笔记里的 `xn--5nqv0mk2lgd.com` —— 他是对的
- **正确 punycode：`上海注册公司.com` = `xn--fhq55fzcr6i6s1crya.com`**
  （编码方法以 中国/测试/公司 三个已知样本交叉验证过；旧串解出来是「哾件慫慏」，根本不是这个域名）
- 实测三域名：`.com` 首页+文章页 HTTP 200；`.cn`、`.中国` 均 **301 → .com**
  → **主域与两个从域全部正常，此前"无 NS 委派"是查错域名得出的伪结论，无需老孟配置**
- 站点产物本身无问题：全站 126 处都是正确 punycode，错的只是记忆笔记
- 铁律（已入 MEMORY.md）：punycode 一律当场用代码算，绝不凭记忆手写
- 排查套路：本机 DNS 解析不了这类中文域名，用 **DoH 取 IP → `curl --resolve 域名:443:IP`** 验证

## 2026-10-04（第 7 次执行；同日 site 目录内已另有一篇手工稿 bookkeeping-yearly-fee）
- 状态：✅ 发布链路全流程成功（校验/构建/自检/打包/部署/提交推送 一次通过，零 error 零 warning）
- 选题：`fee-negotiation`，core「上海注册公司费用可以砍价吗」，簇 fee，角度「哪些费用有弹性、哪些没有」
- 产出：`_content/fee-negotiation.md`，实际中文 ≈2232 字，8 个 H2，3 张对照表，2 个引用块，6 条 FAQ
- 主词「上海注册公司」正文仅数次（含 frontmatter/正文开头），构建校验与自检均无告警通过
- 部署：Cloudflare Pages ✅ https://14525a6b.shanghaizhucegongsi.pages.dev ；文章页 HTTP 200（24095B）
- 提交：`4841234` 已推送 main（15 files changed）；`git ls-remote origin main` 比对一致
- 选题池：已用 9 / 共 70，待用 61；下一篇（status 提示）`annual-cost`
- 备注：config.local.json 未进入 git 暂存区（gitignore 正常）；无失败步骤、无异常

## 2026-10-05（第 8 次执行）
- 状态：✅ 发布链路全流程成功（校验/构建/自检/打包/部署/提交推送 一次通过，零 error 零 warning）
- 选题：`free-agency-trap`，core「上海注册公司免费代办靠谱吗」，簇 fee，角度「免费模式背后的商业逻辑与判断方法」
- 产出：`_content/free-agency-trap.md`，正文 2536 中文字（含表格/FAQ），7 个 H2，2 张对照表，4 个引用块，6 条 FAQ
- 主词「上海注册公司」出现 4 次，密度 0.844%（_len=2843；阈值 0.3–0.9，零告警，但贴近上限）
- 部署：Cloudflare Pages ✅ https://3dfa9294.shanghaizhucegongsi.pages.dev ；文章页 HTTP 200（23500B），主域 .com 同路径也 200
- 提交：`e02da14` 已推送 main（26 files changed）；`git ls-remote origin main` 比对一致
- 选题池：已用 10 / 共 70，待用 60；下一篇 `process-duration`「上海注册公司流程需要几天」（簇 process）
- 新发现（已补进 MEMORY.md）：**H2 里写核心词会被计两次**——锚点 id 由 slugify_anchor 生成，也含核心词，
  而密度是按 `_body` HTML 原文 count 的。4 次里就有 2 次来自那个 H2（id + 文本）
- 备注：config.local.json 未进入 git 暂存区（gitignore 正常）；无失败步骤、无异常

## 2026-10-06（第 9 次执行）
- 状态：✅ 发布链路全流程成功（校验/构建/自检/打包/部署/提交推送 一次通过，零 error 零 warning）
- 选题：`process-duration`，core「上海注册公司流程需要几天」，簇 process（**该簇首篇**），角度「各环节耗时明细与卡点」
- 产出：`_content/process-duration.md`，`_len`=2892（≈2110 实际中文字，落在 1800–2500 目标带），9 个 H2，3 张对照表，4 个引用块，6 条 FAQ
- 主词「上海注册公司」出现 3 次（首段 1 + 一个 H2 双计 2），密度 **0.622%**（阈值 0.3–0.9，零告警）
- 定稿过程：初稿 `_len`=2274 / 密度 0.792%（偏高）→ 补两段正文与一个新 H2 抬到 `_len`=2692（0.669%）→ 再补「整体节奏怎么估」段到 2892（0.622%）。印证：**加正文可同时拉字数、降密度，是修"密度偏高"的正解**
- 本次系数核对：`_len`/实际中文 = 2892/2110 ≈ 1.37，与此前校准一致，无需修正
- 部署：Cloudflare Pages ✅ https://e07cb776.shanghaizhucegongsi.pages.dev ；文章页 HTTP 200（22823B），标题/H2/6 条 FAQ/电话均已线上核到
- 提交：`5ff66ea` 已推送 main（30 files changed）；`git ls-remote origin main` 比对一致
- 选题池：已用 11 / 共 70，待用 59；下一篇 `name-check-apply`「上海注册公司核名怎么操作」（簇 process）
- 备注：config.local.json 未进入 git 暂存区（gitignore 正常）；无失败步骤、无异常
