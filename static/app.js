const form = document.querySelector("#missionForm");
const findingsEl = document.querySelector("#findings");
const checklistEl = document.querySelector("#checklist");
const summaryEl = document.querySelector("#summary");
const scoreEl = document.querySelector("#score");
const badgeEl = document.querySelector("#decisionBadge");
const jsonEl = document.querySelector("#jsonOutput");

function formToJson(formElement) {
  const data = new FormData(formElement);
  const payload = {};
  for (const [key, value] of data.entries()) payload[key] = value;
  for (const checkbox of formElement.querySelectorAll('input[type="checkbox"]')) {
    payload[checkbox.name] = checkbox.checked;
  }
  return payload;
}

function statusIcon(status) {
  return { pass: "✓", caution: "!", fail: "×" }[status] || "•";
}

function render(result) {
  scoreEl.textContent = result.risk_score;
  badgeEl.textContent = result.decision.status;
  badgeEl.className = `badge ${result.decision.tone}`;
  summaryEl.textContent = result.decision.summary;

  findingsEl.innerHTML = result.findings.map((finding) => `
    <article class="finding ${finding.status}">
      <div class="status">${statusIcon(finding.status)}</div>
      <div>
        <strong>${finding.title}</strong>
        <p>${finding.message}</p>
        <small>${finding.regulation} · ${finding.recommendation}</small>
      </div>
    </article>
  `).join("");

  checklistEl.innerHTML = result.checklist.map((item) => `
    <div class="task"><span>${item.category}</span><p>${item.task}</p></div>
  `).join("");

  jsonEl.textContent = JSON.stringify(result, null, 2);
}

async function evaluate(event) {
  event?.preventDefault();

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  summaryEl.textContent = "Evaluating mission against configured FAA Part 107 advisory rules...";
  const response = await fetch("/api/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formToJson(form))
  });
  render(await response.json());
}

form.addEventListener("submit", evaluate);
