const BACKEND_URL = "http://127.0.0.1:8000";

let tradingDaysCache = [];
let dailyBiasCache   = [];
let tradesCache      = [];
let tradeImagesCache = [];

document.addEventListener("DOMContentLoaded", async () => {
  await loadMetrics();
  await loadTradingDays();
  await loadDailyBias();
  await loadTrades();
});

// ─── Navigation ───────────────────────────────────────────────────────────────

function showSection(sectionId) {
  document.querySelectorAll(".app-section").forEach(s => s.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));

  const section = document.getElementById("section-" + sectionId);
  if (section) section.classList.add("active");

  const navItem = document.querySelector(`[data-section="${sectionId}"]`);
  if (navItem) navItem.classList.add("active");
}

// ─── Metrics ─────────────────────────────────────────────────────────────────

async function loadMetrics() {
  const el = document.getElementById("metricsSummary");
  try {
    const r = await fetch(`${BACKEND_URL}/metrics`);
    if (!r.ok) throw new Error(`Status: ${r.status}`);
    renderMetrics(await r.json());
  } catch (err) {
    el.innerHTML = `<p class="empty-state" style="color:#f87171;">Error loading: ${err.message}</p>`;
  }
}

function renderMetrics(m) {
  const el = document.getElementById("metricsSummary");

  const fmt      = (v, s = "") => (v === null || v === undefined) ? "—" : `${v}${s}`;
  const rCls     = (v) => v === null || v === undefined ? "" : v > 0 ? "metric-value-positive" : v < 0 ? "metric-value-negative" : "";
  const warnCls  = (v) => v > 0 ? "metric-value-negative" : "";

  const mkGrid = (cards) =>
    `<div class="metrics-grid">${cards.map(c =>
      `<div class="metric-card">
        <span class="metric-label">${c.label}</span>
        <span class="metric-value ${c.cls}">${c.value}</span>
      </div>`).join("")}</div>`;

  const mkSection = (title, cards) =>
    `<div class="metrics-section">
      <p class="metrics-section-title">${title}</p>
      ${mkGrid(cards)}
    </div>`;

  const summary = [
    { label: "Total Trades",    value: fmt(m.total_trades),   cls: "" },
    { label: "Valid Setups",    value: fmt(m.valid_setups),   cls: m.valid_setups > 0 ? "metric-value-positive" : "" },
    { label: "Invalid Setups",  value: fmt(m.invalid_setups), cls: warnCls(m.invalid_setups) },
  ];

  const performance = [
    { label: "Avg R",           value: fmt(m.avg_result_r),              cls: rCls(m.avg_result_r) },
    { label: "Avg R (Valid)",   value: fmt(m.avg_result_r_valid_setups), cls: rCls(m.avg_result_r_valid_setups) },
    { label: "Win Rate",        value: fmt(m.winrate_overall, "%"),      cls: "" },
    { label: "Win Rate (Valid)",value: fmt(m.winrate_valid_setups, "%"), cls: "" },
  ];

  const discipline = [
    { label: "Disciplined Trades",  value: fmt(m.disciplined_trades),  cls: m.disciplined_trades > 0 ? "metric-value-positive" : "" },
    { label: "Discipline Errors",   value: fmt(m.discipline_errors),   cls: warnCls(m.discipline_errors) },
  ];

  const tech = [
    { label: "No Sweep",         value: fmt(m.trades_without_sweep),       cls: warnCls(m.trades_without_sweep) },
    { label: "No PDA HTF",       value: fmt(m.trades_without_pda),         cls: warnCls(m.trades_without_pda) },
    { label: "No IFVG",          value: fmt(m.trades_without_ifvg),        cls: warnCls(m.trades_without_ifvg) },
    { label: "No V-Shape",       value: fmt(m.trades_without_vshape),      cls: warnCls(m.trades_without_vshape) },
    { label: "Unclean Reaction", value: fmt(m.trades_unclean_reaction),    cls: warnCls(m.trades_unclean_reaction) },
    { label: "Outside NY KZ",    value: fmt(m.trades_outside_ny_killzone), cls: warnCls(m.trades_outside_ny_killzone) },
  ];

  const psych = [
    { label: "FOMO",          value: fmt(m.fomo_trades),        cls: warnCls(m.fomo_trades) },
    { label: "Anxiety",       value: fmt(m.anxiety_trades),     cls: warnCls(m.anxiety_trades) },
    { label: "Frustration",   value: fmt(m.frustration_trades), cls: warnCls(m.frustration_trades) },
    { label: "Rule Breaks",   value: fmt(m.rule_break_trades),  cls: warnCls(m.rule_break_trades) },
    { label: "Fear Exits",    value: fmt(m.fear_exits),         cls: warnCls(m.fear_exits) },
    { label: "Impulse Exits", value: fmt(m.impulse_exits),      cls: warnCls(m.impulse_exits) },
  ];

  const gradesHtml = `
    <div class="metrics-section">
      <p class="metrics-section-title">Execution Quality</p>
      <div class="grade-grid">
        <div class="grade-metric-card grade-a-plus"><span class="grade-metric-label">A+</span><span class="grade-metric-value">${fmt(m.grade_a_plus_trades)}</span></div>
        <div class="grade-metric-card grade-a">     <span class="grade-metric-label">A</span> <span class="grade-metric-value">${fmt(m.grade_a_trades)}</span></div>
        <div class="grade-metric-card grade-b">     <span class="grade-metric-label">B</span> <span class="grade-metric-value">${fmt(m.grade_b_trades)}</span></div>
        <div class="grade-metric-card grade-c">     <span class="grade-metric-label">C</span> <span class="grade-metric-value">${fmt(m.grade_c_trades)}</span></div>
        <div class="grade-metric-card grade-f">     <span class="grade-metric-label">F</span> <span class="grade-metric-value">${fmt(m.grade_f_trades)}</span></div>
      </div>
    </div>`;

  el.innerHTML =
    mkSection("Journal Summary", summary) +
    mkSection("Performance Insights", performance) +
    mkSection("Discipline Alerts", discipline) +
    mkSection("Technical Errors", tech) +
    mkSection("Psychological Errors", psych) +
    gradesHtml;
}

