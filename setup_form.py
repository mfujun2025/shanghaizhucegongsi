#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
询单接收端一键配置（上海注册公司.com）
========================================
做什么：
  1. 粘贴飞书自定义机器人 webhook 地址
  2. 校验格式（粘错了会明确提示）
  3. 真发一条测试卡片到群里 —— 你立刻能在飞书看到效果
  4. 写入 config.local.json 并自动重建站点

双击 配置询单.bat 即可运行。
"""
import os
import re
import sys
import json
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_LOCAL = os.path.join(BASE, "config.local.json")
BUILD = os.path.join(BASE, "build.py")

WEBHOOK_RE = re.compile(r"^https://open\.feishu\.cn/open-apis/bot/v2/hook/[A-Za-z0-9_\-]+$")

LINE = "=" * 58


def hr():
    print(LINE)


def ask_webhook():
    print()
    print("请粘贴飞书机器人的 Webhook 地址，然后回车。")
    print()
    print("  获取路径：飞书群 → 右上角 ··· → 设置 → 群机器人")
    print("            → 添加机器人 → 自定义机器人 → 复制 Webhook 地址")
    print()
    try:
        v = input("Webhook 地址：").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n已取消。")
        return None
    return v


def validate(url):
    """返回 (是否合法, 提示)"""
    if not url:
        return False, "地址是空的。"
    if url.startswith("https://open.feishu.cn/open-apis/bot/v2/hook/") and " " in url:
        return False, "地址里有空格，可能复制多了。"
    if "applink.feishu.cn" in url or "/client/" in url:
        return False, ("这是**机器人详情页**的地址，不是 Webhook 地址。\n"
                       "        要的是 https://open.feishu.cn/open-apis/bot/v2/hook/xxxx 这一条。")
    if not WEBHOOK_RE.match(url):
        return False, ("格式对不上。正确格式形如：\n"
                       "        https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx")
    return True, ""


def send_test(webhook, keyword):
    """真发一条和线上格式一致的测试卡片"""
    print()
    print("正在往群里发一条测试卡片…")
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "template": "blue",
                "title": {"tag": "plain_text", "content": "🔔 新" + keyword + " · 上海注册公司.com"}
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md",
                    "content": "**称呼**：测试消息\n**手机号**：13800000000\n**咨询内容**：这是一条配置测试，收到就说明通了"}},
                {"tag": "hr"},
                {"tag": "note", "elements": [{"tag": "plain_text",
                    "content": "来源：setup_form.py 自检 · 类型：" + keyword}]}
            ]
        }
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    try:
        import urllib.request as ureq
        req = ureq.Request(webhook, data=body,
                           headers={"Content-Type": "application/json"}, method="POST")
        proxy = os.environ.get("https_proxy") or os.environ.get("http_proxy")
        if proxy:
            op = ureq.build_opener(ureq.ProxyHandler({"https": proxy, "http": proxy}))
            resp = op.open(req, timeout=20)
        else:
            resp = ureq.urlopen(req, timeout=20)
        data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("  发送失败（网络层）：%s" % e)
        print("  如果你的网络需要代理，先在环境变量里设 https_proxy 再试。")
        return False, "网络异常"

    code = data.get("code")
    msg = data.get("msg") or data.get("StatusMessage") or ""

    if code == 0:
        print("  发送成功！去看看飞书群里收到卡片了没。")
        return True, ""

    tips = {
        19001: "地址无效：复制少了尾巴，或机器人被删/停用了。回群里重新复制一次。",
        19024: "关键词对不上：去群里把机器人的「安全设置」改成自定义关键词，关键词填「%s」。" % keyword,
        19021: "安全设置选了「签名校验」——静态站不能用签名（密钥会暴露在前端），请改成「自定义关键词」。",
        19022: "安全设置选了「IP 白名单」——静态站出口 IP 不固定，用不了，请改成「自定义关键词」。",
        9499:  "请求体格式错或超长。",
        11232: "触发限流了，等一分钟再试。",
    }
    print("  发送失败：code=%s  %s" % (code, msg))
    if code in tips:
        print("  → %s" % tips[code])
    else:
        print("  完整响应：%s" % json.dumps(data, ensure_ascii=False))
    return False, str(msg)


def main():
    print()
    hr()
    print("  上海注册公司.com · 询单接收端配置")
    hr()

    old = {}
    if os.path.isfile(CONFIG_LOCAL):
        try:
            with open(CONFIG_LOCAL, "r", encoding="utf-8") as f:
                old = json.load(f) or {}
            if old.get("feishu_webhook"):
                print("  当前已配置：...%s" % old["feishu_webhook"][-12:])
                print("  （继续操作会覆盖它）")
        except Exception:
            pass

    kw = old.get("feishu_keyword") or "咨询"
    print("  消息关键词：%s" % kw)
    print("  （机器人安全设置里填的必须是这个词，否则发不进来）")
    print()

    url = ask_webhook()
    if url is None:
        return 1
    if not url:
        print("  没输入内容，已取消。")
        return 1

    ok, err = validate(url)
    if not ok:
        print()
        print("  地址有问题：%s" % err)
        print("  已取消，什么都没改。")
        return 1

    ok, _ = send_test(url, kw)
    if not ok:
        print()
        try:
            ans = input("  要不要先保存这个地址、稍后再排查？(y/N)：").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = "n"
        if ans != "y":
            print("  已取消，什么都没改。")
            return 1

    cfg = {"feishu_webhook": url, "feishu_keyword": kw}
    try:
        with open(CONFIG_LOCAL, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        print()
        print("  已写入 config.local.json（此文件在 .gitignore 里，不会进公开仓库）")
    except Exception as e:
        print("  写入失败：%s" % e)
        return 1

    print()
    print("  正在重建站点…")
    try:
        r = subprocess.run([sys.executable, BUILD], cwd=BASE,
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout or "") + (r.stderr or "")
        for ln in out.strip().splitlines():
            print("    " + ln)
    except Exception as e:
        print("    重建失败：%s" % e)
        print("    可以手动跑：python build.py")
        return 1

    hr()
    print("  搞定。")
    print()
    print("  接下来部署上线：")
    print("    npx wrangler pages deploy . --project-name=shanghaizhucegongsi")
    print()
    print("  上线后自测一次：打开网站表单页，填个真实手机号提交，")
    print("  看群里是否收到卡片。收到就通了。")
    hr()
    print()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(1)
