#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海注册公司.com 静态站构建脚本
=================================
职责：
  1. 统一生成所有页面的 <head> / header / footer（避免手写不一致）
  2. 注入内链、CTA 横条、免责声明
  3. 生成 sitemap.xml 和 robots.txt

用法：python build.py
输出：直接写入本目录（各子目录的 index.html）
"""
import os
import json
import hashlib
import html as html_mod
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://xn--fhq55fzcr6i6s1crya.com"
PHONE = "17652523536"
PHONE_TEL = "17652523536"
BUILD_DATE = date.today().isoformat()

# ---------------------------------------------------------------
# 静态资源指纹（内容哈希）
# ---------------------------------------------------------------
# 为什么不直接叫 main.js：
#   旧版 main.js 是「演示模式」（弹提示但不发送），而 Cloudflare Pages 给它
#   发的是 Cache-Control: public, max-age=14400（4 小时）。用户浏览器缓存了旧版，
#   即使站点已更新，用户点提交也会「看着成功、实际没发出去」——真实事故。
#   加内容哈希后，文件内容一变，URL 就变，彻底绕开旧缓存。
_AST_CACHE = {}


def asset_ver(rel_path):
    """按文件内容算 8 位哈希；同一份内容多次调用结果稳定"""
    if rel_path in _AST_CACHE:
        return _AST_CACHE[rel_path]
    full = os.path.join(BASE_DIR, rel_path)
    try:
        with open(full, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()[:8]
    except OSError:
        h = ""
    _AST_CACHE[rel_path] = h
    return h


def asset_url(page_path, rel_path):
    """带指纹的资源 URL（相对当前页）。无指纹时退化为原路径，不破坏构建"""
    v = asset_ver(rel_path)
    suffix = ("?v=" + v) if v else ""
    return rel(page_path, rel_path) + suffix

# ---------------------------------------------------------------
# 询单接收端配置（优先级：config.local.json > 环境变量 > 空=演示模式）
# ---------------------------------------------------------------
CONFIG_LOCAL = os.path.join(BASE_DIR, "config.local.json")
LOCAL_CFG = {}
if os.path.isfile(CONFIG_LOCAL):
    try:
        with open(CONFIG_LOCAL, "r", encoding="utf-8") as _f:
            LOCAL_CFG = json.load(_f) or {}
    except Exception as _e:
        print("  [警告] config.local.json 读取失败，已忽略：%s" % _e)


def cfg(key, env_name, default=""):
    v = LOCAL_CFG.get(key)
    if v is None or (isinstance(v, str) and not v.strip()):
        v = os.environ.get(env_name) or default
    return str(v or "").strip()


FEISHU_WEBHOOK = cfg("feishu_webhook", "SHZCGS_FEISHU_WEBHOOK")
FEISHU_KEYWORD = cfg("feishu_keyword", "SHZCGS_FEISHU_KEYWORD", "咨询") or "咨询"
SITE_NAME = "上海注册公司.com"

# ---------------------------------------------------------------
# 站点地图：路径 → (导航标题, 页面标题, meta description, 页面 h1, 副标题)
# ---------------------------------------------------------------
PAGES = {
    "": ("首页", "上海注册公司｜营业执照代办｜园区地址挂靠",
         "上海注册公司怎么办？费用、流程、材料、地址挂靠一次说清。宝山实体办公，电话17652523536，先免费帮你判断该注册个体户还是有限公司，再谈办不办。",
         None, None),
    "feiyong/": ("费用", "上海注册公司费用明细｜钱花在哪几块",
                 "上海注册公司费用由哪些部分构成？政府规费、注册地址费、代办服务费、后续记账费逐项拆开讲，教你看懂报价单、避开「低价引流再补收」的套路。",
                 "上海注册公司费用，到底花在哪", "市场上报价差很多，先看懂钱花在哪，才不会被绕"),
    "liucheng/": ("流程", "上海注册公司全流程｜7步办理指引",
                 "上海注册公司全流程7步详解：核名、经营范围、注册地址、提交材料、领取执照、税务开户、做账报税，每一步要做什么、容易卡在哪，一次说清。",
                 "上海注册公司全流程", "现在基本可以全程网上办理，走「一网通办」"),
    "cailiao/": ("材料", "上海注册公司需要什么材料｜清单明细",
                 "上海注册公司需要准备哪些材料？名称、经营范围、地址证明、股东身份材料、公司章程逐项列清，并说明哪些材料最容易因为小细节被退回。",
                 "上海注册公司需要准备什么材料", "提前备齐，能少跑好几趟"),
    "dizhi-guakao/": ("地址挂靠", "上海园区地址挂靠｜靠不靠谱怎么判断",
                 "上海注册公司没有地址怎么办？园区地址挂靠是什么、怎么判断靠不靠谱、哪几类行业不能用挂靠地址，一次说清判断方法，避免踩到不合规的地址。",
                 "没有注册地址怎么办：园区挂靠", "这是大多数初创公司的实际选择"),
    "shijian/": ("办理时间", "上海注册公司要多久｜各环节耗时明细",
                 "上海注册公司要多久？核名、材料审核、领取执照、银行开户各环节分别耗时多久，哪些环节最容易拖慢整体进度，以及怎么合理安排时间预期。",
                 "上海注册公司要多久", "各环节分别要等多久，心里先有个数"),
    "gezhong/": ("个体户/公司", "上海个体户和有限公司怎么选｜区别对比",
                 "上海注册个体户还是有限公司？从责任承担、税负高低、能否开票、融资难度、经营规模五个维度做对比，帮你按自己的实际业务情况做判断。",
                 "个体户还是有限公司，怎么选", "选错了改起来很麻烦，先想清楚再动手"),
    "yinhang/": ("银行开户", "上海公司银行开户流程｜为什么难办",
                 "上海公司银行开户怎么办理？为什么现在开户比以前难、各家银行要求差异有多大、法人是否必须到场、需要带哪些材料，一次讲清避免白跑。",
                 "公司银行开户怎么办", "这一步现在比注册本身还容易卡住"),
    "dailijizhang/": ("代理记账", "上海代理记账多少钱｜怎么选服务",
                 "上海公司代理记账多少钱？费用受哪些因素影响、小规模和一般纳税人有何区别、怎么判断一家代账机构靠不靠谱，附上挑选服务时的几个要点。",
                 "代理记账多少钱，怎么选", "公司成立后的固定支出，办之前先算清楚"),
    "wangshang/": ("网上办理", "上海一网通办注册公司怎么操作｜步骤教程",
                 "上海一网通办怎么注册公司？从平台入口、实名认证、电子签名到材料上传的完整操作思路，以及最常见的几种提交失败原因和对应处理办法。",
                 "上海一网通办怎么操作", "自己办的完整思路，不找人也能走通"),
    "faq/": ("常见问题", "上海注册公司常见问题30问｜答疑汇总",
             "上海注册公司常见问题汇总：法人是否必须到场、住宅能不能注册、注册资本写多少合适、每年要固定花哪些钱、代办和自己办的区别，逐条作答。",
             "常见问题解答", "办之前最容易困惑的问题都在这里"),
    "articles/": ("注册公司攻略", "上海注册公司办理攻略｜实务长文合集",
                  "上海注册公司办理攻略合集：费用构成、办理流程、材料清单、地址挂靠、行业资质、形态对比、注册后事务，按主题分组，每篇讲清一个具体问题。",
                  "上海注册公司办理攻略", "按主题分组，每篇只讲清一个具体问题"),
    "women/": ("关于我们", "关于我们｜上海注册公司.com",
               "上海注册公司.com 由上海宝山本地团队运营，专注公司注册咨询与园区资源对接，地址：上海市宝山区萧云路501号，电话17652523536，欢迎来电咨询。",
               "关于我们", "先帮你把情况理清楚，再谈办不办"),
}

DISC_HTML = """    <div class="disc">
      本站内容为一般性信息整理，仅供决策参考，不构成法律、财税或投资建议。公司注册的具体要求、费用与政策，以市场监督管理部门、税务机关及所在园区的最新规定为准。我们不承诺任何办理结果，请根据自身情况独立判断。
    </div>"""

# build_faq_block() 每次调用会把该页 FAQ 登记在这里；compose() 读取生成 JSON-LD
_FAQ_REGISTRY = {}


def rel(path_from, target):
    """计算从 path_from 页面到 target 的相对链接

    按目录深度算，不能写死一个 "../"：
      ""                    → 0 层
      "feiyong/"            → 1 层
      "articles/<slug>/"    → 2 层  ← 文章页在这里
    """
    if path_from == "":
        return target
    # 目录层数 = 去掉尾部斜杠后，路径里的 / 个数
    depth = path_from.rstrip("/").count("/") + 1
    return "../" * depth + target


def build_head(page_path, title, desc, extra_jsonld=""):
    canonical = SITE_URL + "/" + page_path
    # 全站统一的组织信息结构化数据（本地商家，匹配宝山实体地址）
    org_jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": "上海注册公司.com",
        "url": SITE_URL + "/",
        "telephone": PHONE,
        "description": "上海公司注册咨询与园区资源对接，提供营业执照办理、地址挂靠、代理记账等服务的规则解读。",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "萧云路501号",
            "addressLocality": "上海市",
            "addressRegion": "宝山区",
            "addressCountry": "CN",
        },
        "areaServed": {"@type": "City", "name": "上海市"},
        "priceRange": "咨询免费",
    }, ensure_ascii=False, separators=(",", ":"))
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - 上海注册公司.com</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="上海注册公司,上海公司注册,上海注册公司流程,上海注册公司费用,园区地址挂靠,代理记账">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="{asset_url(page_path, 'css/style.css')}">
<script type="application/ld+json">{org_jsonld}</script>
{extra_jsonld}</head>
<body>
"""


