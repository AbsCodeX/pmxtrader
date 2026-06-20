---
hide:
  - toc
  - navigation
---

<section class="pmx-hero" aria-labelledby="hero-title">
  <div class="pmx-hero__inner">
    <p class="pmx-eyebrow">pmxtrader · GitHub documentation</p>
    <h1 id="hero-title">Documentation built for clear project review.</h1>
    <p class="pmx-lead">
      Human-gated prediction market operations for <strong>Kalshi</strong> and <strong>Polymarket US</strong>.
      One place to understand the project, install it, run it safely, test it, and review QA.
    </p>
    <div class="pmx-hero__actions">
      <a class="pmx-btn pmx-btn--dark" href="https://github.com/AbsCodeX/pmxtrader" target="_blank" rel="noopener">View on GitHub</a>
      <a class="pmx-btn pmx-btn--ghost" href="#setup">Get Started</a>
    </div>
    <ul class="pmx-badges" aria-label="Project status">
      <li><span class="pmx-badge">Build passing</span></li>
      <li><span class="pmx-badge">Tests ready</span></li>
      <li><span class="pmx-badge">Docs complete</span></li>
      <li><span class="pmx-badge">QA reviewed</span></li>
    </ul>
  </div>
</section>

<section class="pmx-section" id="overview" aria-labelledby="overview-title">
  <div class="pmx-section__inner">
    <h2 id="overview-title">Overview</h2>
    <p class="pmx-section__lead">
      pmxtrader is a terminal-first toolkit for researching and executing prediction market trades with layered safety defaults.
    </p>
    <div class="pmx-panel">
      <div class="pmx-panel__row">
        <h3>Who it is for</h3>
        <p>Developers and operators who want Kalshi or Polymarket US access through a single CLI, optional agents, and explicit human confirmation before live orders.</p>
      </div>
      <div class="pmx-panel__row">
        <h3>What problem it solves</h3>
        <p>Trading venues have different APIs, credentials, and foot-guns. pmxtrader wraps PMXT with read-only defaults, preflight checks, preview commands, and a clear Scout → approve → Trader workflow.</p>
      </div>
      <div class="pmx-panel__row pmx-panel__row--last">
        <h3>What you get</h3>
        <p><code>./pmx</code> commands, a read-only web dashboard, Cockpit TUI, multi-agent briefs, and published docs on GitHub Pages.</p>
      </div>
    </div>
  </div>
</section>

<section class="pmx-section pmx-section--surface" id="features" aria-labelledby="features-title">
  <div class="pmx-section__inner">
    <h2 id="features-title">Features</h2>
    <p class="pmx-section__lead">Core capabilities at a glance.</p>
    <div class="pmx-feature-grid">
      <article class="pmx-feature">
        <h3>Terminal CLI</h3>
        <p>Plain-language <code>./pmx</code> commands for session setup, quotes, previews, and live trades after go-live.</p>
      </article>
      <article class="pmx-feature">
        <h3>Safety defaults</h3>
        <p>Sessions start read-only. Preflight, kill switch, contract caps, and YES prompts gate real-money orders.</p>
      </article>
      <article class="pmx-feature">
        <h3>Kalshi &amp; Polymarket US</h3>
        <p>Venue adapters via vendored PMXT with dedicated quickstarts and credential docs.</p>
      </article>
      <article class="pmx-feature">
        <h3>Scout / Trader agents</h3>
        <p>Separate research from execution. Briefs require human <code>approved: true</code> before trade prep.</p>
      </article>
      <article class="pmx-feature">
        <h3>Dashboard &amp; Cockpit</h3>
        <p>Web dashboard for analysis only; Cockpit TUI for live tiles with a confirm modal on trades.</p>
      </article>
      <article class="pmx-feature">
        <h3>CI &amp; docs</h3>
        <p>Python tests, ruff, mypy, markdown lint, link checks, and MkDocs published on every push to <code>main</code>.</p>
      </article>
    </div>
  </div>
</section>

<section class="pmx-section" id="setup" aria-labelledby="setup-title">
  <div class="pmx-section__inner">
    <h2 id="setup-title">Setup</h2>
    <p class="pmx-section__lead">Run these commands from your machine after cloning the repository.</p>

    <ol class="pmx-steps">
      <li class="pmx-step">
        <div class="pmx-step__body">
          <h3>Clone the repository</h3>
          <pre><code class="language-bash">git clone https://github.com/AbsCodeX/pmxtrader.git
