const tabs = Array.from(document.querySelectorAll(".segmented-button"));
const panels = {
  overview: document.getElementById("panel-overview"),
  validation: document.getElementById("panel-validation"),
  ablations: document.getElementById("panel-ablations"),
  artifacts: document.getElementById("panel-artifacts"),
  package: document.getElementById("panel-package")
};

const appState = document.getElementById("appState");

function formatUsd(value, digits = 2) {
  const sign = value < 0 ? "-" : "";
  const abs = Math.abs(value);
  return `${sign}$${abs.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  })}`;
}

function formatUsdCompact(value) {
  const sign = value < 0 ? "-" : "";
  const abs = Math.abs(value);
  if (abs >= 1000) {
    return `${sign}$${(abs / 1000).toFixed(2)}k`;
  }
  return formatUsd(value);
}

function formatPct(value, digits = 1) {
  return `${(value * 100).toFixed(digits)}%`;
}

function formatStatus(status) {
  const map = {
    on_track: "on track",
    inconclusive: "inconclusive",
    candidate_ready_for_small_real_eval_not_proven_live_automation: "candidate ready for small real eval"
  };
  return map[status] || String(status).replaceAll("_", " ");
}

function statusClass(status) {
  if (status === "on_track" || status === "good") {
    return "status-good";
  }
  if (status === "inconclusive" || status === "watch") {
    return "badge-rust";
  }
  return "badge-amber";
}

function toDocHref(path) {
  if (path.startsWith("docs/")) {
    return `./${path.slice("docs/".length)}`;
  }
  return `../${path}`;
}

function activateTab(targetTab) {
  tabs.forEach((button) => {
    const isActive = button.dataset.tab === targetTab;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-selected", isActive ? "true" : "false");
  });

  Object.entries(panels).forEach(([name, panel]) => {
    panel.classList.toggle("is-active", name === targetTab);
  });
}

tabs.forEach((button) => {
  button.addEventListener("click", () => activateTab(button.dataset.tab));
});

function buildHero(data) {
  const benchmark = data.reference.benchmark_summary;
  const deltas = data.reference.window_checks.map((item) => item.expectancy - benchmark.expectancy);
  const maxAbs = Math.max(...deltas.map((value) => Math.abs(value)), 1);
  const sparkBars = deltas
    .map((value) => {
      const height = Math.max(18, (Math.abs(value) / maxAbs) * 110);
      return `<span class="spark-bar ${value >= 0 ? "positive" : "negative"}" style="height:${height}px"></span>`;
    })
    .join("");

  document.getElementById("heroVisual").innerHTML = `
    <div class="visual-label-row">
      <span>Frozen benchmark</span>
      <span class="status-chip ${statusClass(benchmark.observed_recent_status)}">${formatStatus(benchmark.observed_recent_status)}</span>
    </div>
    <div class="visual-metrics">
      <div>
        <span class="visual-number">${benchmark.trades}</span>
        <span class="visual-caption">broad OOS trades</span>
      </div>
      <div>
        <span class="visual-number">${formatPct(benchmark.win_rate)}</span>
        <span class="visual-caption">benchmark win rate</span>
      </div>
      <div>
        <span class="visual-number">${formatUsd(benchmark.expectancy)}</span>
        <span class="visual-caption">benchmark expectancy</span>
      </div>
      <div>
        <span class="visual-number">${formatUsdCompact(benchmark.lifecycle_net_ev)}</span>
        <span class="visual-caption">lifecycle EV</span>
      </div>
    </div>
    <div class="spark-strip" aria-hidden="true">${sparkBars}</div>
  `;
}