// ─── Backend test ─────────────────────────────────────────────────────────────

async function testConnection() {
  const btn = document.getElementById("testBtn");
  const resultBox = document.getElementById("result");

  btn.disabled = true;
  btn.textContent = "Connecting...";
  resultBox.className = "result hidden";
  resultBox.textContent = "";

  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    if (!response.ok) throw new Error(`Server responded with status: ${response.status}`);
    const data = await response.json();
    resultBox.textContent = JSON.stringify(data, null, 2);
    resultBox.className = "result success";
  } catch (error) {
    resultBox.textContent =
      `Error connecting to backend.\n\n` +
      `Details: ${error.message}\n\n` +
      `Is the server running at ${BACKEND_URL}?`;
    resultBox.className = "result error";
  } finally {
    btn.disabled = false;
    btn.textContent = "Test Backend Connection";
  }
}

// ─── Trading Days ─────────────────────────────────────────────────────────────

async function saveTradingDay(event) {
  event.preventDefault();

  const btn = document.getElementById("saveBtn");
  const msgBox = document.getElementById("formMsg");

  btn.disabled = true;
  btn.textContent = "Saving...";
  msgBox.className = "result hidden";
  msgBox.textContent = "";

  const notesValue = document.getElementById("notes").value.trim();

  const payload = {
    trade_date: document.getElementById("trade_date").value,
    market: document.getElementById("market").value.trim(),
    is_news_day: document.getElementById("is_news_day").checked,
    is_ath_context: document.getElementById("is_ath_context").checked,
    notes: notesValue || null,
  };

  if (!payload.trade_date) {
    msgBox.textContent = "Date is required.";
    msgBox.className = "result error";
    btn.disabled = false;
    btn.textContent = "Save Trading Day";
    return;
  }
  if (!payload.market) {
    msgBox.textContent = "Market is required.";
    msgBox.className = "result error";
    btn.disabled = false;
    btn.textContent = "Save Trading Day";
    return;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/trading-days`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || `Error ${response.status}`);
    }

    msgBox.textContent = "Trading day saved successfully.";
    msgBox.className = "result success";
    document.getElementById("trading_day_form").reset();
    await loadTradingDays();
  } catch (error) {
    msgBox.textContent = `Error saving: ${error.message}`;
    msgBox.className = "result error";
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Trading Day";
  }
}

async function loadTradingDays() {
  const listEl = document.getElementById("tradingDaysList");
  listEl.innerHTML = `<p class="empty-state">Loading...</p>`;

  try {
    const response = await fetch(`${BACKEND_URL}/trading-days`);
    if (!response.ok) throw new Error(`Status: ${response.status}`);
    const days = await response.json();

    tradingDaysCache = days;
    populateDaySelect("bias_trading_day_id", days);
    populateDaySelect("trade_trading_day_id", days);
    populateMarketFilter();
    renderTradingDays(days);
  } catch (error) {
    listEl.innerHTML =
      `<p class="empty-state" style="color:#f87171;">` +
      `Error loading: ${error.message}` +
      `</p>`;
  }
}

function populateDaySelect(selectId, days) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const currentValue = select.value;
  select.innerHTML = '<option value="">— Select a trading day —</option>';
  days.forEach((day) => {
    const opt = document.createElement("option");
    opt.value = day.id;
    opt.textContent = `${day.trade_date} — ${day.market}`;
    select.appendChild(opt);
  });
  if (currentValue) select.value = currentValue;
}

function renderTradingDays(days) {
  const listEl = document.getElementById("tradingDaysList");

  if (days.length === 0) {
    listEl.innerHTML = `<p class="empty-state">No trading days registered yet.</p>`;
    return;
  }

  listEl.innerHTML = days.map((day) => {
    const date = new Date(day.trade_date + "T00:00:00").toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });

    const newsTag = `<span class="tag ${day.is_news_day ? "tag-active" : "tag-inactive"}">News</span>`;
    const athTag  = `<span class="tag ${day.is_ath_context ? "tag-active" : "tag-inactive"}">ATH</span>`;
    const notesHtml = day.notes ? `<p class="day-notes">${escapeHtml(day.notes)}</p>` : "";

    return `
      <div class="trading-day-item">
        <div class="day-header">
          <span class="day-date">${date}</span>
          <span class="day-market">${escapeHtml(day.market)}</span>
        </div>
        <div class="day-tags">${newsTag}${athTag}</div>
        ${notesHtml}
        <p class="day-created">Registered: ${formatDateTime(day.created_at)}</p>
      </div>
    `;
  }).join("");
}

// ─── Daily Bias — derivation logic ───────────────────────────────────────────

function deriveBiasValues(priceZone, pendingLiquidity, hadSweep, hadReaction) {
  const sweepOk    = hadSweep    === "yes";
  const reactionOk = hadReaction === "yes";

  const bias_alignment =
    (priceZone === "discount" && pendingLiquidity === "highs") ||
    (priceZone === "premium"  && pendingLiquidity === "lows");

  const bias_active = sweepOk && reactionOk;

  let bias_direction = "none";
  if (priceZone === "discount" && pendingLiquidity === "highs" && sweepOk && reactionOk) {
    bias_direction = "bullish";
  } else if (priceZone === "premium" && pendingLiquidity === "lows" && sweepOk && reactionOk) {
    bias_direction = "bearish";
  }

  return { bias_direction, bias_alignment, bias_active };
}

// ─── Daily Bias — advanced toggle ────────────────────────────────────────────

function toggleAdvanced() {
  const panel    = document.getElementById("advancedFields");
  const btn      = document.getElementById("toggleAdvancedBtn");
  const isHidden = panel.classList.contains("hidden");

  panel.classList.toggle("hidden");
  btn.textContent = isHidden ? "Hide advanced fields" : "Show advanced fields";
}

function resetBiasForm() {
  document.getElementById("dailyBiasForm").reset();
  document.getElementById("advancedFields").classList.add("hidden");
  document.getElementById("toggleAdvancedBtn").textContent = "Show advanced fields";
}

// ─── Daily Bias — POST ────────────────────────────────────────────────────────

async function saveDailyBias(event) {
  event.preventDefault();

  const btn    = document.getElementById("saveBiasBtn");
  const msgBox = document.getElementById("biasFormMsg");

  btn.disabled = true;
  btn.textContent = "Saving...";
  msgBox.className = "result hidden";
  msgBox.textContent = "";

  const priceZone        = document.getElementById("price_zone").value;
  const pendingLiquidity = document.getElementById("pending_liquidity").value;
  const hadSweep         = document.getElementById("had_sweep").value;
  const hadReaction      = document.getElementById("had_reaction").value;

  const { bias_direction, bias_alignment, bias_active } = deriveBiasValues(
    priceZone, pendingLiquidity, hadSweep, hadReaction
  );

  const payload = {
    trading_day_id: parseInt(document.getElementById("bias_trading_day_id").value),
    bias_direction,
    bias_alignment,
    bias_active,
    chop_equilibrium: document.getElementById("bias_chop_equilibrium").checked,
    invalidated:      document.getElementById("bias_invalidated").checked,
    comments:         document.getElementById("bias_comments").value.trim() || null,

    daily_high:                  parseFloat(document.getElementById("bias_daily_high").value)    || 0,
    daily_low:                   parseFloat(document.getElementById("bias_daily_low").value)     || 0,
    daily_eq:                    parseFloat(document.getElementById("bias_daily_eq").value)      || 0,
    current_price:               parseFloat(document.getElementById("bias_current_price").value) || 0,
    zone_position:               document.getElementById("bias_zone_position").value             || "none",
    asia_high:                   parseFloat(document.getElementById("bias_asia_high").value)     || 0,
    asia_low:                    parseFloat(document.getElementById("bias_asia_low").value)      || 0,
    london_high:                 parseFloat(document.getElementById("bias_london_high").value)   || 0,
    london_low:                  parseFloat(document.getElementById("bias_london_low").value)    || 0,
    pending_liquidity_direction: document.getElementById("bias_pending_liquidity_direction").value || "none",
    premium_discount_direction:  document.getElementById("bias_premium_discount_direction").value  || "none",
    invalidation_reason:         document.getElementById("bias_invalidation_reason").value.trim() || null,
  };

  if (!payload.trading_day_id || isNaN(payload.trading_day_id)) {
    msgBox.textContent = "You must select a Trading Day.";
    msgBox.className = "result error";
    btn.disabled = false;
    btn.textContent = "Save Daily Bias";
    return;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/daily-bias`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || `Error ${response.status}`);
    }

    msgBox.textContent = "Daily bias saved successfully.";
    msgBox.className = "result success";
    resetBiasForm();
    await loadDailyBias();
  } catch (error) {
    msgBox.textContent = `Error saving: ${error.message}`;
    msgBox.className = "result error";
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Daily Bias";
  }
}

