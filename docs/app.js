const headlineMetrics = [
  {
    label: "Frozen OOS benchmark",
    value: "1123 trades",
    note: "Broad historical out-of-sample stream used as the anchor instead of endlessly re-optimizing on recency."
  },
  {
    label: "Recent validation window",
    value: "164 trades",
    note: "Latest 90-session slice stayed broadly aligned with the benchmark while using the same ranked-event family."
  },
  {
    label: "Research posture",
    value: "Validation first",
    note: "The point is to surface fragility, not hide it behind one strong backtest number."
  },
  {
    label: "Current verdict",
    value: "Promising, conditional",
    note: "The candidate looks viable if execution stays close to model quality. Sloppy fills weaken it fast."
  }
];

const workflowSteps = [
  {
    title: "Catalyst extraction",
    copy: "Translate opening-session behavior into explicit event families instead of loose chart narratives."
  },
  {
    title: "Context features",
    copy: "Layer in volatility state, lead-lag context, and opening-session structure to rank events more honestly."
  },
  {
    title: "Frozen benchmark",
    copy: "Lock the benchmark first so recent data can be judged against it rather than used to retune it."
  },
  {
    title: "Lifecycle modeling",
    copy: "Ask how the same trade stream behaves once fees, resets, payout rules, and drawdown barriers are applied."
  },
  {
    title: "Execution realism",
    copy: "Stress fills and costs directly, because short-holding-period systems are sensitive to degradation."
  }
];

const windowComparison = [
  { window: "20 sessions", expectancy: 23.76, status: "watch" },
  { window: "30 sessions", expectancy: 42.4, status: "watch" },
  { window: "45 sessions", expectancy: 45.39, status: "good" },
  { window: "60 sessions", expectancy: 26.07, status: "watch" },
  { window: "90 sessions", expectancy: 27.95, status: "good" }
];

const monthlyStability = [
  { month: "2026-03", expectancy: 30.47 },
  { month: "2026-04", expectancy: -15.53 },
  { month: "2026-05", expectancy: 72.87 },
  { month: "2026-06", expectancy: 16.33 }
];

const stressScenarios = [
  { name: "Base", ev: 2509.22, payoutRate: "73.3%", style: "teal" },
  { name: "+$1 / trade", ev: 2324.31, payoutRate: "71.3%", style: "amber" },
  { name: "+$2 / trade", ev: 2120.1, payoutRate: "68.0%", style: "rust" },
  { name: "5% fill haircut", ev: 888.29, payoutRate: "47.3%", style: "crimson" }
];

const firmComparison = [
  { name: "MFFU Rapid 50K", ev: 3740.59, tone: "primary" },
  { name: "Lucid Pro 50K", ev: 3706.86, tone: "secondary" },
  { name: "Topstep 50K", ev: 2509.22, tone: "tertiary" },
  { name: "Lucid Flex 50K", ev: 1936.85, tone: "secondary" },
  { name: "MFFU Flex 50K", ev: -165.65, tone: "warning" }
];

const codeSurface = [
  {
    question: "CLI entrypoint",
    answer: "The package exposes a small command-line surface for summary statistics, regime diagnostics, bootstrap EV estimation, lifecycle simulation, and static HTML reporting."
  },
  {
    question: "Input contract",
    answer: "Users bring an empirical trade CSV with a required pnl column and an optional regime column. That keeps the workbench generic and easy to reuse."
  },
  {
    question: "Public code modules",
    answer: "The package is split into io, metrics, lifecycle, reporting, and cli layers so the workflow stays inspectable instead of collapsing into one script."
  },
  {
    question: "Useful output artifact",
    answer: "The report writer turns the same CSV into a static HTML summary so someone can share results without wiring a notebook or web framework."
  },
  {
    question: "Regime-aware review",
    answer: "If the CSV carries regime labels, the workbench can break the trade stream apart by label and surface which regimes are actually carrying the expectancy."
  }
];

const sparkValues = [18, -7, 22, -28, 14, 9, -5, 31, -11, 26, 12, 19];

const tabs = Array.from(document.querySelectorAll(".segmented-button"));
const panels = {
  overview: document.getElementById("panel-overview"),
  validation: document.getElementById("panel-validation"),
  use: document.getElementById("panel-use"),
  stress: document.getElementById("panel-stress"),
  code: document.getElementById("panel-code")
};