def build_header(page_path):
    home = rel(page_path, "./") if page_path else "./"
    p = lambda s: rel(page_path, s)
    return f"""
<header>
  <div class="wrap nav">
    <a class="logo" href="{home}">上海注册公司<small>营业执照 · 地址挂靠 · 财税一站式</small></a>
    <nav class="navlinks">
      <a href="{p('articles/')}">攻略</a>
      <a href="{p('feiyong/')}">费用</a>
      <a href="{p('liucheng/')}">流程</a>
      <a href="{p('cailiao/')}">材料</a>
      <a href="{p('dizhi-guakao/')}">地址挂靠</a>
      <a href="{p('faq/')}">常见问题</a>
      <a href="{p('women/')}">关于我们</a>
    </nav>
    <a class="navtel" href="tel:{PHONE_TEL}">📞 {PHONE}</a>
  </div>
</header>

<div class="callbar"><a href="tel:{PHONE_TEL}">📞 点击拨打 {PHONE} 免费咨询</a></div>
"""


def build_faq_jsonld(faqs):
    """把 FAQ 列表转成 FAQPage 结构化数据（拿富摘要展示位）
    faqs = [(问题, 答案HTML), ...]；答案里的标签会被剥掉只留纯文本"""
    if not faqs:
        return ""
    import re as _re
    items = []
    for q, a in faqs:
        plain = _re.sub(r"<[^>]+>", "", a)
        plain = _re.sub(r"\s+", " ", plain).strip()
        if not q or not plain:
            continue
        items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": plain},
        })
    if not items:
        return ""
    data = json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": items}, ensure_ascii=False, separators=(",", ":"))
    return ('<script type="application/ld+json">' + data + "</script>\n")