// ─── Daily Bias — GET ─────────────────────────────────────────────────────────

async function loadDailyBias() {
  const listEl = document.getElementById("dailyBiasList");
  listEl.innerHTML = `<p class="empty-state">Loading...</p>`;

  try {
    const response = await fetch(`${BACKEND_URL}/daily-bias`);
    if (!response.ok) throw new Error(`Status: ${response.status}`);
    const biases = await response.json();

    dailyBiasCache = biases;
    populateBiasSelect(biases);
    renderDailyBias(biases);
  } catch (error) {
    listEl.innerHTML =
      `<p class="empty-state" style="color:#f87171;">` +
      `Error loading: ${error.message}` +
      `</p>`;
  }
}

function populateBiasSelect(biases) {
  const select = document.getElementById("trade_daily_bias_id");
  if (!select) return;
  const currentValue = select.value;
  select.innerHTML = '<option value="">— None —</option>';
  biases.forEach((bias) => {
    const day = tradingDaysCache.find((d) => d.id === bias.trading_day_id);
    const dayLabel = day ? `${day.trade_date} — ${day.market}` : `Day #${bias.trading_day_id}`;
    const opt = document.createElement("option");
    opt.value = bias.id;
    opt.textContent = `#${bias.id} · ${dayLabel} · ${bias.bias_direction}`;
    select.appendChild(opt);
  });
  if (currentValue) select.value = currentValue;
}

