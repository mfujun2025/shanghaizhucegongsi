#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海注册公司.com —— 日更流水线
================================
被定时任务调用。一个命令走完「选题 → 构建 → 打包 → 部署」。

用法：
  python daily_publish.py next            # 只打印今天的选题（供写稿用）
  python daily_publish.py publish         # 构建 + 打包 + 部署（写稿完成后执行）
  python daily_publish.py status          # 查看进度

设计说明：
  · 文章由 AI 现场撰写，写入 _content/<slug>.md 后再跑 publish
  · publish 会：校验 → 构建 → 自检 → 打包 → 部署 → 打印结果
  · 部署 token 优先读环境变量 CLOUDFLARE_API_TOKEN，其次读 config.local.json
    的 cloudflare_api_token（定时任务在全新会话跑，环境变量带不过去，所以必须有后者）
  · 全程幂等：失败重跑不会产生重复内容
"""
import os
import re
import sys
import json
import glob
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = HERE
TOPICS = os.path.join(HERE, "_topics", "topics.json")
CONTENT = os.path.join(HERE, "_content")
PROJECT = "shanghaizhucegongsi"
DEPLOY_DIR = os.path.normpath(os.path.join(HERE, "..", "deploy"))
CONFIG_LOCAL = os.path.join(HERE, "config.local.json")


def get_token():
    """取 Cloudflare API Token。

    优先级：环境变量 > config.local.json。
    加 config 这条是因为**定时任务在全新会话里跑，环境变量不会带过去**，
    只靠 env 会导致日更永远停在"跳过部署"。
    config.local.json 已在 .gitignore 里，token 不会进公开仓库。
    """
    t = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if t:
        return t
    try:
        with open(CONFIG_LOCAL, encoding="utf-8") as f:
            return (json.load(f).get("cloudflare_api_token") or "").strip()
    except (OSError, ValueError):
        return ""


def run(cmd, **kw):
    """执行命令，返回 (returncode, output)

    ⚠️ Windows 下 npx / npm 是 .cmd 批处理，subprocess 不传 shell 会
       报 WinError 2（找不到文件）。这里统一用 shell=True 走系统解析。
       命令列表里都是我们自己拼的固定字符串，不涉及外部输入，无注入风险。
    """
    if isinstance(cmd, (list, tuple)):
        cmd = subprocess.list2cmdline(cmd)
    p = subprocess.run(cmd, shell=True, cwd=BASE,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="ignore", **kw)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def load_topics():
    with open(TOPICS, encoding="utf-8") as f:
        return json.load(f)


def written_count():
    return len(glob.glob(os.path.join(CONTENT, "*.md")))


def cmd_status():
    data = load_topics()
    ts = data["topics"]
    used = [t for t in ts if t.get("status") == "已用"]
    free = [t for t in ts if t.get("status") != "已用"]
    print("选题池：共 %d 条，已用 %d，待用 %d" % (len(ts), len(used), len(free)))
    print("已写文章：%d 篇" % written_count())
    if free:
        n = free[0]
        print("\n下一篇：")
        print("  簇   ：%s" % n["cluster"])
        print("  核心词：%s" % n["core"])
        print("  slug ：%s" % n["slug"])
        print("  角度 ：%s" % n["angle"])
    else:
        print("\n⚠️  选题池已用完，需要补充新选题")


def cmd_next():
    """打印今天要写的选题，供 AI 写稿"""
    data = load_topics()
    free = [t for t in data["topics"] if t.get("status") != "已用"]
    if not free:
        print("池已空")
        return 1
    t = free[0]
    # 已写同簇文章，供写稿时避开重复
    written = []
    for f in glob.glob(os.path.join(CONTENT, "*.md")):
        raw = open(f, encoding="utf-8").read()
        m = re.search(r"^cluster:\s*(\S+)", raw, re.M)
        c = re.search(r"^core:\s*(.+)$", raw, re.M)
        if m and c and m.group(1) == t["cluster"]:
            written.append(c.group(1).strip())

    print("=" * 56)
    print("今日选题")
    print("=" * 56)
    print("core   (核心词，全站唯一) ：%s" % t["core"])
    print("slug   (ASCII，勿改)      ：%s" % t["slug"])
    print("cluster(簇)               ：%s" % t["cluster"])
    print("angle  (写作角度)          ：%s" % t["angle"])
    print()
    print("同簇已写（避免角度重复）：")
    for w in written or ["（本簇还没有文章，这是第一篇）"]:
        print("  · %s" % w)
    print()
    print("写好后保存到：_content/%s.md" % t["slug"])
    print("格式参考：_content/zhuce-company-fee-amount.md")
    return 0


def cmd_publish():
    print("=" * 56)
    print("1/5  校验文章")
    print("=" * 56)
    rc, out = run([sys.executable, "build_articles.py", "--check"])
    print(out.strip())
    if rc != 0:
        print("\n❌ 校验未通过，中止")
        return 1

    print("\n" + "=" * 56)
    print("2/5  构建站点")
    print("=" * 56)
    rc, out = run([sys.executable, "gen_pages.py"])
    if rc != 0:
        print(out[-1500:])
        print("\n❌ 主站构建失败")
        return 1
    rc, out = run([sys.executable, "build_articles.py"])
    print(out.strip())
    if rc != 0:
        print("\n❌ 文章构建失败")
        return 1

    print("\n" + "=" * 56)
    print("3/5  站点自检")
    print("=" * 56)
    rc, out = run([sys.executable, "check_site.py"])
    tail = "\n".join(out.strip().split("\n")[-8:])
    print(tail)
    if rc != 0 or "❌" in out:
        print("\n❌ 自检未通过，中止（修好再发）")
        return 1

    print("\n" + "=" * 56)
    print("4/5  打包发布产物")
    print("=" * 56)
    rc, out = run([sys.executable, "pack_deploy.py"])
    print(out.strip().split("\n")[-4] if out.strip() else "")
    if rc != 0:
        print(out[-800:])
        print("\n❌ 打包失败")
        return 1

    print("\n" + "=" * 56)
    print("5/5  部署到 Cloudflare Pages")
    print("=" * 56)
    token = get_token()
    if not token:
        print("⚠️  未找到 CLOUDFLARE_API_TOKEN（环境变量与 config.local.json 都没有）→ 跳过部署")
        print("    产物已就绪：%s" % DEPLOY_DIR)
        print("    手动部署：npx wrangler pages deploy ../deploy --project-name=%s" % PROJECT)
        return 0

    env = dict(os.environ)
    env["CLOUDFLARE_API_TOKEN"] = token
    rc, out = run(["npx", "--yes", "wrangler@4", "pages", "deploy", "../deploy",
                   "--project-name=%s" % PROJECT, "--commit-dirty=true"], env=env)
    lines = out.strip().split("\n")
    for ln in lines[-12:]:
        print("  " + ln)
    if rc != 0:
        print("\n❌ 部署失败（构建产物已就绪，可重跑 publish）")
        return 1

    print("\n✅ 发布完成")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "next":
        return cmd_next()
    if cmd == "publish":
        return cmd_publish()
    if cmd == "status":
        cmd_status()
        return 0
    print("未知命令：%s" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