cd pmxtrader
git submodule update --init   # optional: pmxt-mcp, molt-pmxt</code></pre>
        </div>
      </li>
      <li class="pmx-step">
        <div class="pmx-step__body">
          <h3>Install dependencies</h3>
          <pre><code class="language-bash">./scripts/setup-dev.sh
pip install -r requirements-docs.txt   # optional: docs preview</code></pre>
        </div>
      </li>
      <li class="pmx-step">
        <div class="pmx-step__body">
          <h3>Create environment file</h3>
          <pre><code class="language-bash">cp pmxt/.env.example pmxt/.env
# Add venue keys (Kalshi / Polymarket US) and optional LLM keys</code></pre>
          <p class="pmx-muted">See <a href="environment.md">Environment &amp; safety</a> for every variable.</p>
        </div>
      </li>
      <li class="pmx-step">
        <div class="pmx-step__body">
          <h3>Start a session</h3>
          <pre><code class="language-bash">source scripts/pmxt-env.sh
./pmx session
./pmx preflight</code></pre>
          <p class="pmx-muted">Expect <strong>NO-GO</strong> while read-only — that is the safe default.</p>
        </div>
      </li>
      <li class="pmx-step">
        <div class="pmx-step__body">
          <h3>Run tests</h3>
          <pre><code class="language-bash">python3 -m pytest tests/ -q
./scripts/smoke-functionality.sh</code></pre>
        </div>
      </li>
    </ol>
  </div>
</section>

<section class="pmx-section pmx-section--surface" id="usage" aria-labelledby="usage-title">
  <div class="pmx-section__inner">
    <h2 id="usage-title">Usage</h2>
    <p class="pmx-section__lead">Common commands after setup. Full reference: <a href="commands.md">Command reference</a>.</p>

    <div class="pmx-usage-grid">
      <div class="pmx-usage">
        <h3>Preview a trade (no order sent)</h3>
        <pre><code class="language-bash">./pmx preview trade MARKET OUTCOME 1
./pmx preview poly trade SLUG long 1</code></pre>
      </div>
      <div class="pmx-usage">
        <h3>Check balance</h3>
        <pre><code class="language-bash">./pmx balance
./pmx poly balance</code></pre>
      </div>
      <div class="pmx-usage">
        <h3>Go live (intentional)</h3>
        <pre><code class="language-bash">./pmx go-live
./pmx preflight          # expect GO
./pmx trade MARKET OUT 1 # type YES at prompt</code></pre>
      </div>
      <div class="pmx-usage">
        <h3>Research with Scout</h3>
        <pre><code class="language-bash">./scripts/new-brief.sh my-market
./pmx scout grok
# set approved: true in brief, then:
./pmx trader openai briefs/active/DATE-my-market.md</code></pre>
      </div>
    </div>
  </div>
</section>

<section class="pmx-section" id="project-structure" aria-labelledby="structure-title">
  <div class="pmx-section__inner">
    <h2 id="structure-title">Project structure</h2>
    <p class="pmx-section__lead">Main folders and entry points. Details: <a href="project-structure.md">Project structure guide</a>.</p>
    <pre><code class="language-text">pmxtrader/
├── pmx                 # CLI shim → scripts/pmx.sh
├── apps/               # bridge, cockpit, agents
├── dashboard/          # Web command center (read-only trades)
├── scripts/            # Shell entry points and servers
├── config/             # agents.json, providers.json
├── docs/               # This documentation site
├── tests/              # Python tests
├── pmxt/               # Vendored PMXT engine + sidecar
└── briefs/             # Trade briefs (gitignored when active)</code></pre>
    <div class="pmx-table-wrap">
      <table>
        <thead>
          <tr><th>Path</th><th>Purpose</th></tr>
        </thead>
        <tbody>
          <tr><td><code>apps/bridge/</code></td><td>Shared Python: commands, safety, parsing</td></tr>
          <tr><td><code>scripts/pmx.sh</code></td><td>CLI router for all <code>./pmx</code> subcommands</td></tr>
          <tr><td><code>pmxt/</code></td><td>Sidecar HTTP server and venue adapters</td></tr>
          <tr><td><code>pmxt/.env</code></td><td>Secrets — never committed</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="pmx-section pmx-section--surface" id="testing" aria-labelledby="testing-title">
  <div class="pmx-section__inner">
    <h2 id="testing-title">Testing</h2>
    <p class="pmx-section__lead">Commands reviewers and contributors should run before opening a pull request.</p>

    <div class="pmx-test-grid">
      <div class="pmx-test-card">
        <h3>Unit tests</h3>
        <pre><code class="language-bash">python3 -m pytest tests/ -q</code></pre>
      </div>
      <div class="pmx-test-card">
        <h3>Lint</h3>
        <pre><code class="language-bash">python3 -m ruff check .</code></pre>
      </div>
      <div class="pmx-test-card">
        <h3>Type check</h3>
        <pre><code class="language-bash">python3 -m mypy . --ignore-missing-imports</code></pre>
      </div>
      <div class="pmx-test-card">
        <h3>Docs build</h3>
        <pre><code class="language-bash">npm run docs:build
