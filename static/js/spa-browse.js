(() => {
  const cfg = window.MP_SPA || {};
  const API = (cfg.apiBase || '/api/v1').replace(/\/$/, '');
  const STORAGE_KEY = 'mp_spa_tokens';

  const main = document.getElementById('spa-main');
  const authSlot = document.getElementById('spa-auth-slot');
  const toastEl = document.getElementById('spa-toast');

  const state = {
    user: null,
    tokens: loadTokens(),
  };

  function loadTokens() {
    try {
      return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || 'null');
    } catch {
      return null;
    }
  }

  function saveTokens(tokens) {
    state.tokens = tokens;
    if (tokens) sessionStorage.setItem(STORAGE_KEY, JSON.stringify(tokens));
    else sessionStorage.removeItem(STORAGE_KEY);
  }

  function toast(message) {
    toastEl.hidden = false;
    toastEl.textContent = message;
    clearTimeout(toast._t);
    toast._t = setTimeout(() => {
      toastEl.hidden = true;
    }, 2800);
  }

  async function api(path, options = {}) {
    const headers = Object.assign({ Accept: 'application/json' }, options.headers || {});
    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    if (state.tokens?.access) {
      headers.Authorization = `Bearer ${state.tokens.access}`;
    }
    let res = await fetch(`${API}${path}`, { ...options, headers });
    if (res.status === 401 && state.tokens?.refresh && !options._retried) {
      const refreshed = await refreshAccess();
      if (refreshed) return api(path, { ...options, _retried: true });
    }
    return res;
  }

  async function refreshAccess() {
    if (!state.tokens?.refresh) return false;
    const res = await fetch(`${API}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ refresh: state.tokens.refresh }),
    });
    if (!res.ok) {
      saveTokens(null);
      state.user = null;
      return false;
    }
    const data = await res.json();
    saveTokens({
      access: data.access,
      refresh: data.refresh || state.tokens.refresh,
    });
    return true;
  }

  async function ensureUser() {
    if (!state.tokens?.access) {
      state.user = null;
      return null;
    }
    const res = await api('/auth/me/');
    if (!res.ok) {
      state.user = null;
      return null;
    }
    state.user = await res.json();
    return state.user;
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function posterHtml(poster, title) {
    if (poster) {
      return `<img src="${escapeHtml(poster)}" alt="${escapeHtml(title)} poster" width="300" height="210" loading="lazy" decoding="async">`;
    }
    return `<div class="spa-card-ph" aria-hidden="true"></div>`;
  }

  function cardHtml(item, kind) {
    const href = `#/${kind}/${item.id}`;
    const meta = item.overall_rating != null ? `★ ${item.overall_rating}` : '';
    return `
      <article class="spa-card">
        <a href="${href}">
          ${posterHtml(item.poster, item.title)}
          <div class="spa-card-body">
            <h3>${escapeHtml(item.title)}</h3>
            <p>${escapeHtml(meta)}</p>
          </div>
        </a>
      </article>`;
  }

  function setActiveNav(route) {
    document.querySelectorAll('.spa-nav a').forEach((a) => {
      a.classList.toggle('is-active', a.dataset.route === route);
    });
  }

  function renderAuth() {
    if (state.user) {
      authSlot.innerHTML = `
        <span class="spa-user">${escapeHtml(state.user.username)}${state.user.is_premium ? ' · premium' : ''}</span>
        <button type="button" class="spa-btn" id="spa-logout">Log out</button>`;
      document.getElementById('spa-logout').onclick = logout;
    } else {
      authSlot.innerHTML = `<a class="spa-btn spa-btn-primary" href="#/login">API login</a>`;
    }
  }

  async function logout() {
    try {
      if (state.tokens?.refresh) {
        await api('/auth/logout/', {
          method: 'POST',
          body: JSON.stringify({ refresh: state.tokens.refresh }),
        });
      }
    } catch {
      /* ignore */
    }
    saveTokens(null);
    state.user = null;
    toast('Logged out');
    location.hash = '#/movies';
    await boot();
  }

  async function renderLogin() {
    setActiveNav('');
    main.innerHTML = `
      <form class="spa-login" id="spa-login-form">
        <h1>JWT login</h1>
        <p class="spa-detail-meta" style="margin-bottom:1rem">Uses <code>/api/v1/auth/token/</code>. Demo: admin / admin123 after seed.</p>
        <div class="field">
          <label for="spa-user">Username</label>
          <input id="spa-user" name="username" autocomplete="username" required>
        </div>
        <div class="field">
          <label for="spa-pass">Password</label>
          <input id="spa-pass" name="password" type="password" autocomplete="current-password" required>
        </div>
        <button class="spa-btn spa-btn-primary" type="submit">Get tokens</button>
        <p class="spa-error" id="spa-login-error" hidden></p>
      </form>`;
    document.getElementById('spa-login-form').onsubmit = async (e) => {
      e.preventDefault();
      const err = document.getElementById('spa-login-error');
      err.hidden = true;
      const username = document.getElementById('spa-user').value.trim();
      const password = document.getElementById('spa-pass').value;
      const btn = e.target.querySelector('button');
      btn.disabled = true;
      try {
        const res = await fetch(`${API}/auth/token/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({ username, password }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          err.textContent = data.detail || 'Login failed';
          err.hidden = false;
          return;
        }
        saveTokens({ access: data.access, refresh: data.refresh });
        await ensureUser();
        toast(`Signed in as ${state.user.username}`);
        location.hash = '#/recommended';
        await route();
      } finally {
        btn.disabled = false;
      }
    };
  }

  async function renderList(kind, page = 1) {
    setActiveNav(kind);
    const titles = { movies: 'Movies', series: 'Series', animations: 'Animations' };
    main.innerHTML = `<div class="spa-hero"><h1>${titles[kind]}</h1><p>Paginated list from <code>/api/v1/${kind}/</code>.</p></div><p class="spa-loading">Loading…</p>`;
    const res = await api(`/${kind}/?page=${page}`);
    if (!res.ok) {
      main.innerHTML = `<p class="spa-error">Could not load ${kind} (${res.status}).</p>`;
      return;
    }
    const data = await res.json();
    const results = data.results || data;
    const cards = results.length
      ? `<div class="spa-grid">${results.map((item) => cardHtml(item, kind)).join('')}</div>`
      : `<p class="spa-empty">No titles found.</p>`;
    let pager = '';
    if (data.next || data.previous) {
      const nextPage = data.next ? page + 1 : null;
      const prevPage = data.previous ? page - 1 : null;
      pager = `<div class="spa-pager">
        <button class="spa-btn" ${prevPage ? '' : 'disabled'} data-page="${prevPage || ''}">Previous</button>
        <span class="spa-detail-meta">Page ${page}</span>
        <button class="spa-btn" ${nextPage ? '' : 'disabled'} data-page="${nextPage || ''}">Next</button>
      </div>`;
    }
    main.innerHTML = `
      <div class="spa-hero"><h1>${titles[kind]}</h1><p>Paginated list from <code>/api/v1/${kind}/</code>.</p></div>
      ${cards}${pager}`;
    main.querySelectorAll('.spa-pager button[data-page]').forEach((btn) => {
      btn.onclick = () => {
        const p = Number(btn.dataset.page);
        if (p) renderList(kind, p);
      };
    });
  }

  async function renderDetail(kind, id) {
    setActiveNav(kind);
    main.innerHTML = `<p class="spa-loading">Loading…</p>`;
    const res = await api(`/${kind}/${id}/`);
    if (!res.ok) {
      main.innerHTML = `<p class="spa-error">Not found (${res.status}).</p>`;
      return;
    }
    const item = await res.json();
    const genres = (item.genres || []).map((g) => g.genre_name || g).join(', ') || '—';
    const poster = item.poster
      ? `<img src="${escapeHtml(item.poster)}" alt="" width="220" height="320" fetchpriority="high">`
      : `<div class="spa-detail-ph" aria-hidden="true"></div>`;
    main.innerHTML = `
      <article class="spa-detail">
        <div>${poster}</div>
        <div>
          <p><a href="#/${kind}">← Back</a></p>
          <h1>${escapeHtml(item.title)}</h1>
          <div class="spa-detail-meta">
            <p>Rating: ${escapeHtml(item.overall_rating)} / 10 · Views: ${escapeHtml(item.view_count)}</p>
            <p>Genres: ${escapeHtml(genres)}</p>
            <p>${escapeHtml(item.description || '')}</p>
            ${item.ai_summary ? `<p><strong>AI:</strong> ${escapeHtml(item.ai_summary)}</p>` : ''}
          </div>
          <div class="spa-actions" id="spa-detail-actions"></div>
        </div>
      </article>`;
    const actions = document.getElementById('spa-detail-actions');
    if (!state.user) {
      actions.innerHTML = `<a class="spa-btn spa-btn-primary" href="#/login">Log in to favorite</a>`;
      return;
    }
    const singular = kind === 'movies' ? 'movie' : kind === 'series' ? 'series' : 'animation';
    const favRes = await api('/favorites/');
    let favoriteId = null;
    if (favRes.ok) {
      const favData = await favRes.json();
      const list = favData.results || favData;
      const match = list.find((f) => f[singular] === Number(id) || f[singular]?.id === Number(id));
      favoriteId = match?.id || null;
    }
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'spa-btn spa-btn-primary';
    btn.textContent = favoriteId ? 'Remove favorite' : 'Add favorite';
    btn.onclick = async () => {
      btn.disabled = true;
      try {
        if (favoriteId) {
          const del = await api(`/favorites/${favoriteId}/`, { method: 'DELETE' });
          if (!del.ok && del.status !== 204) throw new Error('remove failed');
          favoriteId = null;
          btn.textContent = 'Add favorite';
          toast('Removed from favorites');
        } else {
          const body = {};
          body[singular] = Number(id);
          const add = await api('/favorites/', { method: 'POST', body: JSON.stringify(body) });
          if (!add.ok) throw new Error('add failed');
          const created = await add.json();
          favoriteId = created.id;
          btn.textContent = 'Remove favorite';
          toast('Added to favorites');
        }
      } catch {
        toast('Favorite action failed');
      } finally {
        btn.disabled = false;
      }
    };
    actions.appendChild(btn);
  }

  async function renderSearch() {
    setActiveNav('search');
    main.innerHTML = `
      <div class="spa-hero"><h1>Search</h1><p>Calls <code>/api/v1/search/?q=</code>.</p></div>
      <form class="spa-toolbar" id="spa-search-form">
        <input id="spa-q" name="q" type="search" placeholder="Title or keyword" required>
        <button class="spa-btn spa-btn-primary" type="submit">Search</button>
      </form>
      <div id="spa-search-results"></div>`;
    document.getElementById('spa-search-form').onsubmit = async (e) => {
      e.preventDefault();
      const q = document.getElementById('spa-q').value.trim();
      const box = document.getElementById('spa-search-results');
      box.innerHTML = `<p class="spa-loading">Searching…</p>`;
      const res = await api(`/search/?q=${encodeURIComponent(q)}`);
      if (!res.ok) {
        box.innerHTML = `<p class="spa-error">Search failed (${res.status}).</p>`;
        return;
      }
      const results = await res.json();
      if (!results.length) {
        box.innerHTML = `<p class="spa-empty">No results for “${escapeHtml(q)}”.</p>`;
        return;
      }
      box.innerHTML = `<div class="spa-grid">${results
        .map((item) => {
          const kind =
            item.type === 'movie' ? 'movies' : item.type === 'series' ? 'series' : 'animations';
          return cardHtml(
            {
              id: item.id,
              title: item.title,
              poster: item.poster,
              overall_rating: item.overall_rating,
            },
            kind
          );
        })
        .join('')}</div>`;
    };
  }

  async function renderRecommended() {
    setActiveNav('recommended');
    main.innerHTML = `<div class="spa-hero"><h1>Recommended</h1><p>From <code>/api/v1/recommendations/</code>${state.user ? '' : ' (anonymous baseline — log in for personalization).'}.</p></div><p class="spa-loading">Loading…</p>`;
    const res = await api('/recommendations/?limit=12');
    if (!res.ok) {
      main.innerHTML = `<p class="spa-error">Could not load recommendations (${res.status}).</p>`;
      return;
    }
    const movies = await res.json();
    main.innerHTML = `
      <div class="spa-hero"><h1>Recommended</h1><p>From <code>/api/v1/recommendations/</code>.</p></div>
      ${
        movies.length
          ? `<div class="spa-grid">${movies.map((m) => cardHtml(m, 'movies')).join('')}</div>`
          : `<p class="spa-empty">No recommendations yet.</p>`
      }`;
  }

  async function renderHome() {
    setActiveNav('');
    main.innerHTML = `
      <div class="spa-hero">
        <h1>API browse client</h1>
        <p>Lightweight JWT demo for the resume: catalog, search, recommendations, and favorites against the same DRF backend. The main product remains server-rendered Django templates.</p>
      </div>
      <div class="spa-actions">
        <a class="spa-btn spa-btn-primary" href="#/movies">Browse movies</a>
        <a class="spa-btn" href="#/login">JWT login</a>
        <a class="spa-btn" href="${escapeHtml(cfg.siteHome || '/')}">Full SSR site</a>
      </div>`;
  }

  function parseHash() {
    const raw = (location.hash || '#/').replace(/^#/, '') || '/';
    const parts = raw.split('/').filter(Boolean);
    return parts;
  }

  async function route() {
    renderAuth();
    const parts = parseHash();
    const [a, b, c] = parts;
    if (!a) return renderHome();
    if (a === 'login') return renderLogin();
    if (a === 'search') return renderSearch();
    if (a === 'recommended') return renderRecommended();
    if (['movies', 'series', 'animations'].includes(a) && b && /^\d+$/.test(b)) {
      return renderDetail(a, b);
    }
    if (['movies', 'series', 'animations'].includes(a)) {
      return renderList(a, 1);
    }
    main.innerHTML = `<p class="spa-error">Unknown route.</p>`;
  }

  async function boot() {
    await ensureUser();
    await route();
  }

  window.addEventListener('hashchange', () => {
    route();
  });

  boot();
})();
