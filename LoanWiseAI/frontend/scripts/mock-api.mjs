// Throwaway mock of the LoanWise API (see docs/API.md) for UI work without Flask.
// Also serves frontend/dist with SPA fallback, so `npm run build && npm run mock`
// gives a full app at http://localhost:5055.
//   MOCK_PORT=5055  MOCK_NO_MODEL=1 (model-info fails)  MOCK_EMPTY=1 (empty history)
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const PORT = Number(process.env.MOCK_PORT || 5055);
const dist = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'dist');
const TERMS = [12, 36, 60, 84, 120, 180, 240, 300, 360, 480];

let nextId = 1;
let history = process.env.MOCK_EMPTY
  ? []
  : [
      { approved: true, conf: 0.86, inputs: { applicant_income: 52000, coapplicant_income: 18000, loan_amount: 2500000, loan_term: 240, credit_history: 'good' } },
      { approved: false, conf: 0.71, inputs: { applicant_income: 14500, coapplicant_income: 0, loan_amount: 1800000, loan_term: 360, credit_history: 'bad' } },
      { approved: true, conf: 0.64, inputs: { applicant_income: 31000, coapplicant_income: 0, loan_amount: 600000, loan_term: 120, credit_history: 'good' } },
    ].map((h, i) => ({
      id: nextId++,
      created_at: new Date(Date.now() - (i + 1) * 86400000 * 1.7).toISOString(),
      inputs: { gender: 'Male', married: 'Yes', dependents: '1', education: 'Graduate', self_employed: 'No', property_area: 'Semiurban', ...h.inputs },
      approved: h.approved,
      verdict: h.approved ? 'Likely Approved' : 'Likely Rejected',
      confidence: h.conf,
    }));

const MODEL_INFO = {
  chosen_model: 'Random Forest',
  selection_metric: 'f1',
  models: [
    { name: 'Logistic Regression', accuracy: 0.805, precision: 0.79, recall: 0.97, f1: 0.871, cv_accuracy_mean: 0.809, cv_accuracy_std: 0.02 },
    { name: 'Decision Tree', accuracy: 0.723, precision: 0.79, recall: 0.81, f1: 0.8, cv_accuracy_mean: 0.71, cv_accuracy_std: 0.03 },
    { name: 'Random Forest', accuracy: 0.821, precision: 0.81, recall: 0.97, f1: 0.883, cv_accuracy_mean: 0.805, cv_accuracy_std: 0.02 },
    { name: 'Gradient Boosting', accuracy: 0.789, precision: 0.8, recall: 0.92, f1: 0.856, cv_accuracy_mean: 0.79, cv_accuracy_std: 0.025 },
    { name: 'K-Nearest Neighbours', accuracy: 0.74, precision: 0.76, recall: 0.9, f1: 0.824, cv_accuracy_mean: 0.73, cv_accuracy_std: 0.03 },
  ],
  feature_importance: [
    { feature: 'Credit_History', importance: 0.29 },
    { feature: 'Total_Income_log', importance: 0.17 },
    { feature: 'EMI', importance: 0.13 },
    { feature: 'LoanAmount_log', importance: 0.12 },
    { feature: 'Loan_to_Income', importance: 0.1 },
    { feature: 'Property_Area', importance: 0.05 },
    { feature: 'Married', importance: 0.03 },
  ],
  dataset: { rows: 614, approved: 422, rejected: 192 },
  trained_at: '2026-10-20T17:40:00Z',
};

const SAMPLES = [
  { gender: 'Male', married: 'Yes', dependents: '2', education: 'Graduate', self_employed: 'No', applicant_income: 4583, coapplicant_income: 1508, loan_amount: 128000, loan_term: 360, credit_history: 'good', property_area: 'Rural' },
  { gender: 'Female', married: 'No', dependents: '0', education: 'Not Graduate', self_employed: 'Yes', applicant_income: 3200, coapplicant_income: 0, loan_amount: 95000, loan_term: 180, credit_history: 'bad', property_area: 'Urban' },
];

function validate(b) {
  const e = {};
  const choice = (k, opts, msg) => !opts.includes(b[k]) && (e[k] = msg);
  choice('gender', ['Male', 'Female'], 'Please choose Man or Woman.');
  choice('married', ['Yes', 'No'], 'Please choose Yes or No.');
  choice('dependents', ['0', '1', '2', '3+'], 'Please choose how many people depend on you.');
  choice('education', ['Graduate', 'Not Graduate'], 'Please choose your education.');
  choice('self_employed', ['Yes', 'No'], 'Please choose how you earn.');
  choice('credit_history', ['good', 'bad'], 'Please answer the question about past loans.');
  choice('property_area', ['Urban', 'Semiurban', 'Rural'], 'Please choose where the house is.');
  const num = (k, lo, hi, msg) => (typeof b[k] !== 'number' || b[k] < lo || b[k] > hi) && (e[k] = msg);
  num('applicant_income', 0, 1e7, 'Please type your monthly income using numbers only, like 25000.');
  num('coapplicant_income', 0, 1e7, 'Please type a number between 0 and 1,00,00,000.');
  num('loan_amount', 1000, 1e7, 'The loan must be between ₹1,000 and ₹1,00,00,000.');
  if (!TERMS.includes(b.loan_term)) e.loan_term = 'Please choose how many years.';
  if (!e.applicant_income && !e.coapplicant_income && b.applicant_income + b.coapplicant_income <= 0)
    e.applicant_income = 'Someone has to earn money for a loan. Please type an income.';
  // Test hook: a loan of exactly ₹4,04,040 triggers a server-side error on that field.
  if (b.loan_amount === 404040) e.loan_amount = 'The server did not like this amount. Please type a different number.';
  return e;
}