def build_breadcrumb_jsonld(page_path, page_name):
    """面包屑结构化数据：首页 > 当前页"""
    if page_path == "":
        return ""
    data = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": page_name,
             "item": SITE_URL + "/" + page_path},
        ],
    }, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">' + data + "</script>\n"


def build_footer(page_path):
    p = lambda s: rel(page_path, s)
    return f"""
<footer>
  <div>上海注册公司.com · 上海注册公司.cn · 上海注册公司.中国</div>
  <div class="nav-f">
    <a href="{p('articles/')}">办理攻略</a>
    <a href="{p('feiyong/')}">费用明细</a>
    <a href="{p('liucheng/')}">办理流程</a>
    <a href="{p('cailiao/')}">材料清单</a>
    <a href="{p('dizhi-guakao/')}">地址挂靠</a>
    <a href="{p('yinhang/')}">银行开户</a>
    <a href="{p('dailijizhang/')}">代理记账</a>
    <a href="{p('faq/')}">常见问题</a>
    <a href="{p('women/')}">关于我们</a>
  </div>
  <div style="margin-top:6px">上海市宝山区萧云路501号 · {PHONE}　|　更新日期 {BUILD_DATE}</div>
{DISC_HTML}
</footer>

<script src="{asset_url(page_path, 'js/main.js')}"></script>
</body>
</html>
"""


