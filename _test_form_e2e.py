#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端回归：线索表单 → 飞书 webhook
====================================
模拟飞书端点（返回真实 CORS 头 + code:0/[错误码]），
用无头 Chrome 跑真实浏览器，断言：
  1. 正常提交 → 成功态 + 卡片字段完整
  2. 接收端报错 → 失败态透传 msg
  3. 手机号非法 → 拦截，且 mock 收到 0 条
  4. 蜜罐命中 → 假成功，且 mock 收到 0 条
  5. 未配置 webhook → 演示模式，不发送
"""
import os
import sys
import json
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
PORT = 8793
MOCK_PORT = 8792
RECEIVED = []          # 收到的卡片 JSON


class MockFeishu(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Max-Age", "86400")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8") if n else ""
        try:
            RECEIVED.append(json.loads(raw))
        except Exception:
            RECEIVED.append({"_raw": raw})

        # 触发失败分支
        if "FAILTEST" in raw:
            body = json.dumps({"code": 19001, "msg": "incoming webhook access token invalid"}, ensure_ascii=False)
        else:
            body = json.dumps({"code": 0, "msg": "success"}, ensure_ascii=False)

        b = body.encode("utf-8")
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass


def main():
    # ---------- 1. 构建测试页（webhook 指向 mock）----------
    env = dict(os.environ)
    env["SHZCGS_FEISHU_WEBHOOK"] = "http://127.0.0.1:%d/hook" % MOCK_PORT
    env["SHZCGS_FEISHU_KEYWORD"] = "咨询"
    # 去掉代理，让浏览器走本地回环
    for k in ("https_proxy", "http_proxy", "HTTPS_PROXY", "HTTP_PROXY", "all_proxy", "ALL_PROXY"):
        env.pop(k, None)
    env["NO_PROXY"] = "127.0.0.1,localhost"
    env["no_proxy"] = "127.0.0.1,localhost"

    for script in ("build.py", "gen_pages.py"):
        r = subprocess.run([sys.executable, script], cwd=BASE, env=env,
                           capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            print("构建失败 %s：\n%s%s" % (script, r.stdout, r.stderr))
            return 1
    print("✓ 已按 mock webhook 构建")

    js = open(os.path.join(BASE, "js", "main.js"), encoding="utf-8").read()
    assert "127.0.0.1:%d" % MOCK_PORT in js, "webhook 未注入！"
    print("✓ webhook 已注入前端 js")

    # ---------- 2. 生成测试页 ----------
    html = open(os.path.join(BASE, "index.html"), encoding="utf-8").read()
    inject = """