function predict(b) {
  const income = b.applicant_income + b.coapplicant_income;
  const r = 0.09 / 12;
  const n = b.loan_term;
  const emi = (b.loan_amount * r * (1 + r) ** n) / ((1 + r) ** n - 1);
  const ratio = emi / Math.max(income, 1);
  let p = b.credit_history === 'good' ? 0.8 : 0.12;
  p -= Math.max(0, ratio - 0.4) * 0.8;
  if (b.property_area === 'Semiurban') p += 0.05;
  p = Math.max(0.03, Math.min(0.97, p));
  const approved = p >= 0.5;
  const confidence = approved ? p : 1 - p;
  const reasons = [];
  reasons.push(
    b.credit_history === 'good'
      ? { type: 'positive', text: 'You have paid past loans on time. This is the biggest thing banks look at.' }
      : { type: 'negative', text: 'Missed or late payments on past loans make banks worried. This matters most.' },
  );
  reasons.push(
    ratio < 0.4
      ? { type: 'positive', text: `The monthly payment is about ${Math.round(ratio * 100)}% of your family income, which is comfortable.` }
      : { type: 'negative', text: `The monthly payment would take about ${Math.round(ratio * 100)}% of your family income. That is a lot.` },
  );
  if (b.coapplicant_income > 0) reasons.push({ type: 'positive', text: 'A second income helps make the loan safer.' });
  if (b.property_area === 'Semiurban') reasons.push({ type: 'neutral', text: 'Houses near cities were approved a bit more often in the past.' });
  const warnings = b.applicant_income > 500000 ? ['Your income is very high for this kind of loan, so we double-checked it.'] : [];
  if (b.loan_amount < 10000) warnings.push('This is a very small loan. We still checked it, but banks may not offer home loans this small.');
  return {
    ok: true,
    approved,
    verdict: approved ? 'Likely Approved' : 'Likely Rejected',
    headline: approved ? 'Great news! Your loan is likely to be approved.' : 'Your loan may not be approved right now.',
    confidence: Number(confidence.toFixed(2)),
    confidence_label: confidence >= 0.75 ? 'High' : confidence >= 0.6 ? 'Medium' : 'Low',
    reasons,
    warnings,
    guardrail_applied: warnings.length > 0,
    emi_estimate: Number(emi.toFixed(0)),
    id: nextId,
  };
}

const send = (res, code, body) => {
  res.writeHead(code, { 'content-type': 'application/json' });
  res.end(JSON.stringify(body));
};

const TYPES = { '.js': 'text/javascript', '.css': 'text/css', '.html': 'text/html', '.svg': 'image/svg+xml', '.woff': 'font/woff', '.woff2': 'font/woff2' };

http
  .createServer(async (req, res) => {
    const url = new URL(req.url, 'http://x');
    const p = url.pathname;
    if (p.startsWith('/api/')) {
      await new Promise((r) => setTimeout(r, 250));
      if (p === '/api/health') return send(res, 200, { ok: true, model_loaded: true });
      if (p === '/api/sample') return send(res, 200, SAMPLES[Math.floor(Math.random() * SAMPLES.length)]);
      if (p === '/api/model-info') {
        if (process.env.MOCK_NO_MODEL) return send(res, 503, { ok: false, message: 'The model has not been trained yet.' });
        return send(res, 200, { ok: true, ...MODEL_INFO });
      }
      if (p === '/api/history' && req.method === 'GET') return send(res, 200, { ok: true, items: [...history].reverse().slice(0, Number(url.searchParams.get('limit') || 50)) });
      if (p === '/api/history' && req.method === 'DELETE') {
        history = [];
        return send(res, 200, { ok: true });
      }
      if (p === '/api/predict' && req.method === 'POST') {
        let raw = '';
        for await (const c of req) raw += c;
        let b;
        try {
          b = JSON.parse(raw);
        } catch {
          return send(res, 400, { ok: false, message: 'We could not read your answers. Please try again.' });
        }
        const errors = validate(b);
        if (Object.keys(errors).length) return send(res, 422, { ok: false, errors, message: 'Some answers need fixing. Look for the red boxes.' });
        const out = predict(b);
        history.push({ id: nextId++, created_at: new Date().toISOString(), inputs: b, approved: out.approved, verdict: out.verdict, confidence: out.confidence });
        return send(res, 200, out);
      }
      return send(res, 404, { ok: false, message: 'That page does not exist.' });
    }
    // static + SPA fallback
    let file = path.join(dist, decodeURIComponent(p));
    if (!file.startsWith(dist) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(dist, 'index.html');
    if (!fs.existsSync(file)) return send(res, 500, { ok: false, message: 'Run npm run build first.' });
    res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  })
  .listen(PORT, () => console.log(`Mock LoanWise API + dist on http://localhost:${PORT}`));