function renderDailyBias(biases) {
  const listEl = document.getElementById("dailyBiasList");

  if (biases.length === 0) {
    listEl.innerHTML = `<p class="empty-state">No daily bias registered yet.</p>`;
    return;
  }

  listEl.innerHTML = biases.map((bias) => {
    const tradingDay = tradingDaysCache.find((d) => d.id === bias.trading_day_id);
    const dayLabel = tradingDay
      ? `${tradingDay.trade_date} — ${tradingDay.market}`
      : `Trading Day #${bias.trading_day_id}`;

    const dirClass = bias.bias_direction === "bullish"
      ? "badge-bullish"
      : bias.bias_direction === "bearish"
      ? "badge-bearish"
      : "badge-none";

    const invalidationHtml = bias.invalidated && bias.invalidation_reason
      ? `<div class="bias-invalidation">Invalidated: ${escapeHtml(bias.invalidation_reason)}</div>`
      : bias.invalidated
      ? `<div class="bias-invalidation">Invalidated</div>`
      : "";

    const commentsHtml = bias.comments
      ? `<p class="bias-text">${escapeHtml(bias.comments)}</p>`
      : "";

    return `
      <div class="bias-item">
        <div class="bias-header">
          <span class="bias-day-label">${escapeHtml(dayLabel)}</span>
          <div class="bias-badges">
            <span class="badge-direction ${dirClass}">${bias.bias_direction}</span>
            <span class="${bias.bias_active ? "badge-active" : "badge-inactive"}">${bias.bias_active ? "Active" : "Inactive"}</span>
          </div>
        </div>
        <div class="bias-flags">
          <span class="bias-flag ${bias.bias_alignment   ? "bias-flag-on" : "bias-flag-off"}">Alignment</span>
          <span class="bias-flag ${bias.chop_equilibrium ? "bias-flag-on" : "bias-flag-off"}">Chop EQ</span>
          <span class="bias-flag ${bias.invalidated      ? "bias-flag-on" : "bias-flag-off"}">Invalidated</span>
        </div>
        ${invalidationHtml}
        ${commentsHtml}
        <p class="bias-created">Registered: ${formatDateTime(bias.created_at)}</p>
      </div>
    `;
  }).join("");
}

