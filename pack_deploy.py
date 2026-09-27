#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包发布产物到 ../deploy/
=========================
为什么需要这个脚本：
  手工拷贝产物极易漏掉「不带常规扩展名、但必须上线」的文件——
  之前就漏过 `_redirects`（导致百度验证文件的 200 重写失效）。
  把「哪些文件要上线」固化进代码，比靠人记住可靠。

规则：
  · 只拷贝「运行站点真正需要的文件」（白名单），不碰源码/文档/脚本
  · `_redirects`、验证文件必须带上（否则验证会 404/308）
  · 拷贝前清空 deploy/ 里的旧产物，避免删过的页面还留在线上

用法：python pack_deploy.py
"""
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.normpath(os.path.join(BASE, "..", "deploy"))

# 站点根目录下需要上线的单个文件
ROOT_FILES = [
    "index.html",
    "robots.txt",
    "sitemap.xml",
    # Cloudflare Pages 规则：百度验证文件的 200 重写 + .html→目录 301
    "_redirects",
    # 站长平台验证文件
    "BingSiteAuth.xml",
    "verify-baidu.txt",
]

# 需要整体拷贝的目录（页面 + 资源）
DIRS = [
    "css",
    "js",
    "feiyong", "liucheng", "cailiao", "dizhi-guakao", "shijian",
    "gezhong", "yinhang", "dailijizhang", "wangshang", "faq", "women",
]

# 绝不外发的（防误拷）
EXCLUDE_NAMES = {
    "config.local.json", ".gitignore", ".git", "__pycache__", ".wrangler",
    "_shots", "deploy",
}


def ensure_clean(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def main():
    os.makedirs(DEST, exist_ok=True)

    # 清掉旧的同名产物（用白名单反向清理，不整目录删，避免误删无关内容）
    for name in os.listdir(DEST):
        if name in EXCLUDE_NAMES:
            continue
        ensure_clean(os.path.join(DEST, name))

    copied = 0

    for name in ROOT_FILES:
        src = os.path.join(BASE, name)
        if not os.path.isfile(src):
            print("  [警告] 缺少文件：%s（上线后会 404）" % name)
            continue
        shutil.copy2(src, os.path.join(DEST, name))
        copied += 1
        print("  + %s" % name)

    for d in DIRS:
        src = os.path.join(BASE, d)
        if not os.path.isdir(src):
            print("  [警告] 缺少目录：%s" % d)
            continue
        dst = os.path.join(DEST, d)
        shutil.copytree(src, dst,
                        ignore=shutil.ignore_patterns(*EXCLUDE_NAMES))
        copied += 1
        print("  + %s/" % d)

    # 安全检查：产物里不该出现任何密钥文件
    leaked = []
    for root, _dirs, files in os.walk(DEST):
        for f in files:
            if f in ("config.local.json",) or f.endswith(".pyc"):
                leaked.append(os.path.join(root, f))
    if leaked:
        print("\n❌ 产物中发现不该上线的文件，已删除：")
        for p in leaked:
            print("   - %s" % p)
            os.remove(p)

    print("\n完成，共 %d 项 → %s" % (copied, DEST))
    print("部署命令（在 site/ 目录执行）：")
    print("  npx wrangler pages deploy ../deploy --project-name=shanghaizhucegongsi --commit-dirty=true")


if __name__ == "__main__":
    main()