function buildHeadlineMetrics(data) {
  const benchmark = data.reference.benchmark_summary;
  const methodology = data.reference.methodology;
  const bootstrap = data.package.bootstrap_ev;
  const profile = data.package.data_profile;

  const metrics = [
    {
      label: "Frozen benchmark",
      value: `${benchmark.trades} trades`,
      note: `${formatUsd(benchmark.expectancy)} per trade across the broad out-of-sample anchor.`
    },
    {
      label: "Recent validation window",
      value: `${benchmark.observed_recent_trades} trades`,
      note: `Recent 90-session slice stayed ${formatStatus(benchmark.observed_recent_status)} versus the frozen reference.`
    },
    {
      label: "Public sample posture",
      value: bootstrap.lower_bound_positive ? "lower bound positive" : "CI still crosses zero",
      note: `Public package bootstrap range: ${formatUsd(bootstrap.lower)} to ${formatUsd(bootstrap.upper)}.`
    },
    {
      label: "Current recommendation",
      value: formatStatus(methodology.recommendation.status),
      note: `${profile.rows} anonymized public trades across ${profile.sessions} sessions reproduce the checked-in public workbench flow.`
    }
  ];

  document.getElementById("headlineMetrics").innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card">
          <div>
            <div class="metric-label">${metric.label}</div>
            <div class="metric-value">${metric.value}</div>
          </div>
          <p class="metric-note">${metric.note}</p>
        </article>
      `
    )
    .join("");
}

function buildOverview(data) {
  const methodology = data.reference.methodology;
  const benchmark = data.reference.benchmark_summary;
  const monthly = data.reference.monthly_stability.filter((item) => typeof item.expectancy === "number");
  const negativeMonths = monthly.filter((item) => item.expectancy < 0);
  const stressBase = data.reference.stress_scenarios.find((item) => item.scenario === "base");
  const stressHaircut = data.reference.stress_scenarios.find((item) => item.scenario === "fill_haircut_5pct");
  const normalRegime = data.package.regimes.normal;

  const workflowSteps = [
    {
      title: "Freeze the benchmark",
      copy: `Use ${benchmark.trades} broad OOS trades as the anchor so recent data is judged, not re-tuned.`
    },
    {
      title: "Judge windows against it",
      copy: "Check 20 to 90-session slices for expectancy drift, lower-bound behavior, and consistency flags."
    },
    {
      title: "Ablate weak branches",
      copy: `Promote only policies that keep a positive EV lower bound, currently ${methodology.best_current_policy}.`
    },
    {
      title: "Wrap in account rules",
      copy: "Model challenge targets, loss barriers, fees, payout triggers, and splits with lifecycle Monte Carlo."
    },
    {
      title: "Stress execution quality",
      copy: "Test added cost and fill degradation directly because short-hold futures ideas are sensitive to slippage."
    }
  ];

  panels.overview.innerHTML = `
    <div class="section-head">
      <h2>Why this repo exists</h2>
      <p>
        The public mirror is designed to show research process, not a magic
        strategy reveal. It keeps the benchmark, ablations, lifecycle
        modeling, and limitations visible while leaving deployable private
        thresholds out of scope.
      </p>
    </div>

    <div class="split-layout">
      <article class="stack-block">
        <h3>Research question</h3>
        <p>
          Can a modest intraday edge in equity-index futures survive realistic
          friction and account geometry once the benchmark is frozen and
          execution degradation is treated as model risk?
        </p>
      </article>
      <article class="stack-block">
        <h3>Public boundary</h3>
        <div class="boundary-grid">
          <div class="boundary-card">
            <div class="boundary-title">Included</div>
            <ul class="detail-list">
              ${methodology.public_boundary.includes.map((item) => `<li>${item}</li>`).join("")}
            </ul>
          </div>
          <div class="boundary-card">
            <div class="boundary-title">Excluded</div>
            <ul class="detail-list">
              ${methodology.public_boundary.excludes.map((item) => `<li>${item}</li>`).join("")}
            </ul>
          </div>
        </div>
      </article>
    </div>

    <div class="workflow-grid">
      ${workflowSteps
        .map(
          (step, index) => `
            <article class="workflow-card">
              <span class="workflow-step">${index + 1}</span>
              <h3>${step.title}</h3>
              <p class="mini-copy">${step.copy}</p>
            </article>
          `
        )
        .join("")}
    </div>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>What survived deeper review</h3>
        <ul class="detail-list">
          ${methodology.recommendation.why.map((item) => `<li>${item}</li>`).join("")}
        </ul>
      </article>
      <article class="mini-panel">
        <h3>What still breaks first</h3>
        <ul class="detail-list">
          <li>5% fill haircut drops lifecycle EV from ${formatUsd(stressBase.net_ev)} to ${formatUsd(stressHaircut.net_ev)}.</li>
          <li>${negativeMonths.length} month bucket went negative in the checked-in monthly stability reference.</li>
          <li>Public sample bootstrap still crosses zero, so the public package example is realistic but intentionally not over-sold.</li>
          <li>The normal regime bucket in the public sample is negative at ${formatUsd(normalRegime.expectancy)} per trade.</li>
        </ul>
      </article>
    </div>
  `;
}

function buildWindowBars(items) {
  const maxValue = Math.max(...items.map((item) => Math.abs(item.expectancy)), 1);
  return items
    .map((item) => {
      const height = Math.max(28, (Math.abs(item.expectancy) / maxValue) * 160);
      return `
        <article class="window-bar-card">
          <div class="window-title">
            <span>${item.recent_sessions} sessions</span>
            <span class="status-chip ${statusClass(item.benchmark_status)}">${formatStatus(item.benchmark_status)}</span>
          </div>
          <div class="window-track">
            <div class="window-fill ${item.expectancy >= 0 ? "good" : "watch"}" style="height:${height}px"></div>
          </div>
          <div class="window-value">${formatUsd(item.expectancy)} / trade</div>
        </article>
      `;
    })
    .join("");
}

function buildMonthlyChart(items) {
  const filtered = items.filter((item) => typeof item.expectancy === "number");
  const maxAbs = Math.max(...filtered.map((item) => Math.abs(item.expectancy)), 1);
  return filtered
    .map((item) => {
      const height = Math.max(28, (Math.abs(item.expectancy) / maxAbs) * 160);
      return `
        <article class="month-card">
          <div class="month-title">
            <span>${item.month}</span>
            <span>${item.expectancy >= 0 ? "positive" : "negative"}</span>
          </div>
          <div class="month-track">
            <div class="month-fill ${item.expectancy >= 0 ? "good" : "watch"}" style="height:${height}px"></div>
          </div>
          <div class="month-value">${formatUsd(item.expectancy)} / trade</div>
        </article>
      `;
    })
    .join("");
}

function buildProfileTokens(items, tone = "badge-teal") {
  return items
    .map(
      (item) => `
        <span class="artifact-chip ${tone}">
          <span>${item.label}</span>
          <strong>${item.count}</strong>
          <span>${formatPct(item.share, 1)}</span>
        </span>
      `
    )
    .join("");
}

function buildValidation(data) {
  const benchmark = data.reference.benchmark_summary;
  const bootstrap = data.package.bootstrap_ev;
  const packageSummary = data.package.summary;
  const regimes = data.package.regimes;
  const profile = data.package.data_profile;

  panels.validation.innerHTML = `
    <div class="section-head">
      <h2>Validation posture</h2>
      <p>
        The broad benchmark is frozen first, then recent windows are checked
        against it. The public package reproduces the latest anonymized sample
        so the repo can be audited end to end.
      </p>
    </div>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>Frozen benchmark</h3>
        <dl class="stat-list">
          <div><dt>Trades</dt><dd>${benchmark.trades}</dd></div>
          <div><dt>Win rate</dt><dd>${formatPct(benchmark.win_rate)}</dd></div>
          <div><dt>Expectancy</dt><dd>${formatUsd(benchmark.expectancy)}</dd></div>
          <div><dt>Lifecycle EV</dt><dd>${formatUsd(benchmark.lifecycle_net_ev)}</dd></div>
        </dl>
      </article>
      <article class="mini-panel">
        <h3>Public reproducible sample</h3>
        <dl class="stat-list">
          <div><dt>Trades</dt><dd>${packageSummary.trades}</dd></div>
          <div><dt>Win rate</dt><dd>${formatPct(packageSummary.win_rate)}</dd></div>
          <div><dt>Expectancy</dt><dd>${formatUsd(packageSummary.expectancy)}</dd></div>
          <div><dt>EV lower bound</dt><dd class="${bootstrap.lower > 0 ? "positive-text" : ""}">${formatUsd(bootstrap.lower)}</dd></div>
        </dl>
      </article>
    </div>

    <div class="chart-block">
      <div class="chart-header">
        <h3>Recent-window checks</h3>
        <p>
          20, 30, 45, 60, and 90-session slices are checked against the same
          benchmark instead of being promoted one by one after the fact.
        </p>
      </div>
      <div class="window-bars">${buildWindowBars(data.reference.window_checks)}</div>
    </div>

    <div class="chart-block">
      <div class="chart-header">
        <h3>Monthly stability</h3>
        <p>
          This section is useful because it shows the path was uneven. A
          credible research repo should not hide the weak buckets.
        </p>
      </div>
      <div class="monthly-chart">${buildMonthlyChart(data.reference.monthly_stability)}</div>
    </div>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>Regime split in the public sample</h3>
        <table class="dense-table">
          <thead>
            <tr>
              <th>Regime</th>
              <th>Trades</th>
              <th>Win rate</th>
              <th>Expectancy</th>
            </tr>
          </thead>
          <tbody>
            ${Object.entries(regimes)
              .map(
                ([regime, stats]) => `
                  <tr>
                    <td>${regime}</td>
                    <td>${stats.trades}</td>
                    <td>${formatPct(stats.win_rate)}</td>
                    <td class="${stats.expectancy >= 0 ? "positive-text" : "negative-text"}">${formatUsd(stats.expectancy)}</td>
                  </tr>
                `
              )
              .join("")}
          </tbody>
        </table>
      </article>
      <article class="mini-panel">
        <h3>Public data profile</h3>
        <p class="mini-copy">
          The checked-in anonymized export preserves empirical pnl while
          coarsening timing and exact trigger detail.
        </p>
        <div class="token-block">
          <div class="token-title">Event families</div>
          <div class="token-list">${buildProfileTokens(profile.event_families, "badge-teal")}</div>
        </div>
        <div class="token-block">
          <div class="token-title">Outcomes</div>
          <div class="token-list">${buildProfileTokens(profile.outcomes, "badge-amber")}</div>
        </div>
      </article>
    </div>
  `;
}

function buildPolicyRows(rows, candidatePolicy) {
  return rows
    .map((row) => {
      const highlight = row.policy === candidatePolicy ? "table-row-highlight" : "";
      return `
        <tr class="${highlight}">
          <td>${row.policy}</td>
          <td>${row.trades}</td>
          <td>${formatPct(row.win_rate)}</td>
          <td>${formatUsd(row.expectancy)}</td>
          <td class="${row.ev_lower > 0 ? "positive-text" : "negative-text"}">${formatUsd(row.ev_lower)}</td>
          <td><span class="status-chip ${statusClass(row.benchmark_status)}">${formatStatus(row.benchmark_status)}</span></td>
          <td>${formatUsd(row.lifecycle_net_ev)}</td>
        </tr>
      `;
    })
    .join("");
}

function buildStressCards(rows) {
  return rows
    .map(
      (row) => `
        <article class="stress-card">
          <div class="stress-head">
            <div>
              <div class="stress-name">${row.scenario.replaceAll("_", " ")}</div>
              <div class="stress-meta">funded payout rate ${formatPct(row.funded_payout_rate)}</div>
            </div>
            <span class="badge ${row.scenario === "fill_haircut_5pct" ? "badge-rust" : row.scenario === "base" ? "badge-teal" : "badge-amber"}">${row.scenario === "base" ? "anchor" : "stress"}</span>
          </div>
          <div class="stress-value">${formatUsd(row.net_ev)}</div>
          <div class="stress-meta">median ${formatUsd(row.median_net)} | p05 ${formatUsd(row.p05_net)}</div>
        </article>
      `
    )
    .join("");
}

function buildFirmRows(rows) {
  return rows
    .map(
      (row) => `
        <tr>
          <td>${row.prop_firm}</td>
          <td>${row.program}</td>
          <td>${formatUsd(row.net_ev)}</td>
          <td>${formatPct(row.funded_payout_rate)}</td>
          <td>${formatUsd(row.avg_fees_paid)}</td>
        </tr>
      `
    )
    .join("");
}

function buildAblations(data) {
  const methodology = data.reference.methodology;
  const baseRows = data.reference.firm_comparison;
  const stressRows = data.reference.firm_comparison_plus2usd;
  const bestBase = baseRows[0];
  const bestStress = stressRows[0];

  panels.ablations.innerHTML = `
    <div class="section-head">
      <h2>Ablations and stress</h2>
      <p>
        This is where the repo starts to feel less like a pitch deck and more
        like research. Candidate branches are compared directly, then the same
        trade stream is wrapped in cost stress and multiple account geometries.
      </p>
    </div>

    <article class="chart-block">
      <div class="chart-header">
        <h3>Policy ablations</h3>
        <p>
          Only one branch kept a positive EV lower bound at the 90-session
          anchor, which is the exact reason it became the promoted policy.
        </p>
      </div>
      <table class="dense-table">
        <thead>
          <tr>
            <th>Policy</th>
            <th>Trades</th>
            <th>Win rate</th>
            <th>Expectancy</th>
            <th>EV lower</th>
            <th>Status</th>
            <th>Lifecycle EV</th>
          </tr>
        </thead>
        <tbody>
          ${buildPolicyRows(data.reference.policy_ablations, methodology.best_current_policy)}
        </tbody>
      </table>
    </article>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>Execution stress ladder</h3>
        <div class="stress-grid">${buildStressCards(data.reference.stress_scenarios)}</div>
      </article>
      <article class="mini-panel">
        <h3>What the stress ladder says</h3>
        <ul class="detail-list">
          <li>Small extra cost is tolerable. Broad fill degradation is not.</li>
          <li>Base lifecycle EV stays positive through the +$2 per trade stress case.</li>
          <li>The fill haircut case is the cleanest warning that execution quality is a first-order variable.</li>
          <li>The promoted branch is good enough to study further, not good enough to call production-safe by default.</li>
        </ul>
      </article>
    </div>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>Cross-firm base case</h3>
        <table class="dense-table">
          <thead>
            <tr>
              <th>Firm</th>
              <th>Program</th>
              <th>Net EV</th>
              <th>Payout rate</th>
              <th>Avg fees</th>
            </tr>
          </thead>
          <tbody>${buildFirmRows(baseRows)}</tbody>
        </table>
      </article>
      <article class="mini-panel">
        <h3>Cross-firm +$2 per trade</h3>
        <table class="dense-table">
          <thead>
            <tr>
              <th>Firm</th>
              <th>Program</th>
              <th>Net EV</th>
              <th>Payout rate</th>
              <th>Avg fees</th>
            </tr>
          </thead>
          <tbody>${buildFirmRows(stressRows)}</tbody>
        </table>
      </article>
    </div>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>Ranking signal</h3>
        <p class="mini-copy">
          Base case leader: <strong>${bestBase.prop_firm} ${bestBase.program}</strong> at
          <strong>${formatUsd(bestBase.net_ev)}</strong>.
        </p>
        <p class="mini-copy">
          Under +$2 cost stress the same top slot remains at
          <strong>${formatUsd(bestStress.net_ev)}</strong>, which is a healthier sign than a ranking that flips immediately.
        </p>
      </article>
      <article class="mini-panel">
        <h3>Interpretation rule</h3>
        <p class="mini-copy">
          The repo is not arguing that payout geometry creates alpha. It is
          showing that account structure changes the realized economics of a
          small edge enough that lifecycle modeling belongs in the research
          loop, not after it.
        </p>
      </article>
    </div>
  `;
}

function buildArtifactRows(artifacts) {
  return artifacts
    .map(
      (artifact) => `
        <tr>
          <td>
            <a class="artifact-link" href="${toDocHref(artifact.path)}">${artifact.label}</a>
          </td>
          <td><span class="artifact-chip ${artifact.group === "reference" ? "badge-teal" : artifact.group === "generated" ? "badge-amber" : "badge-olive"}">${artifact.group}</span></td>
          <td><span class="artifact-chip badge-rust">${artifact.kind}</span></td>
          <td>${artifact.description}</td>
          <td class="artifact-path">${artifact.path}</td>
        </tr>
      `
    )
    .join("");
}

function buildManifestList(entries) {
  return Object.values(entries)
    .map((path) => `<li><a class="artifact-link" href="${toDocHref(path)}">${path}</a></li>`)
    .join("");
}

function buildArtifacts(data) {
  const methodology = data.reference.methodology;
  const commands = data.package.commands.slice(0, 2).join("\n");

  panels.artifacts.innerHTML = `
    <div class="section-head">
      <h2>Artifact trail</h2>
      <p>
        The project stands out more when a reader can move from a top-line
        claim to the exact JSON or CSV that supports it. This tab is the public
        audit surface.
      </p>
    </div>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>Interpretation rules</h3>
        <ul class="detail-list">
          ${methodology.interpretation_rules.map((item) => `<li>${item}</li>`).join("")}
        </ul>
      </article>
      <article class="mini-panel">
        <h3>One-command public rebuild</h3>
        <div class="code-card">
          <pre><code>${commands}</code></pre>
        </div>
        <p class="mini-copy">
          The rebuild command regenerates the checked-in report, generated
          package JSON outputs, artifact manifest, and docs payload from public
          artifacts only.
        </p>
      </article>
    </div>

    <article class="chart-block">
      <div class="chart-header">
        <h3>Checked-in artifacts</h3>
        <p>
          Reference artifacts carry the frozen research claims. Generated
          artifacts prove the public package can rebuild a reproducible surface
          from the anonymized sample.
        </p>
      </div>
      <table class="dense-table artifact-table">
        <thead>
          <tr>
            <th>Artifact</th>
            <th>Group</th>
            <th>Kind</th>
            <th>Description</th>
            <th>Path</th>
          </tr>
        </thead>
        <tbody>${buildArtifactRows(data.artifacts)}</tbody>
      </table>
    </article>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>Reference layer</h3>
        <ul class="detail-list">${buildManifestList(data.manifest.reference)}</ul>
      </article>
      <article class="mini-panel">
        <h3>Generated layer</h3>
        <ul class="detail-list">
          ${buildManifestList(data.manifest.generated)}
          <li><a class="artifact-link" href="${toDocHref(data.manifest.report)}">${data.manifest.report}</a></li>
          <li><a class="artifact-link" href="${toDocHref(data.manifest.docs_data)}">${data.manifest.docs_data}</a></li>
        </ul>
      </article>
    </div>
  `;
}

function buildCommandBlock(commands) {
  return commands.join("\n");
}

function buildModuleCards() {
  const modules = [
    {
      title: "io.py",
      copy: "Load empirical trade rows from CSV with a minimal required schema."
    },
    {
      title: "metrics.py",
      copy: "Compute trade summary, regime splits, and bootstrap EV confidence intervals."
    },
    {
      title: "lifecycle.py",
      copy: "Run lifecycle Monte Carlo under configurable challenge and funded rules."
    },
    {
      title: "reporting.py",
      copy: "Write a shareable static HTML report from the same empirical trade stream."
    },
    {
      title: "public_demo.py",
      copy: "Rebuild the docs payload and generated public artifacts from committed example inputs."
    }
  ];

  return modules
    .map(
      (module) => `
        <article class="qa-card">
          <h3>${module.title}</h3>
          <p class="mini-copy">${module.copy}</p>
        </article>
      `
    )
    .join("");
}

function buildPackage(data) {
  const metadata = data.reference.dataset_metadata;
  const generated = data.manifest.generated;

  panels.package.innerHTML = `
    <div class="section-head">
      <h2>Runnable package surface</h2>
      <p>
        The public package is intentionally smaller than the private research
        environment, but it is still real code. Someone can install it, run the
        CLI, inspect the generated outputs, and understand what is public-safe
        versus private.
      </p>
    </div>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>Quick start</h3>
        <div class="code-card">
          <pre><code>${buildCommandBlock(data.package.commands)}</code></pre>
        </div>
      </article>
      <article class="mini-panel">
        <h3>Input contract</h3>
        <div class="code-card">
          <pre><code>pnl,regime
161.26,volatile
-251.24,normal
161.26,volatile</code></pre>
        </div>
        <p class="mini-copy">
          Core metrics require <code>pnl</code> and optionally read
          <code>regime</code>. The checked-in public sample adds
          ${metadata.fields.filter((field) => !["pnl", "regime"].includes(field)).join(", ")}
          so the example artifacts feel closer to a real trade export.
        </p>
      </article>
    </div>

    <div class="code-grid">
      ${buildModuleCards()}
    </div>

    <div class="comparison-grid">
      <article class="mini-panel">
        <h3>Generated outputs</h3>
        <ul class="detail-list">
          <li><a class="artifact-link" href="${toDocHref(generated.package_summary)}">package_summary.json</a></li>
          <li><a class="artifact-link" href="${toDocHref(generated.package_regimes)}">package_regimes.json</a></li>
          <li><a class="artifact-link" href="${toDocHref(generated.package_bootstrap_ev)}">package_bootstrap_ev.json</a></li>
          <li><a class="artifact-link" href="${toDocHref(generated.package_lifecycle)}">package_lifecycle.json</a></li>
          <li><a class="artifact-link" href="${toDocHref(data.package.report_path)}">anonymized_oos_report.html</a></li>
        </ul>
      </article>
      <article class="mini-panel">
        <h3>Useful, not magical</h3>
        <ul class="detail-list">
          <li>Good for trade-level EV review, regime diagnostics, and quick lifecycle sanity checks.</li>
          <li>Good for showing research workflow and limits in a recruiter-safe repo.</li>
          <li>Not a broker adapter, venue bridge, or deployable live strategy release.</li>
          <li>Not a substitute for venue-specific execution validation.</li>
        </ul>
      </article>
    </div>
  `;
}

function setLoadingState(message, kind = "loading") {
  appState.textContent = message;
  appState.className = `app-state app-state-${kind}`;
}

async function loadSiteData() {
  const response = await fetch("data/site_data.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load docs/data/site_data.json (${response.status})`);
  }
  return response.json();
}

async function main() {
  try {
    setLoadingState("Loading public artifacts...", "loading");
    const data = await loadSiteData();
    buildHero(data);
    buildHeadlineMetrics(data);
    buildOverview(data);
    buildValidation(data);
    buildAblations(data);
    buildArtifacts(data);
    buildPackage(data);
    appState.classList.add("is-hidden");
  } catch (error) {
    console.error(error);
    setLoadingState(
      "Could not load docs/data/site_data.json. Preview the docs through a local server or GitHub Pages.",
      "error"
    );
  }
}

main();
