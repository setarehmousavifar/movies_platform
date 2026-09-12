/**
 * Optional WebSocket client for breaking catalog alerts.
 * Works when the app is served via Daphne/ASGI (see PHASE5_ADVANCED.md).
 */
(function () {
  var protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  var url = protocol + '//' + window.location.host + '/ws/alerts/';
  var container = document.getElementById('catalog-alert-toast') || document.getElementById('breaking-alert-toast');
  if (!container || typeof WebSocket === 'undefined') {
    return;
  }

  function showToast(message) {
    var el = document.createElement('div');
    el.className = 'toast align-items-center text-bg-dark border-0 show';
    el.setAttribute('role', 'alert');
    el.innerHTML =
      '<div class="d-flex"><div class="toast-body"></div>' +
      '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>';
    el.querySelector('.toast-body').textContent = message;
    container.appendChild(el);
    setTimeout(function () {
      el.remove();
    }, 8000);
  }

  try {
    var socket = new WebSocket(url);
    socket.onmessage = function (event) {
      try {
        var data = JSON.parse(event.data);
        showToast(data.message || data.title || 'New catalog update');
      } catch (err) {
        /* ignore malformed payloads */
      }
    };
  } catch (err) {
    /* runserver without Channels WS is fine */
  }
})();