def build_pagehead(page_path, h1, sub, title_for_crumb):
    p = lambda s: rel(page_path, s)
    return f"""
<div class="pagehead">
  <div class="wrap">
    <div class="breadcrumb"><a href="{p('./')}">首页</a> › {title_for_crumb}</div>
    <h1>{h1}</h1>
    <p>{sub}</p>
  </div>
</div>
"""


def build_cta(text, btn_text="📞 电话咨询 " + PHONE):
    return f"""
<div class="wrap"><div class="cta-band">
  <div><h3>{text}</h3><p>不推销，先帮你把情况理清楚再谈办不办</p></div>
  <a class="btn" href="tel:{PHONE_TEL}">{btn_text}</a>
</div></div>
"""


def build_linklist(page_path, exclude=None, title="相关内容", sub="按你关心的问题挑着看"):
    """生成内链区块，自动排除当前页"""
    items = []
    for path, meta in PAGES.items():
        if path == "" or path == exclude:
            continue
        items.append((path, meta[0]))
    links = "\n".join(
        f'      <a href="{rel(page_path, path)}">{name} <span>→</span></a>'
        for path, name in items
    )
    return f"""
<section>
  <div class="wrap">
    <h2 class="sec-title">{title}</h2>
    <p class="sec-sub">{sub}</p>
    <div class="linklist">
{links}
    </div>
  </div>
</section>
"""


def build_faq_block(page_path, faqs, heading="常见问题", sub="点开看答案"):
    """faqs = [(问题, 答案), ...]"""
    if not faqs:
        return ""
    # 登记到收集器：compose() 会用同一份数据生成 FAQPage 结构化数据，
    # 保证「页面可见问答」和「结构化数据」永远一致（不会一个改了另一个忘改）
    _FAQ_REGISTRY[page_path] = faqs
    items = "\n".join(
        f'    <div class="faq-item"><div class="faq-q">{html_mod.escape(q)}</div>'
        f'<div class="faq-a">{a}</div></div>'
        for q, a in faqs
    )
    return f"""
<section style="background:#fff">
  <div class="wrap-narrow">
    <h2 class="sec-title">{heading}</h2>
    <p class="sec-sub">{sub}</p>
{items}
  </div>
</section>
"""


