// Same-origin API when deployed; localhost API when using the optional local frontend server.
const A =
    location.hostname === "localhost" && location.port === "5173"
      ? "http://localhost:3001/api"
      : "/api",
  S = {
    step: 1,
    values: {},
    uploads: {},
    card: null,
    t: null,
    user: JSON.parse(localStorage.getItem("startupready-user") || "null"),
  };
const steps = [
  [
    "Startup overview",
    "GETTING STARTED",
    "Build the context for every funding-readiness insight.",
    "Your story should explain what you do, for whom and why it matters.",
    [
      [
        "Startup snapshot",
        [
          ["startupName", "Startup name", "text", "Acme Labs"],
          ["industry", "Industry", "text", "Climate tech"],
        ],
      ],
      [
        "Business summary",
        [
          [
            "summary",
            "One-sentence description",
            "textarea",
            "What you do, for whom and why",
            1,
          ],
        ],
      ],
    ],
  ],
  [
    "Problem & solution validation",
    "VALIDATION",
    "Show that the problem is painful and your solution is credible.",
    "Evidence from customer conversations is the strongest early signal.",
    [
      [
        "Problem",
        [
          [
            "problem",
            "What problem are you solving?",
            "textarea",
            "Describe the customer pain",
            1,
          ],
          ["problemCustomer", "Who experiences it?", "text", "Primary customer"],
        ],
      ],
      [
        "Solution & proof",
        [
          [
            "solution",
            "Explain your solution",
            "textarea",
            "How it solves the problem",
            1,
          ],
        ],
      ],
    ],
  ],
  [
    "Market opportunity",
    "MARKET",
    "Size the opportunity and map the competitive landscape.",
    "Investors want a defined buyer and a credible path to a meaningful market.",
    [
      [
        "Market details",
        [
          ["customer", "Customer segment", "text", "Independent retailers"],
          ["tam", "TAM", "text", "$2B"],
        ],
      ],
      [
        "Competition",
        [
          [
            "competitors",
            "Top competitors",
            "textarea",
            "Competitors and alternatives",
            1,
          ],
        ],
      ],
    ],
  ],
  [
    "Product readiness",
    "PRODUCT",
    "Assess product maturity, usability and customer evidence.",
    "Product readiness means users can get a clear outcome today.",
    [
      [
        "Product",
        [
          [
            "productStatus",
            "Product status",
            "choice",
            ["Idea", "Prototype", "MVP", "Beta", "Live product"],
          ],
          ["features", "Core features", "textarea", "What users can do", 1],
          ["users", "Active users", "number", "0"],
        ],
      ],
    ],
  ],
  [
    "Technology assessment",
    "TECHNOLOGY",
    "Evaluate the platform supporting secure scale.",
    "This reveals strengths and investment needed for scalable delivery.",
    [
      [
        "Architecture",
        [
          [
            "stack",
            "Technology stack",
            "textarea",
            "Languages, cloud and databases",
            1,
          ],
          [
            "security",
            "Security framework",
            "textarea",
            "Authentication, encryption, compliance",
            1,
          ],
        ],
      ],
    ],
  ],
  [
    "Business model",
    "BUSINESS",
    "Connect your customer value to a repeatable revenue engine.",
    "Clear unit economics make growth more credible.",
    [
      [
        "Revenue & economics",
        [
          [
            "revenueModel",
            "Revenue model",
            "choice",
            [
              "Subscription",
              "Licensing",
              "Marketplace",
              "Transaction fee",
              "Services",
            ],
          ],
          [
            "pricing",
            "Pricing strategy",
            "textarea",
            "Packages and price points",
            1,
          ],
          ["ltv", "Customer lifetime value", "number", "0"],
        ],
      ],
    ],
  ],
  [
    "Team assessment",
    "TEAM",
    "Show the capabilities behind execution.",
    "Strong teams are complementary and know their gaps.",
    [
      [
        "Leadership & team",
        [
          [
            "founders",
            "Founder experience",
            "textarea",
            "Relevant track record",
            1,
          ],
          [
            "team",
            "Current team",
            "textarea",
            "Technology, sales and operations",
            1,
          ],
        ],
      ],
    ],
  ],
  [
    "Financial readiness",
    "FINANCIALS",
    "Share the economics, runway and plan.",
    "Even pre-revenue teams should command the assumptions behind the plan.",
    [
      [
        "Metrics & planning",
        [
          ["revenue", "Annual revenue", "number", "0"],
          ["burn", "Monthly burn rate", "number", "0"],
          ["runway", "Runway (months)", "number", "0"],
        ],
      ],
    ],
  ],
  [
    "Legal & compliance",
    "FOUNDATIONS",
    "Identify legal, IP and compliance readiness.",
    "Clean basics reduce investor diligence friction.",
    [
      [
        "Legal checklist",
        [
          [
            "incorporated",
            "Incorporated",
            "choice",
            ["No", "In progress", "Yes"],
          ],
          ["privacy", "Privacy policy", "choice", ["No", "Draft", "Published"]],
        ],
      ],
    ],
  ],
  [
    "Sales & go-to-market",
    "GO TO MARKET",
    "Explain how you find, convert and retain customers.",
    "A GTM plan connects channel, buyer, sales motion and economics.",
    [
      [
        "GTM",
        [
          [
            "channels",
            "Sales channels",
            "textarea",
            "Direct, partners or self-serve",
            1,
          ],
          ["salesCycle", "Sales cycle", "text", "Typical close time"],
          ["conversion", "Conversion rate (%)", "number", "0"],
        ],
      ],
    ],
  ],
  [
    "Traction & growth",
    "MOMENTUM",
    "Capture evidence that the business is moving forward.",
    "Traction may be revenue, usage, partnerships or external validation.",
    [
      [
        "Metrics",
        [
          ["customers", "Customers", "number", "0"],
          ["mrr", "MRR", "number", "0"],
          ["growth", "Monthly growth (%)", "number", "0"],
        ],
      ],
    ],
  ],
  [
    "ESG & impact",
    "IMPACT",
    "Describe how you build responsibly and create impact.",
    "Responsible growth is a useful signal of governance and resilience.",
    [
      [
        "Impact",
        [
          [
            "environment",
            "Environmental impact",
            "textarea",
            "Measure positive and negative impact",
            1,
          ],
          ["social", "Social impact", "textarea", "Who benefits and how", 1],
        ],
      ],
    ],
  ],
  [
    "Investment readiness",
    "FUNDING",
    "Make the funding case and prepare for diligence.",
    "A potential investor needs a clear reason to engage and material to evaluate.",
    [
      [
        "Funding",
        [
          ["funding", "Funding required", "number", "0"],
          [
            "useOfFunds",
            "Use of funds",
            "textarea",
            "Milestones and allocation",
            1,
          ],
          ["pitchDeck", "Pitch deck", "choice", ["No", "In progress", "Ready"]],
        ],
      ],
    ],
  ],
  [
    "Risk assessment",
    "RISK",
    "Name meaningful risks and the controls that reduce them.",
    "Mature teams assign owners and practical contingency plans.",
    [
      [
        "Risks & mitigation",
        [
          [
            "marketRisk",
            "Market and competition risk",
            "textarea",
            "Risk, likelihood and impact",
            1,
          ],
          [
            "financialRisk",
            "Financial and operational risk",
            "textarea",
            "Risk, likelihood and impact",
            1,
          ],
          [
            "controls",
            "Existing controls and contingency plan",
            "textarea",
            "Owners and mitigations",
            1,
          ],
        ],
      ],
    ],
  ],
  [
    "Final evaluation",
    "YOUR SCORECARD",
    "Review your readiness score and priorities.",
    "Use this as a decision aid, then return to strengthen evidence.",
    [],
  ],
];
const $ = (x) => document.querySelector(x),
  e = (x) =>
    String(x || "").replace(
      /[&<>"]/g,
      (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c],
    );
function requiredFields(stepNumber) {
  return (steps[stepNumber - 1]?.[4] || [])
    .flatMap((section) => section[1])
    .filter((field) => field[2] !== "upload");
}
function missingFields(stepNumber) {
  return requiredFields(stepNumber).filter(
    (field) => !String(S.values[field[0]] || "").trim(),
  );
}
function availableStepCount() {
  for (let step = 1; step < 15; step += 1) {
    if (missingFields(step).length) return step;
  }
  return 15;
}
function nav() {
  $("#nav").innerHTML = steps
    .slice(0, availableStepCount())
    .map(
      (x, i) =>
        `<button class="${S.step == i + 1 ? "active" : ""} ${i < 14 && !missingFields(i + 1).length ? "done" : ""}" onclick="go(${i + 1})">${i + 1}. ${x[0]}</button>`,
    )
    .join("");
}
function field(f) {
  let [k, l, t, p, full] = f,
    v = S.values[k] || "",
    c = full ? "field full" : "field";
  if (t === "choice")
    return `<div class="${c}"><label>${l} <span class="required-mark">*</span></label><div class="chips">${p.map((q) => `<label><input type="radio" name="${k}" value="${q}" ${v === q ? "checked" : ""} required><span>${q}</span></label>`).join("")}</div></div>`;
  if (t === "upload")
    return `<div class="${c}"><label>${l}</label><label class="upload">⇧ Upload supporting document<br><small>${p}</small><input type="file" name="${k}"></label><small>${S.uploads[k] ? "Attached: " + e(S.uploads[k]) : ""}</small></div>`;
  return `<div class="${c}"><label>${l} <span class="required-mark">*</span></label><${t === "textarea" ? "textarea" : "input"} name="${k}" ${t === "textarea" ? "" : `type="${t}"`} placeholder="${p}" required>${t === "textarea" ? e(v) : ""}</${t === "textarea" ? "textarea" : "input"}></div>`;
}
function render() {
  if (!S.user) return renderAuth("login");
  if (S.step === 15) return final();
  let x = steps[S.step - 1],
    pc = Math.round(((S.step - 1) / 14) * 100);
  $("#app").innerHTML =
    `<div><div class="crumb">Step ${S.step} of 15 · ~ ${40 - (S.step - 1) * 2} min left</div><div class="progress"><i style="width:${pc}%"></i></div><div class="heading"><div><div class="tag">${x[1]}</div><h1>${x[0]}</h1><p>${x[2]}</p></div><button class="help" onclick="$('.hint').style.display=$('.hint').style.display==='block'?'none':'block'">? Why are we asking?</button></div><div class="hint">${x[3]}</div><p class="required-note"><span class="required-mark">*</span> Required fields must be completed before you continue.</p>${S.validationError ? `<div class="validation-error" role="alert">${e(S.validationError)}</div>` : ""}<form id="form">${x[4].map((a) => `<div class="formbox"><h2>${a[0]}</h2><p>Share what you know today - you can refine it anytime.</p><div class="fields">${a[1].map(field).join("")}</div></div>`).join("")}</form><div class="actions"><button class="btn" onclick="go(Math.max(1,S.step-1))">Back</button><button class="btn primary" onclick="go(S.step+1)">Save & continue →</button></div></div>`;
  document
    .querySelectorAll("#form input,#form textarea")
    .forEach((q) => {
      q.oninput = change;
      q.onchange = change;
    });
  document
    .querySelectorAll("input[type=file]")
    .forEach((q) => (q.onchange = change));
  $("#sideP").textContent = pc + "% complete";
  $("#sideBar").style.width = pc + "%";
  nav();
  setUserUI();
}
function change(q) {
  q = q.target;
  if (q.type === "file") S.uploads[q.name] = q.files[0]?.name || "";
  else if (q.type !== "radio" || q.checked) S.values[q.name] = q.value;
  clearTimeout(S.t);
  S.t = setTimeout(save, 450);
}
async function save() {
  try {
    $("#saved").textContent = "● Saving…";
    let r = await fetch(A + "/assessment", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ values: S.values, uploads: S.uploads }),
      }),
      d = await r.json();
    S.card = d.scorecard;
    $("#saved").textContent = "● All changes saved";
    nav();
  } catch {
    $("#saved").textContent = "● Backend not connected";
  }
}
function setMobileNav(open) {
  $("#sidebar").classList.toggle("open", open);
  $("#navBackdrop").classList.toggle("open", open);
  $("#menuToggle").setAttribute("aria-expanded", String(open));
}
async function go(n) {
  let target = Math.max(1, Math.min(15, n));
  if (target > S.step) {
    for (let step = S.step; step < target; step += 1) {
      let missing = missingFields(step);
      if (missing.length) {
        S.step = step;
        S.validationError = `Complete all required fields before continuing. Missing: ${missing.map((field) => field[1]).join(", ")}.`;
        setMobileNav(false);
        render();
        toast("Complete the required fields to continue.");
        return;
      }
    }
  }
  S.validationError = "";
  setMobileNav(false);
  await save();
  S.step = target;
  scrollTo(0, 0);
  render();
}
function final() {
  let c = S.card || {
    overall: 35,
    verdict: "Foundation Stage",
    scores: [],
    recommendations: [],
  };
  $("#app").innerHTML =
    `<div class="final"><div class="hero"><div class="tag" style="color:#ddd8ff">STARTUPREADY SCORECARD</div><h1>${e(S.values.startupName || "Your startup")} is ${c.verdict}</h1><p>A focused plan for your next investor conversation.</p><div class="big">${c.overall}<small>/100</small></div></div><p><a class="btn primary" href="${A}/report">↓ Download executive report</a></p><div class="grid">${c.scores.map((x) => `<div class="card"><small>${x.label}</small><b>${x.score}/100</b><div class="bar"><i style="width:${x.score}%"></i></div></div>`).join("")}</div><div class="recommend"><h2>Top improvement recommendations</h2><ul>${c.recommendations.map((x) => `<li><b>[${x.priority}] ${x.area}:</b> ${x.improvement} ${x.impact} · ${x.owner}</li>`).join("")}</ul><h2>SWOT summary</h2><p>Strengths: your highest-scoring evidence. Weaknesses: missing detail. Opportunities: recommendations above. Threats: the documented risk areas.</p><button class="btn" onclick="go(1)">Return to assessment</button></div></div>`;
  nav();
}
function toast(x) {
  let t = $("#toast");
  t.textContent = x;
  t.style.display = "block";
  setTimeout(() => (t.style.display = "none"), 2200);
}
function renderAuth(mode) {
  $("#sidebar").classList.remove("open");
  $("#navBackdrop").classList.remove("open");
  $("#app").innerHTML =
    `<div class="auth-wrap"><section class="auth-card"><div class="auth-brand">✦ StartupReady</div><h1>${mode === "login" ? "Welcome back" : "Create your account"}</h1><p>${mode === "login" ? "Sign in to continue building your funding-readiness profile." : "Start your guided startup evaluation in a few seconds."}</p><form id="authForm">${mode === "signup" ? '<label>Full name<input name="name" placeholder="Your name" required></label>' : ""}<label>Email address<input name="email" type="email" placeholder="you@example.com" required></label><label>Password<input name="password" type="password" placeholder="At least 8 characters" required></label><button class="btn primary auth-submit">${mode === "login" ? "Sign in" : "Create account"}</button><div id="authError" class="auth-error"></div></form><p class="auth-switch">${mode === "login" ? "New to StartupReady?" : "Already have an account?"} <button type="button" onclick="renderAuth('${mode === "login" ? "signup" : "login"}')">${mode === "login" ? "Create an account" : "Sign in"}</button></p></section></div>`;
  $("#authForm").onsubmit = (e) => submitAuth(e, mode);
}
async function submitAuth(event, mode) {
  event.preventDefault();
  let form = new FormData(event.target),
    payload = Object.fromEntries(form.entries()),
    error = $("#authError");
  error.textContent = "";
  if (!String(payload.email || "").trim() || !String(payload.password || "")) {
    error.textContent = "Enter your email address and password.";
    return;
  }
  if (mode === "signup" && !String(payload.name || "").trim()) {
    error.textContent = "Enter your full name.";
    return;
  }
  if (mode === "signup" && String(payload.password).length < 8) {
    error.textContent = "Password must contain at least 8 characters.";
    return;
  }
  try {
    let r = await fetch(A + "/auth/" + mode, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
      d = await r.json();
    if (!r.ok) throw Error(d.error || "Unable to continue.");
    S.user = d.user;
    localStorage.setItem("startupready-user", JSON.stringify(d.user));
    render();
  } catch (err) {
    error.textContent = err.message;
  }
}
function setUserUI() {
  if (!S.user) return;
  $("#profile").textContent = S.user.name
    .split(" ")
    .map((x) => x[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  $("#profile").title = `${S.user.name} - click to sign out`;
  $("#profile").onclick = logout;
}
function logout() {
  localStorage.removeItem("startupready-user");
  S.user = null;
  render();
}
$("#menuToggle").onclick = () =>
  setMobileNav(!$("#sidebar").classList.contains("open"));
$("#navBackdrop").onclick = () => setMobileNav(false);
(async () => {
  try {
    let d = await (await fetch(A + "/assessment")).json();
    S.values = d.values || {};
    S.uploads = d.uploads || {};
    S.card = await (await fetch(A + "/scorecard")).json();
  } catch {}
  render();
})();
