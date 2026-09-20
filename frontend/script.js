const names = [
  "Evidence Agent",
  "Career Reconstruction Agent",
  "Skill Translator Agent",
  "Job Requirement Agent",
  "Evidence Gap Engine",
  "Verification Agent",
  "Learning & Opportunity Agent"
];

const $ = id => document.getElementById(id);

function renderAgents(active = -1, done = false) {
  $("agents").innerHTML = names.map((n, i) => {
    let c = done ? "done" : i === active ? "on" : "";
    let state = done ? "Completed" : i === active ? "Running" : "Waiting";

    return `
      <div class="agent ${c}">
        <div class="agent-top">
          <b><span class="dot"></span>${n}</b>
        </div>
        <div class="state">${state}</div>
      </div>
    `;
  }).join("");
}

renderAgents();


/* =========================
   LOAD MOCK SAP DATA
========================= */

async function loadSAP() {
  try {
    const [e, j, l, v] = await Promise.all([
      fetch("/api/sap/employees"),
      fetch("/api/sap/jobs"),
      fetch("/api/sap/learning"),
      fetch("/api/sap/evidence-events")
    ]);

    const ed = await e.json();
    const jd = await j.json();
    const ld = await l.json();
    const vd = await v.json();

    $("empCount").textContent = ed.data.length;
    $("reqCount").textContent = jd.data.length;
    $("learnCount").textContent = ld.data.length;
    $("eventCount").textContent = vd.data.length;

    $("sapStatus").textContent =
      "Enterprise context loaded • Employees • Requisitions • Learning • Evidence events";

    $("learningCards").innerHTML = ld.data.map(x => `
      <div class="card">
        <b>${x.title}</b>
        <p>${x.provider}</p>
        <small>${x.capabilities.join(" • ")}</small>
      </div>
    `).join("");

  } catch (e) {
    console.error("SAP loading error:", e);
    $("sapStatus").textContent = "Enterprise context unavailable";
  }
}

loadSAP();


/* =========================
   AI + SAP ANALYSIS
========================= */

async function runAnalysis() {

  const btn = $("run");

  btn.disabled = true;

  $("status").classList.remove("error");

  $("status").textContent =
    "AI orchestrator is reading candidate evidence + enterprise context…";


  /* Read input values safely */

  const candidateElement = $("candidate");
  const jobElement = $("job");

  const candidate =
    candidateElement ? candidateElement.value.trim() : "";

  const job =
    jobElement ? jobElement.value.trim() : "";


  /* Check required data BEFORE calling backend */

  if (!candidate) {
    $("status").classList.add("error");
    $("status").textContent =
      "⚠ Candidate profile is empty.";

    btn.disabled = false;
    return;
  }

  if (!job) {
    $("status").classList.add("error");
    $("status").textContent =
      "⚠ Job description is empty.";

    btn.disabled = false;
    return;
  }


  /* Show agent progress */

  for (let i = 0; i < names.length; i++) {
    renderAgents(i);

    await new Promise(resolve =>
      setTimeout(resolve, 260)
    );
  }


  try {

    /* Send candidate + job to backend */

    const r = await fetch("/api/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        candidate: candidate,
        job: job
      })
    });


    const d = await r.json();


    if (!r.ok) {
      throw new Error(
        d.error || "Analysis failed"
      );
    }


    /* Analysis completed */

    renderAgents(-1, true);

    $("status").textContent =
      `Analysis complete • ${d.ai_model || "Local AI"} • ${d.sap_connection?.mode || "SAP mock"}`;


    /* =========================
       CAPABILITY MAP
    ========================= */

    $("capabilities").innerHTML =
      (d.capabilities || []).map(x => `
        <div class="card">
          <b>${x.capability}</b>

          <div class="level ${x.level}">
            ${String(x.level || "").toUpperCase()}
          </div>

          <p>
            ${(x.evidence || []).join(" ")}
          </p>
        </div>
      `).join("")
      || "No capability signals returned.";


    /* =========================
       EVIDENCE GAP TABLE
    ========================= */

    $("gapsTable").innerHTML = `
      <div class="row head">
        <div>Capability</div>
        <div>Status</div>
        <div>Importance</div>
        <div>Interpretation</div>
      </div>

      ${(d.gaps || []).map(x => `
        <div class="row">
          <b>${x.capability}</b>
          <span class="${x.status}">
            ${x.status}
          </span>
          <span>
            ${x.importance || "—"}
          </span>
          <span>
            ${x.note || ""}
          </span>
        </div>
      `).join("")}
    `;


    /* =========================
       VERIFICATION TASKS
    ========================= */

    $("verificationTasks").innerHTML =
      (d.verification_tasks || []).map(x => `
        <div class="task">
          <b>${x.capability}</b>

          <p>
            ${x.task}
          </p>

          <small>
            ${x.why || ""}
          </small>
        </div>
      `).join("")
      || "No verification task recommended.";


    /* =========================
       LEARNING ACTIONS
    ========================= */

    $("learningCards").innerHTML =
      (d.learning_actions || []).map(x => `
        <div class="card">
          <b>${x.capability}</b>

          <p>
            ${x.action}
          </p>

          <small>
            ${x.learning_title || ""}
          </small>
        </div>
      `).join("")
      || "No learning action recommended.";


    /* =========================
       HUMAN REVIEW
    ========================= */

    $("human").innerHTML = `
      <b>Human review required.</b>
      ${d.human_review ||
        "Review evidence and verification before any decision."}
    `;


    /* Scroll to capability result */

    setTimeout(() => {
      $("capability").scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }, 300);


  } catch (e) {

    console.error("Analysis error:", e);

    $("status").classList.add("error");

    $("status").textContent =
      "⚠ " + e.message;

    renderAgents();

  } finally {

    btn.disabled = false;

  }
}


/* =========================
   WRITE VERIFIED EVIDENCE
   TO MOCK SAP
========================= */

async function updateSAP() {

  try {

    const personId =
      $("personId").value.trim();

    const capability =
      $("verifyCapability").value.trim();

    const evidence =
      $("verifyEvidence").value.trim();


    if (!personId || !capability || !evidence) {

      $("writeResult").textContent =
        "⚠ Please fill Person ID, Capability and Evidence.";

      return;
    }


    const r = await fetch(
      "/api/sap/verify",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          person_id: personId,
          capability: capability,
          status: "Verified",
          evidence: evidence
        })
      }
    );


    const d = await r.json();


    if (!r.ok) {
      throw new Error(
        d.error || "Update failed"
      );
    }


    $("writeResult").textContent =
      d.success
        ? `✓ Evidence verified and written to Mock SAP • Event ${d.event.event_id}`
        : "Update failed";


    /* Reload SAP counters */

    loadSAP();


  } catch (e) {

    console.error("SAP verification error:", e);

    $("writeResult").textContent =
      "⚠ " + e.message;
  }
}