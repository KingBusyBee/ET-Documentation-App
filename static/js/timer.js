// Emergent Thought — Session Timer
// Inactivity timeout: 15 minutes of no interaction pauses the timer

const INACTIVITY_MS = 15 * 60 * 1000;   // 15 minutes
const TICK_MS = 1000;

let startTime = null;
let elapsed = 0;          // milliseconds accumulated before current start
let tickInterval = null;
let inactivityTimer = null;
let isRunning = false;
let isIdle = false;

// ── DOM refs ──────────────────────────────────────────────────────────────
const display      = document.getElementById("timer-display");
const btnStart     = document.getElementById("btn-start");
const btnPause     = document.getElementById("btn-pause");
const btnReset     = document.getElementById("btn-reset");
const btnUseTime   = document.getElementById("btn-use-time");
const idleWarning  = document.getElementById("idle-warning");

// ── Formatting ────────────────────────────────────────────────────────────
function fmtTime(ms) {
  const total = Math.floor(ms / 1000);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (h > 0) return `${pad(h)}:${pad(m)}:${pad(s)}`;
  return `${pad(m)}:${pad(s)}`;
}
function pad(n) { return String(n).padStart(2, "0"); }

function totalMs() {
  if (isRunning && startTime) return elapsed + (Date.now() - startTime);
  return elapsed;
}

// ── Display update ─────────────────────────────────────────────────────────
function updateDisplay() {
  display.textContent = fmtTime(totalMs());
}

// ── Timer controls ─────────────────────────────────────────────────────────
function startTimer() {
  if (isRunning) return;
  startTime = Date.now();
  isRunning = true;
  isIdle = false;
  tickInterval = setInterval(updateDisplay, TICK_MS);
  display.classList.remove("idle");
  display.classList.add("running");
  idleWarning.classList.remove("visible");
  btnStart.disabled = true;
  btnPause.disabled = false;
  resetInactivityTimer();
}

function pauseTimer() {
  if (!isRunning) return;
  elapsed += Date.now() - startTime;
  startTime = null;
  isRunning = false;
  clearInterval(tickInterval);
  display.classList.remove("running", "idle");
  btnStart.disabled = false;
  btnPause.disabled = true;
  clearTimeout(inactivityTimer);
}

function resetTimer() {
  pauseTimer();
  elapsed = 0;
  isIdle = false;
  updateDisplay();
  idleWarning.classList.remove("visible");
  btnStart.disabled = false;
}

function useTime() {
  const minutes = totalMs() / 60000;
  if (minutes < 0.1) { alert("No time recorded yet."); return; }
  // Fills the last subject row's duration field — if a parent has added
  // multiple subjects, "Use This Time" applies to whichever one they're
  // currently working on (the most recently added row).
  const durationInputs = document.querySelectorAll(".duration-input");
  const target = durationInputs[durationInputs.length - 1];
  if (!target) return;
  target.value = minutes.toFixed(1);
  target.focus();
  // Scroll to form
  document.getElementById("log-form").scrollIntoView({ behavior: "smooth" });
}

// ── Inactivity detection ───────────────────────────────────────────────────
function resetInactivityTimer() {
  clearTimeout(inactivityTimer);
  if (!isRunning) return;
  isIdle = false;
  idleWarning.classList.remove("visible");
  display.classList.remove("idle");
  if (isRunning) display.classList.add("running");

  inactivityTimer = setTimeout(() => {
    // Auto-pause after 15 minutes of inactivity
    pauseTimer();
    isIdle = true;
    display.classList.add("idle");
    idleWarning.classList.add("visible");
  }, INACTIVITY_MS);
}

// Track any user activity
["mousemove", "keydown", "click", "scroll", "touchstart"].forEach(evt => {
  document.addEventListener(evt, () => {
    if (isRunning) resetInactivityTimer();
  }, { passive: true });
});

// ── Button wiring ──────────────────────────────────────────────────────────
btnStart.addEventListener("click", startTimer);
btnPause.addEventListener("click", pauseTimer);
btnReset.addEventListener("click", () => {
  if (totalMs() > 0 && !confirm("Reset the timer? Unsaved time will be lost.")) return;
  resetTimer();
});
btnUseTime.addEventListener("click", useTime);

// ── Multi-subject log rows ─────────────────────────────────────────────────
const subjectRows   = document.getElementById("subject-rows");
const rowTemplate   = document.getElementById("subject-row-template");
const btnAddRow     = document.getElementById("btn-add-row");

function updateRemoveButtons() {
  // Can't remove the last remaining row — a log entry needs at least one subject
  const rows = subjectRows.querySelectorAll(".subject-row");
  rows.forEach(row => {
    row.querySelector(".btn-remove-row").disabled = rows.length <= 1;
  });
}

if (btnAddRow && rowTemplate) {
  btnAddRow.addEventListener("click", () => {
    const clone = rowTemplate.content.cloneNode(true);
    subjectRows.appendChild(clone);
    updateRemoveButtons();
    subjectRows.querySelector(".subject-row:last-child .subject-select").focus();
  });

  subjectRows.addEventListener("click", (e) => {
    if (e.target.classList.contains("btn-remove-row")) {
      const rows = subjectRows.querySelectorAll(".subject-row");
      if (rows.length <= 1) return;
      e.target.closest(".subject-row").remove();
      updateRemoveButtons();
    }
  });
}

// ── Session delete ─────────────────────────────────────────────────────────
document.querySelectorAll(".btn-delete").forEach(btn => {
  btn.addEventListener("click", async () => {
    const id = btn.dataset.id;
    if (!confirm("Delete this session?")) return;
    const res = await fetch(`/session/${id}`, { method: "DELETE" });
    if (res.ok) btn.closest("tr").remove();
  });
});

// ── Init ───────────────────────────────────────────────────────────────────
updateDisplay();
btnPause.disabled = true;