def build_form():
    return f"""
<section>
  <div class="wrap" style="max-width:560px">
    <div class="formbox">
      <h3>留个联系方式，我们回电</h3>
      <p class="tip">只填手机号就行，不推销，先帮你把情况理清楚</p>
      <form id="leadForm" onsubmit="return submitLead(event)">
        <label for="f-name">怎么称呼你</label>
        <input type="text" id="f-name" name="name" placeholder="例如：王先生" autocomplete="name" required>
        <label for="f-phone">手机号码</label>
        <input type="tel" id="f-phone" name="phone" placeholder="11 位手机号" pattern="1[3-9]\\d{{9}}" autocomplete="tel" required>
        <label for="f-note">想咨询什么（选填）</label>
        <textarea id="f-note" name="note" rows="3" placeholder="例如：想注册一个贸易公司，没有地址"></textarea>
        <!-- 蜜罐字段：正常用户看不见、不会填；被脚本自动填充即判定为垃圾 -->
        <input id="c9" name="company_url" tabindex="-1" autocomplete="off"
               style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0" aria-hidden="true">
        <button type="submit" id="f-submit">让顾问联系我</button>
      </form>
      <p id="formmsg" role="status" aria-live="polite" style="text-align:center;margin-top:14px;font-size:14px;color:var(--brand);display:none"></p>
    </div>
  </div>
</section>
"""


def build_contact_band():
    return f"""
<div class="contact">
  <h2>拿不准的事，直接问更快</h2>
  <p>做不做、怎么做、花多少，先说清楚再谈办理</p>
  <div class="big">{PHONE}</div>
  <p>微信同号 · 上海宝山 · 萧云路501号</p>
</div>
"""


JS_MAIN_TMPL = """/* 上海注册公司.com 全站脚本 */
(function () {
  'use strict';

  /* FAQ 折叠 */
  document.querySelectorAll('.faq-q').forEach(function (q) {
    q.addEventListener('click', function () {
      var item = q.parentElement;
      if (item) item.classList.toggle('open');
    });
  });

  /* 表格横向滚动包装（窄屏可读性） */
  document.querySelectorAll('.article table').forEach(function (t) {
    if (t.parentElement && t.parentElement.classList.contains('table-wrap')) return;
    var w = document.createElement('div');
    w.className = 'table-wrap';
    w.style.overflowX = 'auto';
    t.parentNode.insertBefore(w, t);
  });
})();

/* ============================================================
   线索表单：提交到飞书群机器人（自定义机器人 Webhook）
   接收端地址由构建时注入；未配置则进入演示模式（不发送任何数据）
   ============================================================ */
var SHZCGS_CFG = {
  webhook: "__FEISHU_WEBHOOK__",
  keyword: "__FEISHU_KEYWORD__",
  site: "__SITE_NAME__",
  phone: "__PHONE__"
};

var LEAD_FIELDS = [
  ["称呼", "name"],
  ["手机号", "phone"],
  ["咨询内容", "note"]
];

function leadEsc(s) {
  return String(s || "").replace(/[&<>]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c];
  });
}

function leadNow() {
  var d = new Date();
  function p(n) { return (n < 10 ? "0" : "") + n; }
  return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate())
       + " " + p(d.getHours()) + ":" + p(d.getMinutes());
}

function leadCard(d) {
  var lines = LEAD_FIELDS.filter(function (f) { return d[f[1]]; })
    .map(function (f) { return "**" + f[0] + "**：" + leadEsc(d[f[1]]); });
  return {
    msg_type: "interactive",
    card: {
      config: { wide_screen_mode: true },
      header: {
        template: "blue",
        title: { tag: "plain_text", content: "🔔 新" + SHZCGS_CFG.keyword + " · " + SHZCGS_CFG.site }
      },
      elements: [
        { tag: "div", text: { tag: "lark_md", content: lines.join("\\n") || "（未填写）" } },
        { tag: "hr" },
        { tag: "note", elements: [{ tag: "plain_text",
            content: "来源：表单页 · " + leadNow() + " · 类型：" + SHZCGS_CFG.keyword }] }
      ]
    }
  };
}

function leadShow(text, ok) {
  var msg = document.getElementById("formmsg");
  if (!msg) return;
  msg.textContent = text;
  msg.style.color = ok === false ? "#c0392b" : "var(--brand)";
  msg.style.display = "block";
  msg.scrollIntoView({ block: "center", behavior: "smooth" });
}

function leadBtnLock(lock, text) {
  var b = document.getElementById("f-submit");
  if (!b) return;
  if (lock) {
    b.dataset.old = b.textContent;
    b.textContent = text || "提交中…";
    b.disabled = true;
  } else {
    b.textContent = b.dataset.old || "让顾问联系我";
    b.disabled = false;
  }
}

function submitLead(e) {
  if (e && e.preventDefault) e.preventDefault();

  var el = function (id) { var n = document.getElementById(id); return n ? n.value : ""; };
  var name = el("f-name").trim();
  var phone = el("f-phone").trim();
  var note = el("f-note").trim();

  /* 蜜罐：命中即假成功，不发送（避免被脚本探测出拦截规则） */
  if (el("c9")) {
    leadShow("收到，" + (name || "你") + "。我们会尽快联系你，急的话直接打 " + SHZCGS_CFG.phone, true);
    var f0 = document.getElementById("leadForm");
    if (f0) f0.reset();
    return false;
  }

  if (!/^1[3-9]\\d{9}$/.test(phone)) {
    leadShow("手机号好像不对，请检查一下（11 位，1 开头）", false);
    return false;
  }

  /* 降级：未配置接收端 → 演示模式，不把数据发给任何第三方 */
  if (!SHZCGS_CFG.webhook) {
    leadShow("收到，" + (name || "你") + "。我们会尽快联系你，急的话直接打 " + SHZCGS_CFG.phone, true);
    var f1 = document.getElementById("leadForm");
    if (f1) f1.reset();
    return false;
  }

  leadBtnLock(true);

  fetch(SHZCGS_CFG.webhook, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(leadCard({ name: name, phone: phone, note: note }))
  })
    .then(function (r) { return r.json(); })
    .then(function (j) {
      leadBtnLock(false);
      if (j && (j.code === 0 || j.StatusCode === 0)) {
        leadShow("收到，" + (name || "你") + "。我们会尽快联系你，急的话直接打 " + SHZCGS_CFG.phone, true);
        var f2 = document.getElementById("leadForm");
        if (f2) f2.reset();
      } else {
        var m = (j && (j.msg || j.StatusMessage)) || "未知错误";
        leadShow("提交没成功（" + m + "）。可以直接打电话 " + SHZCGS_CFG.phone + "，更快。", false);
      }
    })
    .catch(function () {
      leadBtnLock(false);
      leadShow("网络好像不太顺，提交没发出去。可以直接打电话 " + SHZCGS_CFG.phone + "，更快。", false);
    });

  return false;
}
"""