// ─── Trades — POST ────────────────────────────────────────────────────────────

async function saveTrade(event) {
  event.preventDefault();

  const btn    = document.getElementById("saveTradeBtn");
  const msgBox = document.getElementById("tradeFormMsg");

  btn.disabled = true;
  btn.textContent = "Saving...";
  msgBox.className = "result hidden";
  msgBox.textContent = "";

  const biasIdRaw = document.getElementById("trade_daily_bias_id").value;
  const resultRaw = document.getElementById("trade_result_r").value;

  const payload = {
    trading_day_id:   parseInt(document.getElementById("trade_trading_day_id").value),
    daily_bias_id:    biasIdRaw ? parseInt(biasIdRaw) : null,
    direction:        document.getElementById("trade_direction").value,
    sweep_confirmed:  document.getElementById("trade_sweep_confirmed").checked,
    pda_confirmed:    document.getElementById("trade_pda_confirmed").checked,
    ifvg_confirmed:   document.getElementById("trade_ifvg_confirmed").checked,
    vshape_confirmed: document.getElementById("trade_vshape_confirmed").checked,
    smt_confirmed:    document.getElementById("trade_smt_confirmed").checked,
    clean_reaction:   document.getElementById("trade_clean_reaction").checked,
    ny_killzone:      document.getElementById("trade_ny_killzone").checked,
    liquidity_type:   document.getElementById("trade_liquidity_type").value || null,
    entry_price:      parseFloat(document.getElementById("trade_entry_price").value),
    stop_loss:        parseFloat(document.getElementById("trade_stop_loss").value),
    take_profit:      parseFloat(document.getElementById("trade_take_profit").value),
    result_r:         resultRaw ? parseFloat(resultRaw) : null,
    notes:            document.getElementById("trade_notes").value.trim() || null,
    followed_rules:   document.getElementById("trade_followed_rules").checked,
    emotional_state:  document.getElementById("trade_emotional_state").value || null,
    exit_reason:      document.getElementById("trade_exit_reason").value || null,
  };

  if (!payload.trading_day_id || isNaN(payload.trading_day_id)) {
    msgBox.textContent = "You must select a Trading Day.";
    msgBox.className = "result error";
    btn.disabled = false;
    btn.textContent = "Save Trade";
    return;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/trades`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.detail || `Error ${response.status}`);
    }

    const imageFile = document.getElementById("trade_image_file").files?.[0];
    const imageUrl  = document.getElementById("trade_image_url").value.trim();
    const imageType = document.getElementById("trade_image_type").value || "entrada";

    if (imageFile) {
      const fd = new FormData();
      fd.append("trade_id",   result.id);
      fd.append("image_type", imageType);
      fd.append("file",       imageFile);
      const upResp = await fetch(`${BACKEND_URL}/trade-images/upload`, { method: "POST", body: fd });
      if (upResp.ok) {
        const img = await upResp.json();
        const preview = document.getElementById("trade_image_file_preview");
        if (preview) {
          preview.innerHTML = `<img src="${escapeHtml(img.image_url)}" alt="uploaded image" style="max-width:100%;border-radius:6px;margin-top:8px;" />`;
          preview.classList.remove("hidden");
        }
      }
    } else if (imageUrl) {
      await fetch(`${BACKEND_URL}/trade-images`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trade_id: result.id, image_url: imageUrl, image_type: imageType }),
      });
    }

    msgBox.textContent = "Trade saved successfully.";
    msgBox.className = "result success";
    document.getElementById("trade_form").reset();
    await loadTrades();
  } catch (error) {
    msgBox.textContent = `Error saving: ${error.message}`;
    msgBox.className = "result error";
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Trade";
  }
}

// ─── Trades — GET ─────────────────────────────────────────────────────────────

async function loadTrades() {
  const listEl = document.getElementById("tradesList");
  listEl.innerHTML = `<p class="empty-state">Loading...</p>`;

  try {
    const [tradesRes, imagesRes] = await Promise.all([
      fetch(`${BACKEND_URL}/trades`),
      fetch(`${BACKEND_URL}/trade-images`),
    ]);
    if (!tradesRes.ok) throw new Error(`Status: ${tradesRes.status}`);
    tradesCache = await tradesRes.json();
    tradeImagesCache = imagesRes.ok ? await imagesRes.json() : [];
    populateMarketFilter();
    applyTradeFilters();
  } catch (error) {
    listEl.innerHTML =
      `<p class="empty-state" style="color:#f87171;">` +
      `Error loading: ${error.message}` +
      `</p>`;
  }
}

function populateMarketFilter() {
  const select = document.getElementById("filter_mercado");
  if (!select) return;
  const currentValue = select.value;
  const markets = [...new Set(tradingDaysCache.map(d => d.market).filter(Boolean))].sort();
  select.innerHTML = '<option value="">All</option>';
  markets.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    select.appendChild(opt);
  });
  if (currentValue) select.value = currentValue;
}

function applyTradeFilters() {
  const setup      = document.getElementById("filter_setup")?.value      ?? "";
  const grade      = document.getElementById("filter_grade")?.value      ?? "";
  const disciplina = document.getElementById("filter_disciplina")?.value ?? "";
  const emocion    = document.getElementById("filter_emocion")?.value    ?? "";
  const resultado  = document.getElementById("filter_resultado")?.value  ?? "";
  const mercado    = document.getElementById("filter_mercado")?.value    ?? "";
  const killzone   = document.getElementById("filter_killzone")?.value   ?? "";
  const search     = (document.getElementById("trade_search")?.value ?? "").toLowerCase().trim();

  let filtered = tradesCache;

  if (search) {
    filtered = filtered.filter(t => {
      const day = tradingDaysCache.find(d => d.id === t.trading_day_id);
      return [day?.market ?? "", t.direction ?? "", t.liquidity_type ?? "", t.notes ?? ""]
        .join(" ").toLowerCase().includes(search);
    });
  }

  if (setup === "valid")   filtered = filtered.filter(t => t.setup_valid);
  if (setup === "invalid") filtered = filtered.filter(t => !t.setup_valid);

  if (grade) filtered = filtered.filter(t => t.trade_grade === grade);

  if (disciplina === "disciplinado") filtered = filtered.filter(t => t.discipline_label === "Trade disciplinado");
  if (disciplina === "error")        filtered = filtered.filter(t => t.discipline_label === "Error de disciplina");

  if (emocion) filtered = filtered.filter(t => t.emotional_state === emocion);

  if (resultado === "ganador")  filtered = filtered.filter(t => t.result_r != null && t.result_r > 0);
  if (resultado === "perdedor") filtered = filtered.filter(t => t.result_r != null && t.result_r < 0);
  if (resultado === "be")       filtered = filtered.filter(t => t.result_r != null && t.result_r === 0);

  if (mercado) {
    filtered = filtered.filter(t => {
      const day = tradingDaysCache.find(d => d.id === t.trading_day_id);
      return day && day.market === mercado;
    });
  }

  if (killzone === "si") filtered = filtered.filter(t => t.ny_killzone);
  if (killzone === "no") filtered = filtered.filter(t => !t.ny_killzone);

  renderTrades(filtered);
}

function renderTrades(trades) {
  const listEl  = document.getElementById("tradesList");
  const countEl = document.getElementById("tradesCount");

  if (countEl) {
    countEl.textContent = `Showing ${trades.length} of ${tradesCache.length} trades`;
  }

  if (trades.length === 0) {
    listEl.innerHTML = tradesCache.length === 0
      ? `<p class="empty-state">No trades registered yet.</p>`
      : `<p class="empty-state">No trades match the filters.</p>`;
    return;
  }

  const groups = new Map();
  trades.forEach(t => {
    const id = t.trading_day_id;
    if (!groups.has(id)) groups.set(id, []);
    groups.get(id).push(t);
  });

  const sortedGroups = [...groups.entries()].sort((a, b) => {
    const dA = tradingDaysCache.find(d => d.id === a[0])?.trade_date ?? "";
    const dB = tradingDaysCache.find(d => d.id === b[0])?.trade_date ?? "";
    return dB > dA ? 1 : -1;
  });

  listEl.innerHTML = sortedGroups.map(([dayId, dayTrades]) => {
    const day    = tradingDaysCache.find(d => d.id === dayId);
    const dateStr = day?.trade_date ?? `Day #${dayId}`;
    const market  = day?.market ?? "";

    const withR  = dayTrades.filter(t => t.result_r != null);
    const wins   = withR.filter(t => t.result_r > 0).length;
    const wr     = withR.length ? Math.round(wins / withR.length * 100) : null;
    const avgR   = withR.length
      ? (withR.reduce((s, t) => s + t.result_r, 0) / withR.length).toFixed(2)
      : null;
    const wrCls  = wr !== null ? (wr >= 50 ? "positive" : "negative") : "";
    const avgCls = avgR !== null
      ? (parseFloat(avgR) > 0 ? "positive" : parseFloat(avgR) < 0 ? "negative" : "")
      : "";

    const daySummary = `<div class="day-summary">
      <span class="day-summary-item">${dayTrades.length} trade${dayTrades.length !== 1 ? "s" : ""}</span>
      ${wr !== null ? `<span class="day-summary-item ${wrCls}">WR ${wr}%</span>` : ""}
      ${avgR !== null ? `<span class="day-summary-item ${avgCls}">Avg ${parseFloat(avgR) > 0 ? "+" : ""}${avgR}R</span>` : ""}
    </div>`;

    return `<div class="day-group">
      <div class="day-group-header">
        <div class="day-group-title">
          <span class="day-group-date">${escapeHtml(dateStr)}</span>
          <span class="day-group-market">${escapeHtml(market)}</span>
        </div>
        ${daySummary}
      </div>
      <div class="day-group-trades">${dayTrades.map(t => renderTradeCard(t)).join("")}</div>
    </div>`;
  }).join("");
}