npm run docs:lint</code></pre>
      </div>
      <div class="pmx-test-card">
        <h3>Smoke</h3>
        <pre><code class="language-bash">./scripts/smoke-functionality.sh</code></pre>
      </div>
      <div class="pmx-test-card">
        <h3>Run locally</h3>
        <pre><code class="language-bash">./scripts/docs-serve.sh
# http://127.0.0.1:8000</code></pre>
      </div>
    </div>

    <div class="pmx-status-row" aria-label="Testing status">
      <div class="pmx-status"><span class="pmx-status__dot pmx-status__dot--pass"></span> CI on every push</div>
      <div class="pmx-status"><span class="pmx-status__dot pmx-status__dot--pass"></span> Secret scan in pre-commit</div>
      <div class="pmx-status"><span class="pmx-status__dot pmx-status__dot--pass"></span> Link check via lychee</div>
    </div>
  </div>
</section>

<section class="pmx-section" id="qa-checklist" aria-labelledby="qa-title">
  <div class="pmx-section__inner">
    <h2 id="qa-title">QA checklist</h2>
    <p class="pmx-section__lead">Use this list when reviewing the project, docs site, or a release candidate.</p>

    <div class="pmx-qa-grid">
      <div class="pmx-qa-group">
        <h3>Functionality QA</h3>
        <ul class="pmx-qa-list">
          <li>App runs locally without errors</li>
          <li>Main pages load correctly</li>
          <li>Navigation links work</li>
          <li>Buttons and CTAs work</li>
          <li>Forms or inputs validate correctly</li>
          <li>API calls work or fail gracefully</li>
          <li>Error states are handled</li>
          <li>Empty states are handled</li>
        </ul>
      </div>
      <div class="pmx-qa-group">
        <h3>UI / UX QA</h3>
        <ul class="pmx-qa-list">
          <li>Layout is clean and easy to scan</li>
          <li>Navigation is simple</li>
          <li>Mobile layout works</li>
          <li>Text is readable</li>
          <li>Spacing is consistent</li>
          <li>Buttons are clear</li>
          <li>No cluttered sections</li>
          <li>No broken visual elements</li>
        </ul>
      </div>
      <div class="pmx-qa-group">
        <h3>Documentation QA</h3>
        <ul class="pmx-qa-list">
          <li>README is clear</li>
          <li>Setup steps are accurate</li>
          <li>Environment variables are documented</li>
          <li>Usage examples are included</li>
          <li>Testing commands are included</li>
          <li>Troubleshooting notes are included</li>
          <li>GitHub links work</li>
        </ul>
      </div>
      <div class="pmx-qa-group">
        <h3>Code QA</h3>
        <ul class="pmx-qa-list">
          <li>Code is organized</li>
          <li>Components are reusable</li>
          <li>No unused files</li>
          <li>No console errors</li>
          <li>No obvious security issues</li>
          <li>Dependencies are reasonable</li>
          <li>Naming is consistent</li>
        </ul>
      </div>
      <div class="pmx-qa-group pmx-qa-group--wide">
        <h3>Deployment QA</h3>
        <ul class="pmx-qa-list pmx-qa-list--cols">
          <li>Build completes successfully</li>
          <li>Environment variables are set</li>
          <li>Production page loads</li>
          <li>GitHub link works</li>
          <li>SEO title and description exist</li>
          <li>Favicon exists</li>
          <li>404 page or fallback exists</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="pmx-section pmx-section--surface" id="troubleshooting" aria-labelledby="troubleshooting-title">
  <div class="pmx-section__inner">
    <h2 id="troubleshooting-title">Troubleshooting</h2>
    <p class="pmx-section__lead">Common issues and where to look first.</p>
    <div class="pmx-faq">
      <details>
        <summary>Install or setup failed</summary>
        <p>Run <code>./scripts/setup-dev.sh</code> again from repo root. On Linux VMs, allow <code>npm --prefix pmxt install</code> to refresh platform-specific binaries. See <code>AGENTS.md</code> for submodule and <code>node_modules</code> notes.</p>
      </details>
      <details>
        <summary>Missing environment variables</summary>
        <p>Copy <code>pmxt/.env.example</code> to <code>pmxt/.env</code>. Venue keys are separate for Kalshi and Polymarket US. Restart the sidecar with <code>./pmx warm</code> after edits.</p>
      </details>
      <details>
        <summary>App will not start / sidecar errors</summary>
        <p>Check <code>~/.pmxt/server.lock</code> for port and token. Run <code>./pmx session</code> or <code>./scripts/pmxt-server.sh restart</code>. Ensure nothing else holds port 3847.</p>
      </details>
      <details>
        <summary>Build failed</summary>
        <p>PMXT core: <code>npm run build --workspace=pmxt-core --prefix pmxt</code>. Docs: <code>npm run docs:build</code>. Read CI logs in GitHub Actions for the exact failing step.</p>
      </details>
      <details>
        <summary>Tests failed</summary>
        <p>Run <code>python3 -m pytest tests/ -q</code> locally. Cockpit tests need <code>pip install -r requirements-cockpit.txt</code>. See <a href="testing.md">Testing &amp; CI</a> for layout and smoke scripts.</p>
      </details>
    </div>
  </div>