JS_MAIN = (JS_MAIN_TMPL
           .replace("__FEISHU_WEBHOOK__", FEISHU_WEBHOOK)
           .replace("__FEISHU_KEYWORD__", FEISHU_KEYWORD)
           .replace("__SITE_NAME__", SITE_NAME)
           .replace("__PHONE__", PHONE))


def write_file(rel_path, content):
    full = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return len(content)


def build_all():
    written = []
    # 静态资源（BASE_DIR 即 site/ 目录，无需再加 site 前缀）
    written.append(("js/main.js", write_file("js/main.js", JS_MAIN)))
    css_path = os.path.join(BASE_DIR, "css", "style.css")
    if os.path.exists(css_path):
        written.append(("css/style.css", os.path.getsize(css_path)))

    # 构建时明确打印接收端，避免「配了没生效」还查半天
    if FEISHU_WEBHOOK:
        masked = FEISHU_WEBHOOK[-8:] if len(FEISHU_WEBHOOK) > 8 else "***"
        print("询单接收端：已启用（飞书 webhook ...%s，关键词「%s」）" % (masked, FEISHU_KEYWORD))
    else:
        print("询单接收端：未配置 → 演示模式（前端校验照跑，不发送任何数据）")
        print("           配置方式：python setup_form.py  或  设 SHZCGS_FEISHU_WEBHOOK 环境变量")

    print("静态资源已就绪，页面由 gen_pages.py 生成。")
    return written


if __name__ == "__main__":
    build_all()
