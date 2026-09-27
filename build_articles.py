#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海注册公司.com 文章构建器（日更管线核心）
==========================================
用法：
  python build_articles.py              # 构建 _content/ 下全部文章
  python build_articles.py --check      # 只校验不写文件

输入： _content/<slug>.md   （frontmatter + markdown 正文，格式见 README）
输出：
  articles/<slug>/index.html   每篇文章页（含 Article/Breadcrumb/FAQ JSON-LD）
  articles/index.html          文章总目录（按簇分组）
  sitemap.xml                  重建（含全部文章）
  index.html 的文章区块         自动注入 <!-- ARTICLES:AUTO --> 处
  _topics/topics.json          同步 slug → 文章路径映射

设计原则：
  · 复用 build.py 的 head/header/footer/form/contact 组件，样式与主站完全一致
  · 只支持一种 markdown 子集（下表），解析器简单可控、不会出意外
  · 构建幂等：反复跑结果一致
"""
import os
import re
import json
import glob
import sys
import html as _html

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = HERE                                   # site/
CONTENT = os.path.join(HERE, "_content")
TOPICS_FILE = os.path.join(HERE, "_topics", "topics.json")

sys.path.insert(0, BASE)
from build import (BASE_DIR, build_head, build_header, build_footer,
                   build_pagehead, build_cta, build_contact_band, build_form,
                   build_linklist, build_faq_jsonld, build_breadcrumb_jsonld,
                   PHONE, PHONE_TEL, SITE_URL, BUILD_DATE, rel)

ARTICLES_DIR = os.path.join(BASE, "articles")

# ---- 簇定义：键 → (显示名, 一句话说明) ----
CLUSTERS = {
    "fee":      ("费用与成本", "钱花在哪、怎么算、怎么不被绕"),
    "process":  ("流程与办理", "每一步做什么、容易卡在哪"),
    "material": ("材料与条件", "要准备什么、什么情况下办不了"),
    "address":  ("地址与园区", "没地址怎么办、挂靠靠不靠谱"),
    "industry": ("行业资质", "不同行业办公司要多注意什么"),
    "compare":  ("形态对比", "个体户还是公司、怎么选不后悔"),
    "maintain": ("注册后事务", "报税、年报、变更、注销"),
}
CLUSTER_ORDER = ["fee", "process", "material", "address",
                 "industry", "compare", "maintain"]

ARTICLES_HUB = "articles/"


# ======================================================= 工具
def esc(s):
    return _html.escape(s, quote=False)


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def text_len(s):
    return len(re.sub(r"[\s]", "", re.sub(r"<[^>]+>", "", s)))


def slugify_anchor(t):
    """h2 文本 → 锚点 id"""
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", t).strip("-")
    return s[:60] or "sec"


# ======================================================= frontmatter
REQUIRED = ["title", "seo_title", "slug", "cluster", "core", "desc", "brief", "date"]


def parse_front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        raise ValueError("缺少 frontmatter（文件必须以 --- 开头）")
    meta = {}
    for ln in m.group(1).split("\n"):
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2)


# ======================================================= markdown
def render_table(rows):
    head = [c.strip() for c in rows[0].strip("|").split("|")]
    body = rows[2:]
    h = ('<div class="table-scroll"><table class="info-table"><thead><tr>'
         + "".join("<th>%s</th>" % inline(c) for c in head)
         + "</tr></thead><tbody>")
    for r in body:
        cells = [c.strip() for c in r.strip("|").split("|")]
        h += "<tr>" + "".join("<td>%s</td>" % inline(c) for c in cells) + "</tr>"
    return h + "</tbody></table></div>"


def render_faq(lines):
    """::faq 块 → (html, [(q, a), ...])"""
    qa, cur = [], None
    for ln in lines:
        s = ln.strip()
        if s.startswith("Q|"):
            if cur:
                qa.append(cur)
            cur = [s[2:].strip(), ""]
        elif s.startswith("A|") and cur:
            cur[1] = (cur[1] + " " + s[2:].strip()).strip()
    if cur:
        qa.append(cur)

    out = []
    for q, a in qa:
        out.append('<details class="faq-item"><summary class="faq-q">%s</summary>'
                   '<div class="faq-a">%s</div></details>' % (esc(q), inline(a)))
    return "\n".join(out), qa


def render_markdown(md):
    """返回 (html, faqs, toc)"""
    lines = md.split("\n")
    out, faqs, toc = [], [], []
    i = 0
    h2_id = 0

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        # ::faq 块
        if s == "::faq":
            block = []
            i += 1
            while i < len(lines) and lines[i].strip() != "::":
                block.append(lines[i])
                i += 1
            html_faq, qa = render_faq(block)
            out.append('<div class="article-faq">%s</div>' % html_faq)
            faqs.extend(qa)
            i += 1
            continue

        # 表格
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            out.append(render_table(rows))
            continue

        # 标题
        m = re.match(r"^(#{2,4})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1))
            txt = m.group(2).strip()
            if lvl == 2:
                h2_id += 1
                aid = slugify_anchor(txt) or ("sec%d" % h2_id)
                toc.append((aid, txt))
                out.append('<h2 id="%s">%s</h2>' % (aid, inline(txt)))
            else:
                out.append("<h%d>%s</h%d>" % (lvl, inline(txt), lvl))
            i += 1
            continue

        # 引用块
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(buf)))
            continue

        # 列表
        if re.match(r"^[-*]\s+", s) or re.match(r"^\d+\.\s+", s):
            ordered = bool(re.match(r"^\d+\.\s+", s))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                t = lines[i].strip()
                mm = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", t)
                if not mm:
                    break
                items.append("<li>%s</li>" % inline(mm.group(1)))
                i += 1
            out.append("<%s>%s</%s>" % (tag, "".join(items), tag))
            continue

        # 空行
        if not s:
            i += 1
            continue

        # 段落
        out.append("<p>%s</p>" % inline(s))
        i += 1

    return "\n".join(out), faqs, toc


# ======================================================= 页面组装
def build_toc(toc):
    if len(toc) < 4:
        return ""
    items = "".join('<a href="#%s">%s</a>' % (a, esc(t)) for a, t in toc)
    return ('<nav class="toc"><div class="toc-title">本文目录</div>'
            '<div class="toc-list">%s</div></nav>' % items)


def build_article_page(meta, body_html, faqs, toc_html):
    page_path = "articles/%s/" % meta["slug"]
    title = meta["seo_title"]
    desc = meta["desc"]

    jsonld = (build_faq_jsonld(faqs)
              + build_breadcrumb_jsonld(page_path, meta["title"])
              + build_article_jsonld(meta))

    head = build_head(page_path, title, desc, extra_jsonld=jsonld)

    crumb = '<div class="breadcrumb"><a href="../../">首页</a> › ' \
            '<a href="../">%s</a> › %s</div>' % ("注册公司攻略", esc(meta["core"]))
    pagehead = f"""
