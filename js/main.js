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

  if (!/^1[3-9]\d{9}$/.test(phone)) {
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
