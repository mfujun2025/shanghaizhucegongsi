#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
站点自检脚本：检查死链、元信息、必需要素
用法：python check_site.py
"""
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ERRORS = []
WARNS = []


def find_pages():
    pages = []
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in ("css", "js", "__pycache__", "node_modules")]
        if "index.html" in files:
            pages.append(os.path.join(root, "index.html"))
    return sorted(pages)


def check_links(pages):
    """检查所有 href 是否指向存在的文件"""
    for page in pages:
        rel = os.path.relpath(page, BASE).replace("\\", "/")
        with open(page, encoding="utf-8") as f:
            html = f.read()
        # 检查相对链接（排除锚点、tel、mailto、http）
        for m in re.finditer(r'href="([^"]+)"', html):
            href = m.group(1)
            if href.startswith(("http", "tel:", "mailto:", "#")):
                continue
            target_path, _, anchor = href.partition("#")
            # 剥掉查询串（资源指纹 ?v=xxxx 不是文件路径的一部分）
            target_path = target_path.partition("?")[0]
            if not target_path:
                continue
            if target_path == "./":
                target = os.path.join(os.path.dirname(page), "index.html")
            else:
                target = os.path.normpath(os.path.join(os.path.dirname(page), target_path))
                if target.endswith(("/", "\\")) or not os.path.splitext(target)[1]:
                    target = os.path.join(target, "index.html")
            if not os.path.exists(target):
                ERRORS.append(f"[死链] {rel} → {href}")
        # 检查资源链接
        for m in re.finditer(r'(?:src|href)="([^"]*\.(?:css|js)(?:\?[^"]*)?)"', html):
            r = m.group(1)
            if r.startswith(("http", "//")):
                continue
            r_clean = r.partition("?")[0]
            t = os.path.normpath(os.path.join(os.path.dirname(page), r_clean))
            if not os.path.exists(t):
                ERRORS.append(f"[资源缺失] {rel} → {r}")


def check_meta(pages):
    for page in pages:
        rel = os.path.relpath(page, BASE).replace("\\", "/")
        with open(page, encoding="utf-8") as f:
            html = f.read()
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        if not title or len(title.group(1).strip()) < 8:
            ERRORS.append(f"[标题缺失/过短] {rel}")
        else:
            tlen = len(title.group(1).strip())
            if tlen > 60:
                WARNS.append(f"[标题过长 {tlen} 字符] {rel} → {title.group(1)[:50]}…")
        desc = re.search(r'name="description" content="(.*?)"', html, re.S)
        if not desc:
            ERRORS.append(f"[描述缺失] {rel}")
        else:
            dlen = len(desc.group(1))
            if dlen < 40:
                WARNS.append(f"[描述偏短 {dlen}] {rel}")
            if dlen > 160:
                WARNS.append(f"[描述偏长 {dlen}] {rel}")
        if 'rel="canonical"' not in html:
            ERRORS.append(f"[canonical 缺失] {rel}")
        if 'name="viewport"' not in html:
            ERRORS.append(f"[viewport 缺失] {rel}")


def check_elements(pages):
    for page in pages:
        rel = os.path.relpath(page, BASE).replace("\\", "/")
        with open(page, encoding="utf-8") as f:
            html = f.read()
        if "tel:17652523536" not in html:
            ERRORS.append(f"[缺电话入口] {rel}")
        if "17652523536" not in html:
            WARN_PHONE = True
        if "免责声明" not in html and "不构成法律" not in html:
            ERRORS.append(f"[缺免责声明] {rel}")
        if rel != "index.html" and "breadcrumb" not in html:
            WARNS.append(f"[缺面包屑] {rel}")


def check_wordcount(pages):
    """正文内容字数（去掉标签）

    阈值按页面类型分：
      · 文章页 articles/<slug>/  → 正文 ≥1500（长文，撑长尾覆盖）
      · 导航型页面（首页/目录页）→ 不设下限（本来就短）
      · 其他内页               → ≥600
    """
    for page in pages:
        rel = os.path.relpath(page, BASE).replace("\\", "/")
        with open(page, encoding="utf-8") as f:
            html = f.read()
        # 只取 article 区域
        m = re.search(r'<div class="article">(.*?)</div>\s*</div>', html, re.S)
        seg = m.group(1) if m else html
        text = re.sub(r"<[^>]+>", "", seg)
        text = re.sub(r"\s+", "", text)
        cnt = len(re.findall(r"[\u4e00-\u9fff]", text))

        is_article = re.match(r"^articles/[^/]+/index\.html$", rel)
        is_hub = rel in ("index.html", "articles/index.html")
        if is_article and cnt < 1500:
            WARNS.append(f"[文章正文偏短 {cnt} 字，目标 ≥1500] {rel}")
        elif not is_hub and not is_article and cnt < 600:
            WARNS.append(f"[正文偏短 {cnt} 字] {rel}")
        print(f"    {rel:38s} 正文中文字数 ≈ {cnt}")


def main():
    pages = find_pages()
    print(f"发现 {len(pages)} 个页面\n")
    print("检查内链...")
    check_links(pages)
    print("检查元信息...")
    check_meta(pages)
    print("检查必备元素...")
    check_elements(pages)
    print("统计正文字数...")
    check_wordcount(pages)

    print("\n" + "=" * 52)
    if ERRORS:
        print(f"❌ 错误 {len(ERRORS)} 项：")
        for e in ERRORS:
            print("   " + e)
    else:
        print("✅ 无错误")
    if WARNS:
        print(f"\n⚠️  提示 {len(WARNS)} 项：")
        for w in WARNS:
            print("   " + w)
    else:
        print("✅ 无提示")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