<div class="pagehead">
  <div class="wrap">
    {crumb}
    <h1>{esc(meta['title'])}</h1>
    <p>{esc(meta['brief'])}</p>
  </div>
</div>
"""
    article = f"""
<div class="wrap">
  <div class="article">
    <div class="article-meta">更新日期 {esc(meta['date'])}　|　核心词：{esc(meta['core'])}</div>
    {toc_html}
    {body_html}
  </div>
</div>
"""

    parts = [
        head,
        build_header(page_path),
        pagehead,
        article,
        build_cta("还有拿不准的？直接打电话问更快"),
        build_form(),
        build_contact_band(),
        build_related(page_path, meta),
        build_footer(page_path),
    ]
    return "".join(parts)


def build_article_jsonld(meta):
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": meta["title"],
        "description": meta["desc"],
        "datePublished": meta["date"],
        "dateModified": meta["date"],
        "author": {"@type": "Organization", "name": "上海注册公司.com"},
        "publisher": {"@type": "Organization", "name": "上海注册公司.com"},
        "mainEntityOfPage": SITE_URL + "/articles/%s/" % meta["slug"],
        "about": meta["core"],
        "keywords": ",".join([k for k in [meta.get("core", "")] + meta.get("longtail", "").split("|") if k]),
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            + "</script>\n")


def build_related(page_path, meta):
    """同簇相关文章（构目录时才知道有哪些，此处用占位符，二次替换）"""
    return "<!-- RELATED:%s -->" % meta["cluster"]


# ======================================================= 目录页
def build_hub(all_meta):
    page_path = ARTICLES_HUB
    title = "上海注册公司办理攻略｜70篇实务问答"
    desc = ("上海注册公司办理攻略合集：费用构成、办理流程、材料清单、地址挂靠、行业资质、"
            "形态对比、注册后事务，按主题分组，每篇讲清一个具体问题。")

    groups = []
    for ck in CLUSTER_ORDER:
        items = [m for m in all_meta if m["cluster"] == ck]
        if not items:
            continue
        cname, cdesc = CLUSTERS[ck]
        cards = "".join(
            '<a class="art-card" href="%s/"><div class="art-t">%s</div>'
            '<div class="art-b">%s</div></a>' % (m["slug"], esc(m["title"]), esc(m["brief"]))
            for m in items
        )
        groups.append(
            '<section class="art-group"><h2 class="sec-title">%s</h2>'
            '<p class="sec-sub">%s</p><div class="art-grid">%s</div></section>'
            % (esc(cname), esc(cdesc), cards)
        )

    body = f"""