function formatUsd(value) {
  const sign = value < 0 ? "-" : "";
  const abs = Math.abs(value);
  return `${sign}$${abs.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function buildHeadlineMetrics() {
  const container = document.getElementById("headlineMetrics");
  container.innerHTML = headlineMetrics
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

function buildWorkflow() {
  const container = document.getElementById("workflowGrid");
  container.innerHTML = workflowSteps
    .map(
      (step, index) => `
        <article class="workflow-card">
          <span class="workflow-step">${index + 1}</span>
          <h3>${step.title}</h3>
          <p class="mini-copy">${step.copy}</p>
        </article>
      `
    )
    .join("");
}

function buildSparkStrip() {
  const container = document.getElementById("heroSparkStrip");
  const maxAbs = Math.max(...sparkValues.map((value) => Math.abs(value)));
  container.innerHTML = sparkValues
    .map((value) => {
      const height = Math.max(18, (Math.abs(value) / maxAbs) * 110);
      return `<span class="spark-bar ${value >= 0 ? "positive" : "negative"}" style="height:${height}px"></span>`;
    })
    .join("");
}

function buildWindowBars() {
  const container = document.getElementById("windowBars");
  const maxValue = Math.max(...windowComparison.map((item) => item.expectancy));
  container.innerHTML = windowComparison
    .map((item) => {
      const height = Math.max(28, (item.expectancy / maxValue) * 160);
      const statusText = item.status === "good" ? "on track" : "inconclusive";
      return `
        <article class="window-bar-card">
          <div class="window-title">
            <span>${item.window}</span>
            <span class="status-chip ${item.status === "good" ? "status-good" : "badge-rust"}">${statusText}</span>
          </div>
          <div class="window-track">
            <div class="window-fill ${item.status}" style="height:${height}px"></div>
          </div>
          <div class="window-value">${formatUsd(item.expectancy)} / trade</div>
        </article>
      `;
    })
    .join("");
}

function buildMonthlyChart() {
  const container = document.getElementById("monthlyChart");
  const maxAbs = Math.max(...monthlyStability.map((item) => Math.abs(item.expectancy)));
  container.innerHTML = monthlyStability
    .map((item) => {
      const height = Math.max(28, (Math.abs(item.expectancy) / maxAbs) * 160);
      const tone = item.expectancy >= 0 ? "good" : "watch";
      return `
        <article class="month-card">
          <div class="month-title">
            <span>${item.month}</span>
            <span>${item.expectancy >= 0 ? "positive" : "negative"}</span>
          </div>
          <div class="month-track">
            <div class="month-fill ${tone}" style="height:${height}px"></div>
          </div>
          <div class="month-value">${formatUsd(item.expectancy)} / trade</div>
        </article>
      `;
    })
    .join("");
}

function buildStressGrid() {
  const container = document.getElementById("stressGrid");
  container.innerHTML = stressScenarios
    .map(
      (scenario) => `
        <article class="stress-card">
          <div class="stress-head">
            <div>
              <div class="stress-name">${scenario.name}</div>
              <div class="stress-meta">Funded payout rate ${scenario.payoutRate}</div>
            </div>
            <span class="badge badge-${scenario.style === "crimson" ? "rust" : scenario.style}">${scenario.name === "Base" ? "anchor" : "stress"}</span>
          </div>
          <div class="stress-value">${formatUsd(scenario.ev)}</div>
        </article>
      `
    )
    .join("");
}

function buildFirmBars() {
  const container = document.getElementById("firmBars");
  const maxValue = Math.max(...firmComparison.map((item) => Math.abs(item.ev)));
  container.innerHTML = firmComparison
    .map((item) => {
      const width = Math.max(4, (Math.abs(item.ev) / maxValue) * 100);
      return `
        <div class="firm-row">
          <div class="firm-label">${item.name}</div>
          <div class="firm-track">
            <div class="firm-fill ${item.tone}" style="width:${width}%"></div>
          </div>
          <div class="firm-value">${formatUsd(item.ev)}</div>
        </div>
      `;
    })
    .join("");
}

function buildCodeGrid() {
  const container = document.getElementById("codeGrid");
  container.innerHTML = codeSurface
    .map(
      (prompt) => `
        <article class="qa-card">
          <h3>${prompt.question}</h3>
          <p class="mini-copy">${prompt.answer}</p>
        </article>
      `
    )
    .join("");
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

buildHeadlineMetrics();
buildWorkflow();
buildSparkStrip();
buildWindowBars();
buildMonthlyChart();
buildStressGrid();
buildFirmBars();
buildCodeGrid();