function renderTradeCard(trade) {
  const hasTechError  = (trade.technical_error_label  || "").startsWith("Error");
  const hasPsychError = (trade.psychology_error_label || "").startsWith("Error") || !!trade.emotional_label;
  const highlightCls  = trade.trade_grade === "A+" ? "highlight-aplus"
    : hasTechError  ? "highlight-error"
    : hasPsychError ? "highlight-psychology"
    : "";

  const resultBgCls = trade.result_r != null
    ? (trade.result_r > 0 ? "trade-positive" : trade.result_r < 0 ? "trade-negative" : "trade-be")
    : "";

  const dirBadge = trade.direction === "long"
    ? `<span class="badge-long">Long</span>`
    : `<span class="badge-short">Short</span>`;

  let resultHtml = "";
  if (trade.result_r != null) {
    const cls = trade.result_r > 0 ? "result-positive" : trade.result_r < 0 ? "result-negative" : "result-neutral";
    resultHtml = `<span class="bias-level-value ${cls}">${trade.result_r > 0 ? "+" : ""}${trade.result_r}R</span>`;
  } else {
    resultHtml = `<span class="bias-level-value result-neutral">—</span>`;
  }

  const notesHtml  = trade.notes ? `<p class="bias-text">${escapeHtml(trade.notes)}</p>` : "";
  const typeLabels = { entrada: "Entry", salida: "Exit", contexto: "Context" };
  const tradeImages = tradeImagesCache.filter(img => img.trade_id === trade.id);
  const imagesHtml  = tradeImages.length
    ? `<div class="trade-images">${tradeImages.map(img =>
        `<a href="${escapeHtml(img.image_url)}" target="_blank" rel="noopener" class="trade-image-link">${typeLabels[img.image_type] || img.image_type}: View image</a>`
      ).join("")}</div>`
    : "";

  const discClass = trade.discipline_label === "Trade disciplinado" ? "badge-bullish"
    : trade.discipline_label === "Error de disciplina" ? "badge-bearish" : "badge-none";
  const labelParts = [];
  if (trade.discipline_label) labelParts.push(`<span class="badge-direction ${discClass}">${escapeHtml(trade.discipline_label)}</span>`);
  if (trade.emotional_label)  labelParts.push(`<span class="badge-direction badge-bearish">${escapeHtml(trade.emotional_label)}</span>`);
  if (trade.exit_label)       labelParts.push(`<span class="badge-direction badge-bearish">${escapeHtml(trade.exit_label)}</span>`);
  const labelsHtml = labelParts.length
    ? `<div class="bias-badges" style="flex-wrap:wrap;gap:6px;margin-bottom:10px;">${labelParts.join("")}</div>`
    : "";

  const gradeClass   = { "A+": "grade-a-plus", "A": "grade-a", "B": "grade-b", "C": "grade-c", "F": "grade-f" }[trade.trade_grade] || "grade-f";
  const techCls      = hasTechError ? "analysis-error" : (trade.technical_error_label || "").startsWith("Advertencia") ? "analysis-warn" : "analysis-ok";
  const psycCls      = (trade.psychology_error_label || "").startsWith("Error") ? "analysis-error" : "analysis-ok";
  const analysisHtml = trade.trade_grade ? `
    <div class="trade-analysis">
      <span class="trade-grade ${gradeClass}">${escapeHtml(trade.trade_grade)}</span>
      <span class="analysis-chip ${techCls}">${escapeHtml(trade.technical_error_label || "")}</span>
      <span class="analysis-chip ${psycCls}">${escapeHtml(trade.psychology_error_label || "")}</span>
      <span class="analysis-chip analysis-quality">${escapeHtml(trade.execution_quality_label || "")}</span>
    </div>` : "";

  const emotionLabels = { calmado: "Calm", ansioso: "Anxious", fomo: "FOMO", frustrado: "Frustrated", neutral: "Neutral" };
  const exitLabels    = { por_plan: "By plan", por_miedo: "By fear", por_impulso: "By impulse", manual: "Manual", otro: "Other" };
  const psychoParts   = [];
  if (trade.followed_rules != null) {
    psychoParts.push(`<span class="bias-flag ${trade.followed_rules ? "bias-flag-on" : "bias-flag-off"}">${trade.followed_rules ? "Followed rules" : "Broke rules"}</span>`);
  }
  if (trade.emotional_state) psychoParts.push(`<span class="bias-dir-chip">State: <span>${emotionLabels[trade.emotional_state] || trade.emotional_state}</span></span>`);
  if (trade.exit_reason)     psychoParts.push(`<span class="bias-dir-chip">Exit: <span>${exitLabels[trade.exit_reason] || trade.exit_reason}</span></span>`);
  const psychoHtml = psychoParts.length ? `<div class="bias-directions">${psychoParts.join("")}</div>` : "";

  return `
    <div class="trade-item ${resultBgCls} ${highlightCls}">
      <div class="bias-header">
        <div class="bias-badges">${dirBadge}</div>
        ${trade.liquidity_type ? `<span class="bias-dir-chip" style="font-size:0.72rem;">Liq: <span>${escapeHtml(trade.liquidity_type.toUpperCase())}</span></span>` : ""}
      </div>
      ${labelsHtml}
      ${analysisHtml}
      <div class="bias-levels">
        <div class="bias-level-item">
          <span class="bias-level-label">Entry</span>
          <span class="bias-level-value">${trade.entry_price}</span>
        </div>
        <div class="bias-level-item">
          <span class="bias-level-label">Stop Loss</span>
          <span class="bias-level-value">${trade.stop_loss}</span>
        </div>
        <div class="bias-level-item">
          <span class="bias-level-label">Take Profit</span>
          <span class="bias-level-value">${trade.take_profit}</span>
        </div>
        <div class="bias-level-item">
          <span class="bias-level-label">Result</span>
          ${resultHtml}
        </div>
      </div>
      <div class="bias-flags">
        <span class="bias-flag ${trade.sweep_confirmed  ? "bias-flag-on" : "bias-flag-off"}">Sweep</span>
        <span class="bias-flag ${trade.pda_confirmed    ? "bias-flag-on" : "bias-flag-off"}">PDA HTF</span>
        <span class="bias-flag ${trade.ifvg_confirmed   ? "bias-flag-on" : "bias-flag-off"}">IFVG</span>
        <span class="bias-flag ${trade.vshape_confirmed ? "bias-flag-on" : "bias-flag-off"}">V-Shape</span>
        <span class="bias-flag ${trade.smt_confirmed    ? "bias-flag-on" : "bias-flag-off"}">SMT</span>
        <span class="bias-flag ${trade.clean_reaction   ? "bias-flag-on" : "bias-flag-off"}">Clean Rx</span>
        <span class="bias-flag ${trade.ny_killzone      ? "bias-flag-on" : "bias-flag-off"}">KZ NY</span>
        <span class="bias-flag ${trade.setup_valid      ? "bias-flag-on" : "bias-flag-off"}">${trade.setup_valid ? "Valid Setup" : "Invalid Setup"}</span>
      </div>
      ${psychoHtml}
      ${imagesHtml}
      ${notesHtml}
      <p class="bias-created">Registered: ${formatDateTime(trade.created_at)}</p>
    </div>`;
}

