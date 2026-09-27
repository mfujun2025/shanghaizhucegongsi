/* 上海注册公司.com 全站脚本 */
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
  webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/efab23c8-23da-40fa-8cf6-ba42da4495a9",
  keyword: "上海注册公司",
  site: "上海注册公司.com",
  phone: "17652523536"
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
        { tag: "div", text: { tag: "lark_md", content: lines.join("\n") || "（未填写）" } },
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

  if (!/^1[3-9]\d{9}$/.test(phone)) {
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
