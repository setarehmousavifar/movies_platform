/**
 * Progressive enhancement: call /api/v1/ with session + CSRF.
 * Forms/links keep server actions as no-JS fallback.
 */
(function () {
  'use strict';

  var API = '/api/v1';

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : '';
  }

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) {
      return meta.content;
    }
    return getCookie('csrftoken');
  }

  function toast(message, kind) {
    var container = document.getElementById('catalog-alert-toast');
    if (!container) {
      window.alert(message);
      return;
    }
    var bg = kind === 'error' ? 'text-bg-danger' : kind === 'success' ? 'text-bg-success' : 'text-bg-dark';
    var el = document.createElement('div');
    el.className = 'toast align-items-center ' + bg + ' border-0 show';
    el.setAttribute('role', 'status');
    el.innerHTML =
      '<div class="d-flex"><div class="toast-body"></div>' +
      '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>';
    el.querySelector('.toast-body').textContent = message;
    container.appendChild(el);
    setTimeout(function () {
      el.remove();
    }, 4500);
  }

  function setBusy(el, busy) {
    if (!el) return;
    if (el.tagName === 'A') {
      el.setAttribute('aria-busy', busy ? 'true' : 'false');
      el.style.pointerEvents = busy ? 'none' : '';
      el.style.opacity = busy ? '0.7' : '';
      if (busy) {
        el.dataset._label = el.textContent;
        el.textContent = 'Working…';
      } else if (el.dataset._label) {
        el.textContent = el.dataset._label;
        delete el.dataset._label;
      }
      return;
    }
    el.disabled = !!busy;
    el.classList.toggle('disabled', !!busy);
    if (busy) {
      el.dataset._label = el.textContent;
      el.textContent = 'Working…';
    } else if (el.dataset._label) {
      el.textContent = el.dataset._label;
      delete el.dataset._label;
    }
  }

  function apiRequest(method, path, body) {
    var headers = {
      Accept: 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    };
    if (body !== undefined) {
      headers['Content-Type'] = 'application/json';
    }
    var token = csrfToken();
    if (token && method !== 'GET' && method !== 'HEAD') {
      headers['X-CSRFToken'] = token;
    }
    return fetch(API + path, {
      method: method,
      credentials: 'same-origin',
      headers: headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }).then(function (res) {
      return res.text().then(function (text) {
        var data = null;
        if (text) {
          try {
            data = JSON.parse(text);
          } catch (err) {
            data = { detail: text };
          }
        }
        if (!res.ok) {
          var msg =
            (data && (data.detail || data.code)) ||
            'Request failed (' + res.status + ')';
          if (typeof msg === 'object') {
            msg = JSON.stringify(msg);
          }
          var err = new Error(msg);
          err.status = res.status;
          err.data = data;
          throw err;
        }
        return data;
      });
    });
  }

  function findEngagementItem(listPath, kind, id) {
    return apiRequest('GET', listPath).then(function (data) {
      var rows = Array.isArray(data) ? data : data && data.results ? data.results : [];
      var key = kind;
      var want = Number(id);
      for (var i = 0; i < rows.length; i++) {
        if (Number(rows[i][key]) === want) {
          return rows[i];
        }
      }
      return null;
    });
  }

  function handleFavoriteWatchlist(form, kind, id, listPath, isAdd, successLabel) {
    var btn = form.querySelector('button[type="submit"]');
    setBusy(btn, true);
    var payload = {};
    payload[kind] = Number(id);

    var chain;
    if (isAdd) {
      chain = apiRequest('POST', listPath, payload).then(function () {
        toast(successLabel || 'Saved.', 'success');
        if (btn) {
          btn.dataset._label = listPath.indexOf('favorite') >= 0 ? 'Remove from Favorites' : 'Remove from Watchlist';
        }
        var nextAction = form.action.replace('/add/', '/remove/');
        form.action = nextAction;
      });
    } else {
      chain = findEngagementItem(listPath, kind, id).then(function (item) {
        if (!item) {
          toast('Item already removed.', 'success');
          return;
        }
        return apiRequest('DELETE', listPath + item.id + '/').then(function () {
          toast('Removed.', 'success');
          if (btn) {
            btn.dataset._label = listPath.indexOf('favorite') >= 0 ? 'Add to Favorites' : 'Add to Watchlist';
          }
          form.action = form.action.replace('/remove/', '/add/');
          if (form.closest('.list-group-item')) {
            form.closest('.list-group-item').remove();
          }
        });
      });
    }

    return chain
      .catch(function (err) {
        if (err.status === 403 || err.status === 401) {
          toast('Please log in to continue.', 'error');
        } else {
          toast(err.message || 'Something went wrong.', 'error');
        }
      })
      .finally(function () {
        setBusy(btn, false);
      });
  }

  document.addEventListener(
    'submit',
    function (e) {
      var form = e.target;
      if (!(form instanceof HTMLFormElement)) return;

      var action = form.getAttribute('action') || '';
      var fav = action.match(/\/favorites\/(add|remove)\/(movie|series|animation)\/(\d+)\/?/);
      if (fav) {
        e.preventDefault();
        handleFavoriteWatchlist(
          form,
          fav[2],
          fav[3],
          '/favorites/',
          fav[1] === 'add',
          fav[1] === 'add' ? 'Added to favorites.' : 'Removed from favorites.'
        );
        return;
      }

      var watch = action.match(/\/watchlist\/(add|remove)\/(movie|series|animation)\/(\d+)\/?/);
      if (watch) {
        e.preventDefault();
        handleFavoriteWatchlist(
          form,
          watch[2],
          watch[3],
          '/watchlist/',
          watch[1] === 'add',
          watch[1] === 'add' ? 'Added to watchlist.' : 'Removed from watchlist.'
        );
        return;
      }

      var notif = action.match(/\/notifications\/(\d+)\/read\/?/);
      if (notif) {
        e.preventDefault();
        var btn = form.querySelector('button[type="submit"]');
        setBusy(btn, true);
        apiRequest('POST', '/notifications/' + notif[1] + '/read/', {})
          .then(function () {
            toast('Marked as read.', 'success');
            var row = form.closest('.list-group-item');
            if (row) {
              row.classList.remove('list-group-item-warning');
              form.replaceWith(Object.assign(document.createElement('span'), { className: 'badge bg-success', textContent: 'Read' }));
            }
          })
          .catch(function (err) {
            toast(err.message || 'Could not update notification.', 'error');
          })
          .finally(function () {
            setBusy(btn, false);
          });
      }
    },
    true
  );

  document.addEventListener(
    'click',
    function (e) {
      var link = e.target.closest('a[href*="/downloads/"]');
      if (!link || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey) {
        return;
      }
      var match = (link.getAttribute('href') || '').match(/\/downloads\/(\d+)\/?/);
      if (!match) return;

      e.preventDefault();
      setBusy(link, true);
      apiRequest('GET', '/downloads/' + match[1] + '/')
        .then(function (data) {
          if (data && data.download_url) {
            window.location.href = data.download_url;
          } else {
            toast('Download URL unavailable.', 'error');
          }
        })
        .catch(function (err) {
          if (err.status === 403) {
            toast('Premium subscription required to download.', 'error');
            window.setTimeout(function () {
              window.location.href = '/subscription/';
            }, 1200);
          } else if (err.status === 401) {
            toast('Please log in to download.', 'error');
            window.location.href = '/login/';
          } else {
            toast(err.message || 'Download failed.', 'error');
          }
        })
        .finally(function () {
          setBusy(link, false);
        });
    },
    true
  );

  window.MoviesAPI = {
    request: apiRequest,
    toast: toast,
  };
})();
