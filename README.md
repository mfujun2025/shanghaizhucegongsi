# 上海注册公司.com

上海地区公司注册信息与咨询服务站点，由上海宝山本地团队运营。

- 主站：上海注册公司.com（`xn--fhq55fzcr6i6s1crya.com`）
- 咨询电话：17652523536（微信同号）
- 地址：上海市宝山区萧云路501号

## 站点内容

| 页面 | 路径 | 说明 |
|---|---|---|
| 首页 | `/` | 三大决策点、费用构成、流程概览、地址挂靠、FAQ |
| 费用明细 | `/feiyong/` | 费用四项构成拆解、判断报价是否靠谱 |
| 办理流程 | `/liucheng/` | 7 步全流程与每步卡点 |
| 材料清单 | `/cailiao/` | 按地址来源分类的材料准备清单 |
| 地址挂靠 | `/dizhi-guakao/` | 园区挂靠判断方法、行业限制 |
| 办理时间 | `/shijian/` | 各环节耗时拆解 |
| 个体户/公司 | `/gezhong/` | 五个维度对比与选择方法 |
| 银行开户 | `/yinhang/` | 开户难点、材料、注意事项 |
| 代理记账 | `/dailijizhang/` | 费用影响因素、选择要点、常见坑 |
| 网上办理 | `/wangshang/` | 一网通办操作思路 |
| 常见问题 | `/faq/` | 30 条问答 |
| 关于我们 | `/women/` | 团队介绍与联系方式 |

## 技术栈

纯静态站点，无框架依赖：

- HTML5 + 原生 CSS（`css/style.css`）+ 原生 JS（`js/main.js`）
- Python 构建脚本：`build.py`（模板/共享组件）+ `gen_pages.py`（页面内容）
- `check_site.py`：站点自检（死链、元信息、必备元素、字数）

## 构建与自检

```bash
# 生成 js/main.js
python build.py

# 生成全部页面 + sitemap + robots
python gen_pages.py

# 自检（死链、meta、canonical、免责声明等）
python check_site.py

# 本地预览
python -m http.server 8080
```

## 部署

托管在 **Cloudflare Pages**，域名 DNS 也在 Cloudflare。

- 主站：`xn--fhq55fzcr6i6s1crya.com` → 本项目根目录
- 从站：`xn--fhq55fzcr6i6s1crya.cn` / `xn--fhq55fzcr6i6s1crya.xn--fiqs8s` → 用 `_redirects` 做 301 到主站

### 从域名 301 配置

把 `_redirects.example` 复制为 `_redirects`，内容：

```
/*  https://xn--fhq55fzcr6i6s1crya.com/:splat  301
```

> 301 是唯一能把从域名权重合并到主站的方式。不要用 JS 跳转或 meta refresh 替代。

## 内容原则

- 不写具体收费金额（费用因行业、经营范围、地址来源而异）
- 不做任何「保证通过」「绝对合规」类承诺
- 涉及政策、资质的内容只讲「去哪查、怎么判断」
- 每页保留免责声明

## 域名架构

三个域名**一主两从**，绝不建三个内容站（会被判站群作弊）：

```
上海注册公司.com          → 主站（全部内容）
上海注册公司.cn            → 301 到主站
上海注册公司.中国          → 301 到主站
```