</section>

<section class="pmx-section" id="github" aria-labelledby="github-title">
  <div class="pmx-section__inner">
    <h2 id="github-title">GitHub &amp; contribution</h2>
    <p class="pmx-section__lead">Source, issues, and pull requests live on GitHub.</p>
    <div class="pmx-panel">
      <div class="pmx-panel__row">
        <h3>Repository</h3>
        <p><a href="https://github.com/AbsCodeX/pmxtrader">github.com/AbsCodeX/pmxtrader</a> — open an issue for bugs or questions.</p>
      </div>
      <div class="pmx-panel__row">
        <h3>Pull requests</h3>
        <p>Fork the repo, branch from <code>main</code>, run the testing commands above, and open a PR with a clear summary and test plan.</p>
      </div>
      <div class="pmx-panel__row pmx-panel__row--last">
        <h3>License</h3>
        <p>See the LICENSE file in the repository root for terms.</p>
      </div>
    </div>
    <div class="pmx-hero__actions pmx-hero__actions--compact">
      <a class="pmx-btn pmx-btn--dark" href="https://github.com/AbsCodeX/pmxtrader" target="_blank" rel="noopener">View on GitHub</a>
      <a class="pmx-btn pmx-btn--ghost" href="https://github.com/AbsCodeX/pmxtrader/issues" target="_blank" rel="noopener">Open an issue</a>
    </div>
  </div>
</section>

<footer class="pmx-site-footer" aria-label="Footer">
  <div class="pmx-site-footer__inner">
    <div class="pmx-site-footer__cols">
      <div>
        <p class="pmx-site-footer__heading">Project</p>
        <a href="#overview">Overview</a>
        <a href="#features">Features</a>
        <a href="https://github.com/AbsCodeX/pmxtrader" target="_blank" rel="noopener">GitHub</a>
      </div>
      <div>
        <p class="pmx-site-footer__heading">Documentation</p>
        <a href="#setup">Setup</a>
        <a href="#usage">Usage</a>
        <a href="#testing">Testing</a>
        <a href="commands.md">Command reference</a>
      </div>
      <div>
        <p class="pmx-site-footer__heading">Deep dives</p>
        <a href="operations/index.md">Operations</a>
        <a href="architecture.md">Architecture</a>
        <a href="known-risks.md">Known risks</a>
      </div>
      <div>
        <p class="pmx-site-footer__heading">Contact</p>
        <a href="https://github.com/AbsCodeX/pmxtrader/issues" target="_blank" rel="noopener">GitHub Issues</a>
      </div>
    </div>
    <p class="pmx-site-footer__copy">Copyright © Abigail · pmxtrader documentation</p>
  </div>
</footer>