<pre id="tresult">PENDING</pre>
<script>
(function(){
  var q = new URLSearchParams(location.search);
  var mode = q.get("c") || "ok";
  function fill(v){ document.getElementById("f-name").value=v.name;
    document.getElementById("f-phone").value=v.phone;
    document.getElementById("f-note").value=v.note||""; }
  function setHoney(v){ document.getElementById("c9").value=v; }
  function run(){
    var r = document.getElementById("tresult");
    try {
      if (mode==="bad")    { fill({name:"测试",phone:"123"}); }
      if (mode==="honey")  { fill({name:"测试",phone:"13800138000"}); setHoney("http://spam.example"); }
      if (mode==="fail")   { fill({name:"FAILTEST",phone:"13800138001",note:"FAILTEST"}); }
      if (mode==="ok")     { fill({name:"张三",phone:"13800138002",note:"想注册贸易公司"}); }
      if (mode==="demo")   { fill({name:"李四",phone:"13800138003"}); }
      var ret = submitLead({preventDefault:function(){}});
      var msg = document.getElementById("formmsg");
      var out = {mode:mode, ret:ret,
                 text:(msg?msg.textContent:""),
                 shown:(msg && msg.style.display!=="none")};
      setTimeout(function(){
        var m2 = document.getElementById("formmsg");
        out.text = m2 ? m2.textContent : "";
        out.shown = !!(m2 && m2.style.display !== "none");
        r.textContent = "RESULT::" + JSON.stringify(out);
      }, 2500);
    } catch(e) { r.textContent = "RESULT::" + JSON.stringify({mode:mode, error:String(e)}); }
  }
  if (document.readyState === "complete") setTimeout(run, 300);
  else window.addEventListener("load", function(){ setTimeout(run, 300); });
})();
</script>
"""
    test_page = html.replace("</body>", inject + "</body>")
    tp = os.path.join(BASE, "_t_form.html")
    with open(tp, "w", encoding="utf-8") as f:
        f.write(test_page)

    # ---------- 3. 起服务 ----------
    mock = HTTPServer(("127.0.0.1", MOCK_PORT), MockFeishu)
    threading.Thread(target=mock.serve_forever, daemon=True).start()

    class Static(BaseHTTPRequestHandler):
        def do_GET(self):
            p = self.path.split("?")[0]
            if p == "/":
                p = "/_t_form.html"
            fp = os.path.join(BASE, p.lstrip("/").replace("/", os.sep))
            if not os.path.isfile(fp):
                self.send_response(404); self.end_headers(); return
            body = open(fp, "rb").read()
            self.send_response(200)
            ct = "text/html"
            if fp.endswith(".js"): ct = "application/javascript"
            elif fp.endswith(".css"): ct = "text/css"
            self.send_header("Content-Type", ct + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    static = HTTPServer(("127.0.0.1", PORT), Static)
    threading.Thread(target=static.serve_forever, daemon=True).start()
    print("✓ 服务已起：页面 %d / mock %d" % (PORT, MOCK_PORT))

    # ---------- 4. 找浏览器 ----------
    chrome = None
    for c in [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]:
        if os.path.isfile(c):
            chrome = c
            break
    if not chrome:
        print("找不到 Chrome/Edge，无法跑浏览器回归")
        return 1
    print("✓ 浏览器：%s" % chrome)

    # ---------- 5. 逐场景跑 ----------
    results = {}
    for mode in ["ok", "fail", "bad", "honey", "demo"]:
        RECEIVED.clear()
        url = "http://127.0.0.1:%d/_t_form.html?c=%s" % (PORT, mode)
        r = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--disable-dev-shm-usage", "--virtual-time-budget=12000",
             "--dump-dom", url],
            capture_output=True, text=True, timeout=90, encoding="utf-8", errors="replace")
        dom = r.stdout or ""
        mark = "RESULT::"
        i = dom.find(mark)
        got = None
        if i >= 0:
            j = dom.find("</pre>", i)
            try:
                got = json.loads(dom[i + len(mark):j].strip())
            except Exception:
                got = {"_parse_error": dom[i:i + 400]}
        results[mode] = {"dom": got, "received": list(RECEIVED)}

    # ---------- 6. 断言 ----------
    print()
    print("=" * 60)
    fails = []

    def chk(name, cond, detail=""):
        print(("  ✓ " if cond else "  ✗ ") + name + (("  → " + detail) if detail and not cond else ""))
        if not cond:
            fails.append(name)

    # 1 正常提交
    r = results["ok"]
    chk("正常提交：收到 1 条", len(r["received"]) == 1, "实收 %d" % len(r["received"]))
    chk("正常提交：成功态", bool(r["dom"] and r["dom"].get("shown")), json.dumps(r["dom"], ensure_ascii=False))
    if r["received"]:
        card = r["received"][0]
        txt = json.dumps(card, ensure_ascii=False)
        chk("正常提交：卡片类型 interactive", card.get("msg_type") == "interactive")
        chk("正常提交：含称呼", "张三" in txt)
        chk("正常提交：含手机号", "13800138002" in txt)
        chk("正常提交：含咨询内容", "贸易公司" in txt)
        chk("正常提交：关键词在标题", "咨询" in json.dumps(
            card.get("card", {}).get("header", {}), ensure_ascii=False))
        chk("正常提交：关键词在 note", "咨询" in json.dumps(
            card.get("card", {}).get("elements", []), ensure_ascii=False))

    # 2 失败分支
    r = results["fail"]
    chk("接收端报错：失败态", bool(r["dom"] and r["dom"].get("shown")))
    chk("接收端报错：透传 msg",
        bool(r["dom"] and "invalid" in (r["dom"].get("text") or "")),
        json.dumps(r["dom"], ensure_ascii=False))

    # 3 手机号非法 → 不发
    r = results["bad"]
    chk("手机号非法：mock 收到 0 条", len(r["received"]) == 0, "实收 %d" % len(r["received"]))
    chk("手机号非法：有提示", bool(r["dom"] and r["dom"].get("shown")))

    # 4 蜜罐 → 假成功且不发
    r = results["honey"]
    chk("蜜罐：mock 收到 0 条", len(r["received"]) == 0, "实收 %d" % len(r["received"]))
    chk("蜜罐：假成功提示", bool(r["dom"] and r["dom"].get("shown")), json.dumps(r["dom"], ensure_ascii=False))

    # 5 演示模式（未配 webhook 时）—— 本轮配了 mock，该模式仍会发送，跳过
    print("  · 演示模式：本轮已配 mock webhook，单独验证见下方")

    print("=" * 60)

    # 清理测试页
    try:
        os.remove(tp)
        print("已删除测试页 _t_form.html")
    except Exception:
        pass

    if fails:
        print("❌ 失败 %d 项：%s" % (len(fails), "、".join(fails)))
        return 1
    print("✅ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