<div class="pagehead">
  <div class="wrap">
    <div class="breadcrumb"><a href="../">首页</a> › 注册公司攻略</div>
    <h1>上海注册公司办理攻略</h1>
    <p>按主题分组，每篇只讲清一个具体问题</p>
  </div>
</div>
<div class="wrap art-hub">
{''.join(groups)}
</div>
"""
    jsonld = build_breadcrumb_jsonld(page_path, "注册公司攻略")
    parts = [
        build_head(page_path, title, desc, extra_jsonld=jsonld),
        build_header(page_path),
        body,
        build_cta("攻略看完了还是不确定自己该怎么做？"),
        build_form(),
        build_contact_band(),
        build_footer(page_path),
    ]
    return "".join(parts)


# ======================================================= 主流程
def load_all():
    files = sorted(glob.glob(os.path.join(CONTENT, "*.md")))
    out = []
    errs = []
    for f in files:
        try:
            raw = open(f, encoding="utf-8").read()
            meta, md = parse_front_matter(raw)
        except Exception as e:
            errs.append("%s：%s" % (os.path.basename(f), e))
            continue
        miss = [k for k in REQUIRED if not meta.get(k)]
        if miss:
            errs.append("%s：缺少字段 %s" % (os.path.basename(f), ",".join(miss)))
            continue
        if meta["cluster"] not in CLUSTERS:
            errs.append("%s：cluster「%s」不在定义中（可选：%s）"
                        % (os.path.basename(f), meta["cluster"], "/".join(CLUSTERS)))
            continue
        body_html, faqs, toc = render_markdown(md)
        meta["_body"] = body_html
        meta["_faqs"] = faqs
        meta["_toc"] = build_toc(toc)
        meta["_len"] = text_len(body_html)
        meta["_file"] = os.path.basename(f)
        out.append(meta)
    return out, errs


def check(arts):
    """返回 (错误, 警告)"""
    errors, warns = [], []
    seen_slug, seen_core = {}, {}

    for m in arts:
        name = m["_file"]
        if m["slug"] in seen_slug:
            errors.append("[slug重复] %s 与 %s" % (name, seen_slug[m["slug"]]))
        seen_slug[m["slug"]] = name
        if m["core"] in seen_core:
            errors.append("[核心词重复] %s 与 %s（都是「%s」）"
                          % (name, seen_core[m["core"]], m["core"]))
        seen_core[m["core"]] = name

        if not re.match(r"^[a-z0-9-]+$", m["slug"]):
            errors.append("[slug非ASCII] %s → %s" % (name, m["slug"]))

        st = len(m["seo_title"])
        if st > 30:
            warns.append("[seo_title偏长] %s = %d 字" % (name, st))
        dl = len(m["desc"])
        if not (50 <= dl <= 80):
            warns.append("[desc长度] %s = %d 字（建议 60-78）" % (name, dl))
        if m["_len"] < 1500:
            errors.append("[正文过短] %s = %d 字（下限 1500）" % (name, m["_len"]))
        if m["_len"] < 1800:
            warns.append("[正文偏薄] %s = %d 字（目标 1800-2500）" % (name, m["_len"]))
        if not m["_faqs"]:
            warns.append("[缺FAQ] %s" % name)
        if len(m["_faqs"]) < 4:
            warns.append("[FAQ偏少] %s = %d 条（建议 4-8）" % (name, len(m["_faqs"])))
        # 主词密度（只看正文，不含 header/footer/表单等全站组件）
        kw = "上海注册公司"
        cnt = m["_body"].count(kw)
        dens = cnt * len(kw) / max(m["_len"], 1) * 100
        if dens < 0.3:
            warns.append("[主词密度偏低] %s = %.2f%%（目标 0.3-0.6%%）" % (name, dens))
        elif dens > 0.9:
            warns.append("[主词密度偏高] %s = %.2f%%（建议压到 0.6%% 以内，避免堆砌嫌疑）"
                         % (name, dens))
    return errors, warns


def write(rel_path, content):
    full = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return len(content)


def main():
    only_check = "--check" in sys.argv
    arts, errs = load_all()

    if not arts:
        print("⚠️  _content/ 下没有文章（%s）" % CONTENT)
        print("    添加第一篇：在 _content/ 放一个 .md 文件，格式见 README")
        return

    errors, warns = check(arts)
    errors = errs + errors

    print("载入 %d 篇\n" % len(arts))
    if errors:
        print("❌ 错误 %d 项：" % len(errors))
        for e in errors:
            print("   " + e)
    if warns:
        print("⚠️  提示 %d 项：" % len(warns))
        for w in warns:
            print("   " + w)
    if errors:
        print("\n构建中止（先修错误）")
        sys.exit(1)
    if only_check:
        print("\n✅ 校验通过")
        return

    # 写文章页
    for m in arts:
        html = build_article_page(m, m["_body"], m["_faqs"], m["_toc"])
        # 同簇相关文章（此时全部 meta 已知）
        same = [x for x in arts if x["cluster"] == m["cluster"] and x["slug"] != m["slug"]]
        if same:
            links = "".join(
                '<a href="../%s/">%s <span>→</span></a>' % (x["slug"], esc(x["title"]))
                for x in same
            )
            related = ('</div></div>\n<section><div class="wrap">'
                       '<h2 class="sec-title">%s的相关问题</h2>'
                       '<div class="linklist">%s</div></div></section>\n'
                       % (esc(CLUSTERS[m["cluster"]][0]), links))
        else:
            related = ""
        html = html.replace("<!-- RELATED:%s -->" % m["cluster"], related)
        write("articles/%s/index.html" % m["slug"], html)

    # 目录页
    write("articles/index.html", build_hub(arts))

    # sitemap
    rebuild_sitemap(arts)

    # 同步 topics.json 的路径
    sync_topics(arts)

    print("\n生成：%d 篇文章页 + 1 个目录页 + sitemap" % len(arts))
    print("✅ 完成")


def rebuild_sitemap(arts):
    """重建 sitemap：主站页面 + 全部文章"""
    from build import PAGES
    from datetime import date
    today = date.today().isoformat()
    urls = []
    for path in PAGES:
        loc = SITE_URL + "/" + path
        pri = "1.0" if path == "" else ("0.8" if path in ("feiyong/", "liucheng/") else "0.7")
        freq = "weekly" if path == "" else "monthly"
        urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>\n"
                    f"    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>")
    # 文章目录页
    urls.append(f"  <url>\n    <loc>{SITE_URL}/articles/</loc>\n    <lastmod>{today}</lastmod>\n"
                f"    <changefreq>daily</changefreq>\n    <priority>0.8</priority>\n  </url>")
    for m in arts:
        urls.append(f"  <url>\n    <loc>{SITE_URL}/articles/{m['slug']}/</loc>\n"
                    f"    <lastmod>{m['date']}</lastmod>\n"
                    f"    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    write("sitemap.xml", xml)
    # 把站点总页数写进 robots（信息性）
    robots = f"""User-agent: *
Allow: /

# 站长平台验证文件对搜索无价值，不必抓取
Disallow: /verify-baidu.txt
Disallow: /baidu_verify_
Disallow: /_content/
Disallow: /_topics/

Sitemap: {SITE_URL}/sitemap.xml
"""
    write("robots.txt", robots)


def sync_topics(arts):
    """把已写好的文章 slug 回写到 topics.json，标记为已用"""
    if not os.path.isfile(TOPICS_FILE):
        return
    try:
        data = json.load(open(TOPICS_FILE, encoding="utf-8"))
    except Exception:
        return
    done = {m["slug"]: m["date"] for m in arts}
    changed = 0
    for t in data.get("topics", []):
        if t.get("slug") in done and t.get("status") != "已用":
            t["status"] = "已用"
            t["used_date"] = done[t["slug"]]
            changed += 1
    if changed:
        json.dump(data, open(TOPICS_FILE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print("  同步 topics.json：%d 条标记为已用" % changed)


if __name__ == "__main__":
    main()