// ─── Utilities ────────────────────────────────────────────────────────────────

function formatDateTime(isoString) {
  return new Date(isoString).toLocaleString("en-US", {
    day:    "numeric",
    month:  "numeric",
    year:   "2-digit",
    hour:   "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

// ─── PDF Reports ──────────────────────────────────────────────────────────────

async function downloadMonthlyPDF() {
  const yearVal     = parseInt(document.getElementById("pdf_year").value);
  const monthVal    = parseInt(document.getElementById("pdf_month").value);
  const includeImgs = document.getElementById("include_pdf_images")?.checked ?? false;
  const msg         = document.getElementById("pdfMsg");
  if (!yearVal || !monthVal) {
    msg.textContent = "Select year and month.";
    msg.className = "result error";
    return;
  }
  if (yearVal < 2000 || yearVal > 2100) {
    msg.textContent = "Invalid year. Must be between 2000 and 2100.";
    msg.className = "result error";
    return;
  }
  try {
    msg.textContent = "Generating PDF...";
    msg.className = "result";
    let url = `${BACKEND_URL}/reports/monthly/pdf?year=${yearVal}&month=${monthVal}`;
    if (includeImgs) url += "&include_images=true";
    window.open(url, "_blank");
    msg.textContent = "PDF generated.";
    msg.className = "result success";
    setTimeout(() => msg.classList.add("hidden"), 3000);
  } catch (err) {
    msg.textContent = `Error: ${err.message}`;
    msg.className = "result error";
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
