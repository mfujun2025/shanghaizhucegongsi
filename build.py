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
import html as html_mod
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://xn--5nqv0mk2lgd.com"
PHONE = "17652523536"
PHONE_TEL = "17652523536"
BUILD_DATE = date.today().isoformat()

# ---------------------------------------------------------------
# 站点地图：路径 → (导航标题, 页面标题, meta description, 页面 h1, 副标题)
# ---------------------------------------------------------------
PAGES = {
    "": ("首页", "上海注册公司_营业执照代办_园区地址挂靠",
         "上海注册公司怎么办？费用、流程、材料、地址挂靠一次说清。宝山实体办公，电话17652523536，免费帮你判断该注册个体户还是有限公司。",
         None, None),
    "feiyong/": ("费用", "上海注册公司费用明细_钱花在哪几块",
                 "上海注册公司费用由哪些部分构成？政府规费、注册地址费、代办服务费、后续记账费逐项拆解，教你看懂报价、避免隐藏收费。",
                 "上海注册公司费用，到底花在哪", "市场上报价差很多，先看懂钱花在哪，才不会被绕"),
    "liucheng/": ("流程", "上海注册公司全流程_7步办理指引",
                 "上海注册公司全流程7步详解：核名、经营范围、注册地址、提交材料、领取执照、税务开户、做账报税，每步注意事项一次说清。",
                 "上海注册公司全流程", "现在基本可以全程网上办理，走「一网通办」"),
    "cailiao/": ("材料", "上海注册公司需要什么材料_清单明细",
                 "上海注册公司需要准备哪些材料？名称、经营范围、地址证明、股东身份材料、章程等逐项列清，附常见被退回的原因。",
                 "上海注册公司需要准备什么材料", "提前备齐，能少跑好几趟"),
    "dizhi-guakao/": ("地址挂靠", "上海园区地址挂靠_靠不靠谱怎么判断",
                 "上海注册公司没有地址怎么办？园区地址挂靠是什么、怎么判断靠不靠谱、哪些行业不能挂靠，一次说清判断方法。",
                 "没有注册地址怎么办：园区挂靠", "这是大多数初创公司的实际选择"),
    "shijian/": ("办理时间", "上海注册公司要多久_各环节耗时明细",
                 "上海注册公司要多久？核名、审核、领照、开户各环节分别耗时多久，哪些环节容易拖慢进度，以及怎么合理预期。",
                 "上海注册公司要多久", "各环节分别要等多久，心里先有个数"),
    "gezhong/": ("个体户/公司", "上海个体户和有限公司怎么选_区别对比",
                 "上海注册个体户还是有限公司？责任承担、税负、开票、融资、经营规模五个维度对比，帮你按自己的业务情况做判断。",
                 "个体户还是有限公司，怎么选", "选错了改起来很麻烦，先想清楚再动手"),
    "yinhang/": ("银行开户", "上海公司银行开户流程_为什么难办",
                 "上海公司银行开户怎么办理？为什么现在开户变难了、各家银行要求差异、法人是否要到场、需要哪些材料，一次讲清。",
                 "公司银行开户怎么办", "这一步现在比注册本身还容易卡住"),
    "dailijizhang/": ("代理记账", "上海代理记账多少钱_怎么选服务",
                 "上海公司代理记账多少钱？费用受什么影响、小规模和一般纳税人有何区别、怎么判断代账机构是否靠谱，附选择要点。",
                 "代理记账多少钱，怎么选", "公司成立后的固定支出，办之前先算清楚"),
    "wangshang/": ("网上办理", "上海一网通办注册公司怎么操作_步骤教程",
                 "上海一网通办怎么注册公司？平台入口、实名认证、电子签名、材料上传的完整操作思路，以及常见提交失败原因。",
                 "上海一网通办怎么操作", "自己办的完整思路，不找人也能走通"),
    "faq/": ("常见问题", "上海注册公司常见问题30问_答疑汇总",
             "上海注册公司常见问题汇总：法人是否到场、住宅能否注册、注册资本写多少、每年要花什么钱、代办和自己办的区别等。",
             "常见问题解答", "办之前最容易困惑的问题都在这里"),
    "women/": ("关于我们", "关于我们_上海注册公司.com",
               "上海注册公司.com 由上海宝山本地团队运营，专注公司注册咨询与园区资源对接，地址：上海市宝山区萧云路501号，电话17652523536。",
               "关于我们", "先帮你把情况理清楚，再谈办不办"),
}

DISC_HTML = """    <div class="disc">
      本站内容为一般性信息整理，仅供决策参考，不构成法律、财税或投资建议。公司注册的具体要求、费用与政策，以市场监督管理部门、税务机关及所在园区的最新规定为准。我们不承诺任何办理结果，请根据自身情况独立判断。
    </div>"""


def rel(path_from, target):
    """计算从 path_from 页面到 target 的相对链接（用于子目录页面）"""
    if path_from == "":
        return target
    return "../" + target


def build_head(page_path, title, desc):
    canonical = SITE_URL + "/" + page_path
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
<link rel="stylesheet" href="{rel(page_path, 'css/style.css')}">
</head>
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


def build_footer(page_path):
    p = lambda s: rel(page_path, s)
    return f"""
<footer>
  <div>上海注册公司.com · 上海注册公司.cn · 上海注册公司.中国</div>
  <div class="nav-f">
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

<script src="{p('js/main.js')}"></script>
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
        <button type="submit">让顾问联系我</button>
      </form>
      <p id="formmsg" style="text-align:center;margin-top:14px;font-size:14px;color:var(--brand);display:none"></p>
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


JS_MAIN = """/* 上海注册公司.com 全站脚本 */
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
    w.appendChild(t);
  });
})();

/* 线索表单提交（前端占位，后续可接飞书 Webhook） */
function submitLead(e) {
  e.preventDefault();
  var name = (document.getElementById('f-name') || {}).value || '';
  var phone = (document.getElementById('f-phone') || {}).value || '';
  var note = (document.getElementById('f-note') || {}).value || '';
  name = name.trim();
  phone = phone.trim();

  if (!/^1[3-9]\\d{9}$/.test(phone)) {
    alert('请填写正确的 11 位手机号');
    return false;
  }

  var msg = document.getElementById('formmsg');
  if (msg) {
    msg.textContent = '收到，' + (name || '你') + '。我们会尽快联系你，急的话直接打 17652523536';
    msg.style.display = 'block';
    msg.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }
  document.getElementById('leadForm').reset();
  return false;
}
"""


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

    print("静态资源已就绪，页面由 gen_pages.py 生成。")
    return written


if __name__ == "__main__":
    build_all()
