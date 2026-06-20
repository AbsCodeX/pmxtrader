const API = (location.protocol.startsWith('http') && location.port)
      ? `${location.protocol}//${location.host}`
      : 'http://127.0.0.1:8765';
    const isFileProtocol = location.protocol === 'file:';
    const DOCS_SITE = 'https://abscodex.github.io/pmxtrader';

    /** One-click action strip — runs safe commands directly (no duplicate card grid). */
    const ACTION_STRIP = [
      { run: 'status', label: 'Status', icon: '●' },
      { run: 'warm', label: 'Warm', icon: '↻' },
      { run: 'balance', label: 'Kalshi $', icon: 'K' },
      { run: 'poly-balance', label: 'Poly $', icon: 'P' },
      { run: 'positions', label: 'Kalshi pos', icon: '◫' },
      { run: 'poly-positions', label: 'Poly pos', icon: '◧' },
      { run: 'preflight', label: 'Preflight', icon: '✓' },
      { run: 'panic-dry-run', label: 'Panic dry', icon: '⚠' },
      { action: 'analyze', label: 'Analyze', icon: '🔍' },
      { action: 'dashboard', label: 'Reload API', icon: '⎋' },
    ];

    /** Legacy reference — tab panels only (quick blocks removed to reduce bulk). */
    const QUICK_BLOCKS = [];

    const REF_DOCS = [
      { icon: '📋', title: 'Command reference', href: `${DOCS_SITE}/commands/`, desc: 'Full ./pmx command list' },
      { icon: '🔐', title: 'Environment & safety', href: `${DOCS_SITE}/environment/`, desc: 'Env vars, read-only, caps' },
      { icon: '⚠️', title: 'Known risks', href: `${DOCS_SITE}/known-risks/`, desc: 'Real money, agents, surfaces' },
      { icon: '🧪', title: 'Testing & CI', href: `${DOCS_SITE}/testing/`, desc: 'pytest, ruff, smoke scripts' },
      { icon: '🏗', title: 'Architecture', href: `${DOCS_SITE}/architecture/`, desc: 'Bridge, sidecar, agents' },
      { icon: '📱', title: 'Telegram + Hermes', href: `${DOCS_SITE}/telegram-integration/`, desc: 'Mobile control setup' },
    ];

    const SECTIONS = [
      { id: 'start', label: '🚀 Start', lead: 'Session bootstrap, warm sidecar, dashboard server.', cmds: [
        { c: 'pmxt-terminal', d: 'Open new macOS Terminal + session (after setup-direnv)' },
        { c: 'pmxt-start', d: 'Bootstrap sidecar + status in current shell' },
        { c: './pmx session', d: 'Same as pmxt-start' },
        { c: './pmx dashboard', d: 'Open this page with live API + link analyzer' },
        { c: './scripts/setup-direnv.sh', d: 'One-time: direnv + pmxt-terminal in ~/.zshrc' },
        { c: './pmx warm', d: 'Warm PMXT sidecar after .env change', run: 'warm' },
        { c: './scripts/pmxt-server.sh restart', d: 'Restart sidecar with pmxt/.env' },
        { c: './scripts/pmxt-server.sh stop', d: 'Stop sidecar process' },
      ]},
      { id: 'control', label: '⏸ Pause / live', lead: 'Go-live, pause, resume — Terminal only (blocked here).', cmds: [
        { c: './pmx go-live', d: 'Clear read-only + disengage kill switch', tag: 'terminal' },
        { c: './pmx resume', d: 'Same as go-live', tag: 'terminal' },
        { c: './pmx activate-live', d: 'Warm + go-live + preflight', tag: 'terminal' },
        { c: './pmx preflight', d: 'GO / NO-GO checklist before live orders', run: 'preflight' },
        { c: './pmx stop on "reason"', d: 'Kill switch ON — block new trades', tag: 'terminal' },
        { c: './pmx stop', d: 'Halt with default reason', tag: 'terminal' },
        { c: './pmx stop orders', d: 'Halt + cancel resting orders', tag: 'terminal' },
      ]},
      { id: 'portfolio', label: '💰 Portfolio', lead: 'Balances and open positions — safe to run live from this page.', cmds: [
        { c: './pmx status', d: 'Kill switch + balances summary', run: 'status' },
        { c: './pmx balance', d: 'Kalshi available cash', run: 'balance' },
        { c: './pmx positions', d: 'Kalshi open holdings', run: 'positions' },
        { c: './pmx poly balance', d: 'Polymarket US cash', run: 'poly-balance' },
        { c: './pmx poly positions', d: 'Poly US holdings', run: 'poly-positions' },
        { c: './pmx poly orders', d: 'Open Poly resting orders', run: 'poly-orders' },
      ]},
      { id: 'analyze', label: '🔍 Analyze', lead: 'Read-only quotes and cross-venue research.', cmds: [
        { c: "./pmx link 'KALSHI_URL' USA 1", d: 'Kalshi URL → event resolve + quote + fill estimate' },
        { c: "./pmx poly link 'https://polymarket.us/market/SLUG' long", d: 'Poly US URL → slug + orderbook quote' },
        { c: './pmx compare url URL', d: 'Cross-venue odds (Scout)' },
        { c: './pmx scout grok', d: 'Deep research after link snapshot' },
        { c: './pmx preview trade MARKET OUT 1', d: 'Dry-run Kalshi order (no send)' },
        { c: './pmx preview poly trade SLUG long 1', d: 'Dry-run Poly order (no send)' },
      ]},
      { id: 'kalshi', label: '📈 Kalshi', lead: 'Kalshi quotes, watch, and live trade commands.', cmds: [
        { c: './pmx balance', d: 'Available cash', run: 'balance' },
        { c: './pmx positions', d: 'Open holdings', run: 'positions' },
        { c: "./pmx link 'KALSHI_URL' USA 1", d: 'URL → full eval snapshot' },
        { c: './pmx quote EVENT OUTCOME 1', d: 'Price + book + fill estimate' },
        { c: './pmx event EVENT', d: 'Raw event JSON' },
        { c: './pmx trade MARKET OUTCOME 1', d: 'Market buy — Terminal only, kill switch OFF', tag: 'trade' },
        { c: './pmx watch OUTCOME_ID', d: 'Stream orderbook' },
        { c: './pmx compare url URL', d: 'Cross-venue odds (Scout)' },
      ]},
      { id: 'poly', label: '🎯 Poly US', lead: 'Polymarket US retail commands.', cmds: [
        { c: './pmx poly balance', d: 'US cash', run: 'poly-balance' },
        { c: './pmx poly positions', d: 'Holdings', run: 'poly-positions' },
        { c: './pmx poly quote SLUG long', d: 'Market + orderbook' },
        { c: "./pmx poly link 'https://polymarket.us/market/SLUG' long", d: 'Quote from URL' },
        { c: './pmx poly trade SLUG long 1', d: 'Market buy — Terminal only', tag: 'trade' },
        { c: './pmx poly sell SLUG long 100', d: 'Market sell — Terminal only', tag: 'trade' },
        { c: './pmx poly close SLUG long', d: 'Flatten position — Terminal only', tag: 'trade' },
        { c: './pmx poly watch book SLUG long --max-messages 10', d: 'Live book (active markets)' },
        { c: './pmx poly history --limit 20', d: 'Your fill history' },
        { c: './pmx poly orders', d: 'Open orders', run: 'poly-orders' },
        { c: './pmx poly cancel-all', d: 'Cancel all resting orders', tag: 'terminal' },
      ]},
      { id: 'agents', label: '🤖 Agents', lead: 'Scout / Trader lanes and Hermes bundles.', cmds: [
        { c: './pmx scout grok', d: 'Scout — fast research (Hermes/xAI)' },
        { c: './pmx scout claude', d: 'Scout — deep research' },
        { c: './pmx trader openai briefs/active/BRIEF.md', d: 'Trader — approved brief only' },
        { c: './scripts/setup-hermes.sh', d: 'Sync LLM keys + Hermes skills/bundles' },
        { c: './pmx hermes-telegram', d: 'Wire pmxtrader into Hermes Telegram profile' },
        { c: './scripts/check-providers.sh', d: 'Verify API keys', run: 'providers' },
        { c: 'hermes chat --cli -t no_mcp → /pmxtrader', d: 'Hermes auto Scout/Trader bundle' },
      ]},
      { id: 'safety', label: '🛡 Safety', lead: 'Kill switch, panic flatten, emergency stops — Terminal only.', cmds: [
        { c: './pmx status', d: 'Kill switch + balances', run: 'status' },
        { c: './pmx stop on "reason"', d: 'Block new trades (kill switch ON)', tag: 'terminal' },
        { c: './pmx resume', d: 'Allow trading again (go-live)', tag: 'terminal' },
        { c: './pmx stop orders', d: 'Halt + cancel resting orders', tag: 'terminal' },
        { c: './pmx panic', d: 'Emergency flatten — type PANIC in Terminal', tag: 'trade' },
        { c: './pmx panic --dry-run', d: 'Preview panic scope (Kalshi + Poly US)', run: 'panic-dry-run' },
        { c: './pmx panic status', d: 'Show venues included in panic flatten' },
      ]},
      { id: 'docs', label: '📚 Docs', lead: 'Published guides on GitHub Pages — open in new tab.', cmds: [
        { c: `${DOCS_SITE}/commands/`, d: 'Master command reference', link: true },
        { c: `${DOCS_SITE}/environment/`, d: 'Environment variables & safety defaults', link: true },
        { c: `${DOCS_SITE}/known-risks/`, d: 'Real money, agents, execution surfaces', link: true },
        { c: `${DOCS_SITE}/testing/`, d: 'pytest, CI, smoke scripts', link: true },
        { c: `${DOCS_SITE}/architecture/`, d: 'System architecture overview', link: true },
        { c: `${DOCS_SITE}/telegram-integration/`, d: 'Hermes Telegram + mobile UI', link: true },
        { c: `${DOCS_SITE}/multi-agent/`, d: 'Scout / Trader workflow', link: true },
        { c: 'docs/polymarket-us-integration.md', d: 'Poly US keys + MCP (repo path)' },
        { c: 'docs/kalshi-integration.md', d: 'Kalshi ↔ scripts (repo path)' },
      ]},
    ];

    const tabsEl = document.getElementById('tabs');
    const panelsEl = document.getElementById('panels');
    const termOut = document.getElementById('term-out');
    const termIn = document.getElementById('term-in');
    const connBadge = document.getElementById('conn-badge');
    const statusBar = document.getElementById('status-bar');
    const themeToggle = document.getElementById('theme-toggle');
    let live = false;
    let apiToken = typeof window.__PMXT_DASHBOARD_TOKEN__ === 'string' ? window.__PMXT_DASHBOARD_TOKEN__ : '';
    let activeTab = SECTIONS[0].id;
    let lastAnalyzeCmd = '';

    // Theme: default light (user preference), persist toggle
    (function initTheme() {
      const saved = localStorage.getItem('pmxt-theme');
      const theme = saved === 'light' ? 'light' : 'dark';
      document.documentElement.dataset.theme = theme;
      themeToggle.textContent = theme === 'dark' ? 'Light' : 'Dark';
    })();

    themeToggle.onclick = () => {
      const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
      document.documentElement.dataset.theme = next;
      localStorage.setItem('pmxt-theme', next);
      themeToggle.textContent = next === 'dark' ? 'Light' : 'Dark';
    };

    function appendOut(text) {
      termOut.textContent += text;
      termOut.scrollTop = termOut.scrollHeight;
    }

    function renderActionStrip() {
      const el = document.getElementById('action-strip');
      if (!el) return;
      el.innerHTML = `
        <div class="action-strip">${ACTION_STRIP.map(item => {
          if (item.action === 'analyze') {
            return `<button type="button" class="strip-btn" id="btn-goto-analyze"><span class="strip-icon">${item.icon}</span>${item.label}</button>`;
          }
          if (item.action === 'dashboard') {
            return `<button type="button" class="strip-btn strip-btn--muted" id="btn-strip-reload"><span class="strip-icon">${item.icon}</span>${item.label}</button>`;
          }
          return `<button type="button" class="strip-btn strip-btn--run" data-run="${item.run}"><span class="strip-icon">${item.icon}</span>${item.label}</button>`;
        }).join('')}</div>`;
      const reloadBtn = document.getElementById('btn-strip-reload');
      if (reloadBtn) {
        reloadBtn.onclick = () => {
          checkLive();
          refreshStatusBar();
          if (!live && !location.protocol.startsWith('http')) {
            window.open('http://127.0.0.1:8765/', '_blank');
          } else if (!live) {
            window.location.reload();
          }
        };
      }
    }

    function renderQuickBlocks() {
      renderActionStrip();
    }

    function renderRefDocs() {
      const el = document.getElementById('doc-ref');
      if (!el) return;
      el.innerHTML = `
        <div class="ref-grid">${REF_DOCS.map(doc => `
          <a class="ref-card" href="${doc.href}" target="_blank" rel="noopener">
            <span class="ref-card__icon">${doc.icon}</span>
            <span class="ref-card__title">${doc.title}</span>
            <span class="ref-card__desc">${doc.desc}</span>
          </a>`).join('')}
        </div>`;
    }

    function renderPanels(filter = '') {
      const q = filter.toLowerCase();
      panelsEl.innerHTML = SECTIONS.map(sec => {
        const cmds = sec.cmds.filter(x =>
          !q || x.c.toLowerCase().includes(q) || (x.d||'').toLowerCase().includes(q)
        );
        if (!cmds.length && q) return '';
        const isActive = sec.id === activeTab;
        return `<div class="panel ${isActive?'active':''}" data-panel="${sec.id}">
          ${sec.lead ? `<p class="panel-lead">${sec.lead}</p>` : ''}
          <div class="cmd-list">${cmds.map(x => {
            const tag = x.tag || '';
            const copyLabel = tag === 'trade' || tag === 'terminal' ? 'Terminal' : 'Copy';
            const linkBtn = x.link ? `<a class="btn-link" href="${x.c}" target="_blank" rel="noopener">Open ↗</a>` : '';
            return `
            <div class="cmd">
              <div>
                ${tag ? `<div class="tag tag--${tag}">${tag}</div>` : ''}
                <code>${x.c}</code>
                <small>${x.d||''}</small>
              </div>
              <div class="btn-row">
                ${x.link ? linkBtn : `<button data-copy="${x.c.replace(/"/g,'&quot;')}">${copyLabel}</button>`}
                ${x.run ? `<button class="primary" data-run="${x.run}">Run</button>` : ''}
              </div>
            </div>`;
          }).join('')}</div>
        </div>`;
      }).join('');
      if (!document.querySelector('.panel.active')) {
        const first = document.querySelector('.panel');
        if (first) {
          activeTab = first.dataset.panel;
          first.classList.add('active');
          document.querySelectorAll('.tab').forEach(t => {
            t.classList.toggle('active', t.dataset.tab === activeTab);
          });
        }
      }
    }

    function renderTabs() {
      tabsEl.innerHTML = SECTIONS.map(sec =>
        `<button class="tab ${sec.id===activeTab?'active':''}" data-tab="${sec.id}">${sec.label}</button>`
      ).join('');
    }

    renderQuickBlocks();
    renderRefDocs();
    renderTabs();
    renderPanels();

    tabsEl.addEventListener('click', e => {
      const btn = e.target.closest('.tab');
      if (!btn) return;
      activeTab = btn.dataset.tab;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.querySelector(`[data-panel="${activeTab}"]`)?.classList.add('active');
    });

    document.getElementById('search').addEventListener('input', e => renderPanels(e.target.value));

    async function copyText(text) {
      try { await navigator.clipboard.writeText(text); return true; }
      catch { return false; }
    }

    document.body.addEventListener('click', async e => {
      if (e.target.closest('#btn-goto-analyze')) {
        document.getElementById('link-analyzer')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        document.getElementById('link-url')?.focus();
        return;
      }
      const copyBtn = e.target.closest('[data-copy]');
      if (copyBtn) {
        await copyText(copyBtn.getAttribute('data-copy'));
        const old = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        setTimeout(() => copyBtn.textContent = old, 900);
        return;
      }
      const runBtn = e.target.closest('[data-run]');
      if (runBtn) runCommand(runBtn.getAttribute('data-run'));
    });

    function parseStatusSummary(stdout) {
      if (!stdout) return '';
      let kill = '?';
      if (/^ENGAGED\b/m.test(stdout)) kill = 'ON';
      else if (/^OFF\b/m.test(stdout)) kill = 'OFF';
      else kill = stdout.match(/^(ON|OFF)\b/m)?.[1] || '?';
      const kalshi = stdout.match(/^Kalshi:\s*\n\s*available:\s*([\d.]+)/m)?.[1];
      const poly = stdout.match(/^Polymarket US:\s*\n\s*available:\s*([\d.]+)/m)?.[1];
      const killStyle = kill === 'ON' ? 'color:var(--danger)' : kill === 'OFF' ? '' : 'color:var(--warn)';
      let parts = [`Kill switch: <strong style="${killStyle}">${kill}</strong>`];
      if (kalshi) parts.push(`Kalshi $${kalshi}`);
      if (poly) parts.push(`Poly $${poly}`);
      return parts.join(' · ');
    }

    function renderSafetyBadges(data) {
      if (!data || !data.ok) return '';
      const chips = [];
      const ks = data.killSwitch || '?';
      chips.push(`<span class="safety-chip ${ks === 'ON' ? 'danger' : 'ok'}">KILL ${ks}</span>`);
      const ro = data.readOnly ? 'ON' : 'OFF';
      chips.push(`<span class="safety-chip ${data.readOnly ? 'warn' : 'ok'}">READ-ONLY ${ro}</span>`);
      if (data.maxTradeContracts != null) {
        chips.push(`<span class="safety-chip neutral">MAX ${data.maxTradeContracts}</span>`);
      }
      return chips.join(' ');
    }

    function mergeStatusBar(statusStdout, safety) {
      const base = parseStatusSummary(statusStdout);
      const badges = renderSafetyBadges(safety);
      if (!badges) return base;
      return `${badges}${base ? ' · ' + base : ''}`;
    }

    function apiHeaders() {
      const h = { 'Content-Type': 'application/json' };
      if (apiToken) h['X-Pmxtrader-Token'] = apiToken;
      return h;
    }

    function friendlyApiError(status, data) {
      if (status === 403) {
        return 'Session token invalid — reload this page via ./pmx dashboard (do not open file://).';
      }
      if (status === 400 && data?.error) {
        return data.error + (data.hint ? `\nHint: ${data.hint}` : '');
      }
      if (status >= 500) return 'Dashboard server error — check Terminal where ./pmx dashboard is running.';
      if (data?.error) return data.error;
      return `Request failed (HTTP ${status})`;
    }

    async function postJson(path, payload) {
      const r = await fetch(`${API}${path}`, {
        method: 'POST',
        headers: apiHeaders(),
        body: JSON.stringify(payload),
      });
      let data = {};
      try { data = await r.json(); } catch { /* non-JSON */ }
      if (!r.ok) {
        const msg = friendlyApiError(r.status, data);
        return { ok: false, error: msg, status: r.status, ...data };
      }
      return data;
    }

    async function refreshStatusBar() {
      if (!live) {
        statusBar.classList.remove('visible');
        return;
      }
      try {
        const [statusData, safetyData] = await Promise.all([
          postJson('/api/run', { command: 'status' }),
          fetch(`${API}/api/safety`, { headers: apiHeaders() }).then(async r => {
            try { return await r.json(); } catch { return {}; }
          }),
        ]);
        if (statusData.stdout || safetyData.ok) {
          statusBar.innerHTML = mergeStatusBar(statusData.stdout, safetyData);
          statusBar.classList.add('visible');
        } else if (statusData.error) {
          statusBar.textContent = statusData.error;
          statusBar.classList.add('visible');
        }
      } catch {
        statusBar.classList.remove('visible');
      }
    }

    function updateOfflineNote() {
      const note = document.getElementById('offline-note');
      const detail = document.getElementById('offline-detail');
      if (live) {
        note.style.display = 'none';
        return;
      }
      note.style.display = 'block';
      if (isFileProtocol) {
        detail.textContent = 'Opened as a local file — browsers block live API calls. Use ';
      } else {
        detail.textContent = 'Start the dashboard server for live commands and link analysis: ';
      }
    }

    async function checkLive() {
      try {
        const r = await fetch(`${API}/api/health`, { signal: AbortSignal.timeout(800) });
        const wasLive = live;
        live = r.ok;
        if (live && !wasLive) refreshStatusBar();
        if (!live) statusBar.classList.remove('visible');
      } catch {
        live = false;
        statusBar.classList.remove('visible');
      }
      connBadge.className = 'badge ' + (live ? 'live' : 'offline');
      connBadge.innerHTML = `<span class="dot"></span> ${live ? 'live API' : 'offline'}`;
      updateOfflineNote();
      const btnDash = document.getElementById('btn-dashboard');
      if (location.protocol.startsWith('http')) {
        btnDash.textContent = live ? 'Connected' : 'Retry connection';
      }
    }

    async function runCommand(cmd) {
      appendOut(`\n$ ${cmd}\n`);
      if (!live) {
        appendOut('[offline] Run: ./pmx dashboard\n');
        return;
      }
      try {
        const data = await postJson('/api/run', { command: cmd });
        if (data.command) appendOut(`→ ${data.command}\n`);
        if (data.stdout) appendOut(data.stdout + (data.stdout.endsWith('\n') ? '' : '\n'));
        if (data.stderr) appendOut(data.stderr);
        if (data.error) appendOut(`ERROR: ${data.error}\n`);
        if (!data.ok && !data.error && !data.stdout) appendOut(`exit ${data.exitCode}\n`);
        if (cmd === 'status' && data.stdout) {
          fetch(`${API}/api/safety`, { headers: apiHeaders() })
            .then(r => r.json())
            .then(safety => {
              statusBar.innerHTML = mergeStatusBar(data.stdout, safety);
              statusBar.classList.add('visible');
            })
            .catch(() => {
              statusBar.innerHTML = parseStatusSummary(data.stdout);
              statusBar.classList.add('visible');
            });
        }
      } catch (err) {
        appendOut(`ERROR: ${err.message}\n`);
      }
    }

    termIn.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        const v = termIn.value.trim();
        if (v) {
          if (v.startsWith('http://') || v.startsWith('https://')) {
            linkUrl.value = v;
            updateVenueUI();
            document.getElementById('link-analyzer').scrollIntoView({ behavior: 'smooth', block: 'start' });
            analyzeLink();
          } else {
            runCommand(v);
          }
        }
        termIn.value = '';
      }
    });

    document.getElementById('term-clear').onclick = () => {
      termOut.textContent = 'Terminal cleared.\n';
    };

    document.getElementById('btn-dashboard').onclick = () => {
      if (location.protocol.startsWith('http')) {
        checkLive();
        if (!live) window.location.reload();
        return;
      }
      window.open('http://127.0.0.1:8765/', '_blank');
    };

    const linkUrl = document.getElementById('link-url');
    const linkOutcome = document.getElementById('link-outcome');
    const linkSide = document.getElementById('link-side');
    const linkSize = document.getElementById('link-size');
    const analyzeOut = document.getElementById('analyze-out');
    const analyzePreview = document.getElementById('analyze-preview');
    const analyzePreviewBody = document.getElementById('analyze-preview-body');
    const venueTag = document.getElementById('venue-tag');
    const fieldOutcome = document.getElementById('field-outcome');
    const fieldSide = document.getElementById('field-side');
    const btnAnalyze = document.getElementById('btn-analyze');
    const btnAnalyzeCopy = document.getElementById('btn-analyze-copy');

    function detectVenue(url) {
      const u = url.toLowerCase();
      if (u.includes('kalshi')) return 'kalshi';
      if (u.includes('polymarket')) return 'poly';
      return null;
    }

    function updateVenueUI() {
      const v = detectVenue(linkUrl.value.trim());
      venueTag.className = 'venue-tag' + (v ? ' ' + v : '');
      if (v === 'kalshi') {
        venueTag.textContent = 'Kalshi';
        fieldOutcome.style.display = '';
        fieldSide.style.display = 'none';
        linkSize.parentElement.style.display = '';
      } else if (v === 'poly') {
        venueTag.textContent = 'Poly US';
        fieldOutcome.style.display = 'none';
        fieldSide.style.display = '';
        linkSize.parentElement.style.display = 'none';
      } else {
        venueTag.textContent = 'paste URL';
        fieldOutcome.style.display = '';
        fieldSide.style.display = 'none';
        linkSize.parentElement.style.display = '';
      }
    }

    function buildAnalyzeCmd() {
      const url = linkUrl.value.trim();
      if (!url) return '';
      const v = detectVenue(url);
      const q = url.includes("'") ? `"${url}"` : `'${url}'`;
      if (v === 'poly') return `./pmx poly link ${q} ${linkSide.value}`;
      const out = linkOutcome.value.trim() || 'USA';
      return `./pmx link ${q} ${out} ${linkSize.value || '1'}`;
    }

    function setAnalyzeOutput(text, opts = {}) {
      analyzeOut.textContent = text;
      analyzeOut.classList.toggle('empty', !!opts.empty);
      analyzeOut.classList.toggle('error', !!opts.error);
    }

    function setAnalyzePreview(text) {
      if (!text || !text.trim()) {
        analyzePreview.classList.add('hidden');
        analyzePreviewBody.textContent = '';
        return;
      }
      analyzePreviewBody.textContent = text.trim();
      analyzePreview.classList.remove('hidden');
    }

    async function analyzeLink() {
      const url = linkUrl.value.trim();
      if (!url) {
        setAnalyzeOutput('Paste a Kalshi or Polymarket US URL first.', { empty: true });
        return;
      }
      lastAnalyzeCmd = buildAnalyzeCmd();
      btnAnalyzeCopy.disabled = !lastAnalyzeCmd;
      setAnalyzePreview('');
      setAnalyzeOutput('Analyzing… (may take up to ~30s while sidecar fetches data)', {});
      btnAnalyze.disabled = true;

      if (!live) {
        setAnalyzeOutput(
          `[offline] Start dashboard first:\n  ./pmx dashboard\n\nOr copy to Terminal:\n  ${lastAnalyzeCmd}`,
          { error: true }
        );
        btnAnalyze.disabled = false;
        return;
      }

      try {
        const payload = {
          url,
          outcome: linkOutcome.value.trim() || 'USA',
          side: linkSide.value,
          size: linkSize.value || 1,
        };
        const data = await postJson('/api/analyze', payload);
        let text = '';
        if (data.venue) text += `[${data.venue === 'kalshi' ? 'Kalshi' : 'Poly US'}] ${data.url || url}\n\n`;
        if (data.command) text += `$ ${data.command}\n\n`;
        if (data.preview) setAnalyzePreview(data.preview);
        else if (data.stdout) setAnalyzePreview(data.stdout.split('\n').slice(0, 6).join('\n'));
        if (data.stdout) text += data.stdout;
        if (data.stderr) text += (text && !text.endsWith('\n') ? '\n' : '') + data.stderr;
        if (data.error) text += `\nERROR: ${data.error}\n`;
        if (!text.trim()) text = `No output (exit ${data.exitCode ?? '?'})\n`;
        if (lastAnalyzeCmd) text += `\n---\nTerminal cmd:\n  ${lastAnalyzeCmd}\n`;
        setAnalyzeOutput(text, { error: !data.ok });
        appendOut(`\n[analyze] ${url}\n${(data.stdout || data.error || '').slice(0, 600)}\n`);
      } catch (err) {
        setAnalyzePreview('');
        setAnalyzeOutput(`ERROR: ${err.message}`, { error: true });
      } finally {
        btnAnalyze.disabled = false;
      }
    }

    document.getElementById('btn-paste-url').onclick = async () => {
      try {
        const t = await navigator.clipboard.readText();
        if (t) {
          linkUrl.value = t.trim();
          updateVenueUI();
          linkUrl.focus();
        }
      } catch {
        linkUrl.focus();
      }
    };

    linkUrl.addEventListener('input', updateVenueUI);
    linkUrl.addEventListener('keydown', e => { if (e.key === 'Enter') analyzeLink(); });
    btnAnalyze.onclick = analyzeLink;
    btnAnalyzeCopy.onclick = async () => {
      if (!lastAnalyzeCmd) return;
      await copyText(lastAnalyzeCmd);
      btnAnalyzeCopy.textContent = 'Copied!';
      setTimeout(() => { btnAnalyzeCopy.textContent = 'Copy cmd'; }, 900);
    };
    document.getElementById('btn-analyze-clear').onclick = () => {
      linkUrl.value = '';
      setAnalyzePreview('');
      setAnalyzeOutput('Paste a link and click Analyze. Requires live dashboard server (./pmx dashboard) and warmed sidecar.', { empty: true });
      lastAnalyzeCmd = '';
      btnAnalyzeCopy.disabled = true;
      updateVenueUI();
    };
    updateVenueUI();

    checkLive();
    setInterval(checkLive, 8000);
