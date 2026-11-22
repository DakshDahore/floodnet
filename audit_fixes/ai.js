// ai.js - provider chain: Groq -> Gemini -> deterministic rules.
// Fixes vs original: keys only from env, model names from env (no hardcoded labels),
// reported engine is the one that ACTUALLY answered, hard timeouts, key in a header
// (not the URL), numeric-only facts (no prompt injection), and the LLM can never
// downgrade the physics-derived alert level.
const LEVELS = ["GREEN", "AMBER", "RED"];

// PLACEHOLDER policy thresholds - must be set by the responsible flood authority.
export function deterministicAlert({ depthCm, chokePct }) {
  if (depthCm >= 30 || (depthCm >= 15 && chokePct >= 50)) return "RED";
  if (depthCm >= 5 || chokePct >= 30) return "AMBER";
  return "GREEN";
}

function deterministicBulletin(level, f) {
  const t = { GREEN: "No flood action required.", AMBER: "Flood watch: stay alert and avoid low-lying roads.", RED: "Flood warning: move to higher ground and follow official instructions." };
  return `${t[level]} (modelled depth ${f.depthCm} cm, drainage choke ${f.chokePct}%).`;
}

const num = (x) => (Number.isFinite(Number(x)) ? Number(x) : 0);

function buildPrompt(f, level) {
  return `Return ONLY JSON: {"alert_level":"GREEN|AMBER|RED","bulletin":"<=60 words"}. ` +
    `Facts: depth_cm=${f.depthCm}, drainage_choke_pct=${f.chokePct}, eta_min=${f.etaMin}. Required minimum alert_level: ${level}.`;
}

function parseValidated(text, floor) {
  const m = String(text || "").match(/\{[\s\S]*\}/);
  if (!m) return null;
  let o; try { o = JSON.parse(m[0]); } catch { return null; }
  if (!LEVELS.includes(o.alert_level) || typeof o.bulletin !== "string") return null;
  if (LEVELS.indexOf(o.alert_level) < LEVELS.indexOf(floor)) return null; // never downgrade physics
  return { alert_level: o.alert_level, bulletin: o.bulletin.slice(0, 500) };
}

async function timed(fn, ms) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), ms);
  try { return await fn(c.signal); } finally { clearTimeout(t); }
}

const providers = (env) => [
  env.GROQ_API_KEY && env.GROQ_MODEL && {
    name: "groq", model: env.GROQ_MODEL,
    async call(prompt, signal) {
      const r = await fetch("https://api.groq.com/openai/v1/chat/completions", {
        method: "POST", signal,
        headers: { "content-type": "application/json", authorization: `Bearer ${env.GROQ_API_KEY}` },
        body: JSON.stringify({ model: env.GROQ_MODEL, temperature: 0, max_tokens: 200, messages: [{ role: "user", content: prompt }] }),
      });
      if (!r.ok) throw new Error(`groq ${r.status}`);
      return (await r.json()).choices?.[0]?.message?.content;
    },
  },
  env.GEMINI_API_KEY && env.GEMINI_MODEL && {
    name: "gemini", model: env.GEMINI_MODEL,
    async call(prompt, signal) {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(env.GEMINI_MODEL)}:generateContent`, {
        method: "POST", signal,
        headers: { "content-type": "application/json", "x-goog-api-key": env.GEMINI_API_KEY },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0, maxOutputTokens: 200 } }),
      });
      if (!r.ok) throw new Error(`gemini ${r.status}`);
      return (await r.json()).candidates?.[0]?.content?.parts?.[0]?.text;
    },
  },
].filter(Boolean);

export async function runTacticalReasoning(env, rawFacts, { timeoutMs = 4000 } = {}) {
  const f = { depthCm: num(rawFacts.depthCm), chokePct: num(rawFacts.chokePct), etaMin: num(rawFacts.etaMin) };
  const floor = deterministicAlert(f);
  const attempts = [];
  for (const p of providers(env)) {
    try {
      const text = await timed((signal) => p.call(buildPrompt(f, floor), signal), timeoutMs);
      const ok = parseValidated(text, floor);
      if (ok) return { ...ok, engine: `${p.name}/${p.model}`, attempts };
      attempts.push({ provider: p.name, error: "invalid_or_downgraded_output" });
    } catch (e) {
      attempts.push({ provider: p.name, error: String(e.message || e).slice(0, 80) });
    }
  }
  return { alert_level: floor, bulletin: deterministicBulletin(floor, f), engine: "deterministic-rules", attempts };
}
