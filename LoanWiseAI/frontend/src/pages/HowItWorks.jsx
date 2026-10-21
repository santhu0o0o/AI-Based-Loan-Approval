import { motion, useReducedMotion } from 'framer-motion';
import { ArrowRight, BadgeCheck, Brain, ClipboardList, RefreshCw, ServerCrash, ShieldCheck, Stamp } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { Disclaimer, PageHead, Skeleton } from '../components/bits.jsx';
import { groupIN, niceDate } from '../lib/format.js';

const FLOW = [
  { icon: ClipboardList, title: 'You answer', text: 'Your 11 answers go in.' },
  { icon: ShieldCheck, title: 'We check them', text: 'Missing or odd numbers are fixed or flagged.' },
  { icon: Brain, title: 'The model decides', text: 'It compares you with 614 past loans.' },
  { icon: Stamp, title: 'You get an answer', text: 'Likely yes or no, plus the reasons.' },
];

// Model output names -> plain English.
const FEATURE_WORDS = [
  [/credit/i, 'Paid past loans on time'],
  [/total.?income|income.?total/i, 'Total family income'],
  [/emi|installment/i, 'Monthly payment size'],
  [/ratio|loan.?to|lti|dti/i, 'Loan compared to income'],
  [/coapplicant/i, 'Helper’s income'],
  [/applicant.?income|^income/i, 'Your income'],
  [/loan.?amount|amount/i, 'How much you borrow'],
  [/term/i, 'How many years to repay'],
  [/property|area|urban|rural/i, 'Where the house is'],
  [/married/i, 'Married or not'],
  [/dependents/i, 'People who depend on you'],
  [/education|graduate/i, 'College degree'],
  [/self.?employed/i, 'Salary or own business'],
  [/gender|male|female/i, 'Man or woman'],
];
const featureWords = (f) => FEATURE_WORDS.find(([re]) => re.test(f))?.[1] || String(f).replace(/_/g, ' ');

const METRICS = {
  accuracy: { label: 'Accuracy', help: 'Out of every 100 past loans it had not seen before, how many it got right.' },
  f1: { label: 'F1 score', help: 'A stricter score that also checks it doesn’t just say “yes” to everyone.' },
};

function FlowDiagram() {
  const reduce = useReducedMotion();
  return (
    <ol className="flow" aria-label="How your answers become a result">
      {FLOW.map(({ icon: Icon, title, text }, i) => (
        <li key={title} className="flow-node">
          <motion.span
            className="flow-icon"
            aria-hidden="true"
            initial={reduce ? false : { scale: 0.6, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true, amount: 0.6 }}
            transition={{ delay: i * 0.35, type: 'spring', stiffness: 300, damping: 18 }}
          >
            <Icon size={30} />
          </motion.span>
          <div>
            <h3>
              <span className="flow-num">{i + 1}.</span> {title}
            </h3>
            <p>{text}</p>
          </div>
          {i < FLOW.length - 1 && (
            <svg className="flow-link" viewBox="0 0 100 12" preserveAspectRatio="none" aria-hidden="true">
              <line x1="0" y1="6" x2="100" y2="6" className="flow-line" />
              {!reduce && (
                <circle r="4" cy="6" className="flow-dot">
                  <animate attributeName="cx" from="0" to="100" dur="1.8s" begin={`${i * 0.35}s`} repeatCount="indefinite" />
                </circle>
              )}
            </svg>
          )}
        </li>
      ))}
    </ol>
  );
}

function ModelChart({ models, chosen }) {
  const [metric, setMetric] = useState('accuracy');
  const [hover, setHover] = useState(null);
  const reduce = useReducedMotion();
  const rows = [...models].sort((a, b) => (b[metric] ?? 0) - (a[metric] ?? 0));
  return (
    <div className="chart-card">
      <div className="chart-head">
        <div>
          <h3>We tested {models.length} different models</h3>
          <p className="muted">{METRICS[metric].help}</p>
        </div>
        <div className="seg" role="radiogroup" aria-label="Which score to show">
          {Object.entries(METRICS).map(([k, m]) => (
            <label key={k} className={`seg-opt${metric === k ? ' is-on' : ''}`}>
              <input type="radio" name="metric" value={k} checked={metric === k} onChange={() => setMetric(k)} />
              {m.label}
            </label>
          ))}
        </div>
      </div>
      <ul className="bars" aria-label={`${METRICS[metric].label} of each model`}>
        {rows.map((m) => {
          const v = Number(m[metric]) || 0;
          const isChosen = m.name === chosen;
          return (
            <li
              key={m.name}
              className={`bar-row${isChosen ? ' is-chosen' : ''}`}
              onMouseEnter={() => setHover(m.name)}
              onMouseLeave={() => setHover(null)}
            >
              <span className="bar-name">
                {m.name}
                {isChosen && (
                  <span className="chosen-badge">
                    <BadgeCheck size={16} aria-hidden="true" /> We use this one
                  </span>
                )}
              </span>
              <span className="bar-track">
                <motion.span
                  className="bar-fill"
                  initial={reduce ? false : { width: 0 }}
                  animate={{ width: `${Math.max(2, v * 100)}%` }}
                  transition={{ duration: 0.8, ease: [0.2, 0.8, 0.2, 1] }}
                />
                {hover === m.name && (
                  <span className="bar-tip" role="tooltip">
                    Accuracy {Math.round((m.accuracy ?? 0) * 100)}%, F1 {Math.round((m.f1 ?? 0) * 100)}%
                    {m.cv_accuracy_mean != null && `, average when re-tested ${Math.round(m.cv_accuracy_mean * 100)}%`}
                  </span>
                )}
              </span>
              <span className="bar-value">{Math.round(v * 100)}%</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function Factors({ items }) {
  const reduce = useReducedMotion();
  const top = [...items].sort((a, b) => b.importance - a.importance).slice(0, 6);
  const max = Math.max(...top.map((t) => t.importance), 0.0001);
  return (
    <div className="chart-card">
      <h3>What matters most to the model</h3>
      <p className="muted">Longer bar means that answer changes the result more.</p>
      <ul className="bars factors">
        {top.map((f, i) => (
          <li key={f.feature} className="bar-row" title={`${f.feature}: ${(f.importance * 100).toFixed(1)}%`}>
            <span className="bar-name">{featureWords(f.feature)}</span>
            <span className="bar-track">
              <motion.span
                className="bar-fill bar-fill-ink"
                initial={reduce ? false : { width: 0 }}
                whileInView={{ width: `${(f.importance / max) * 100}%` }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.06, duration: 0.7 }}
              />
            </span>
            <span className="bar-value">{Math.round(f.importance * 100)}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function HowItWorks() {
  const [state, setState] = useState({ status: 'loading' });
  const loadInfo = useCallback(async () => {
    setState({ status: 'loading' });
    try {
      const info = await api.modelInfo();
      setState({ status: 'ready', info });
    } catch (err) {
      setState({ status: 'error', message: err.message });
    }
  }, []);
  useEffect(() => {
    loadInfo();
  }, [loadInfo]);

  const info = state.info;
  const models = Array.isArray(info?.models) ? info.models : [];
  const ds = info?.dataset;

  return (
    <div className="wrap">
      <PageHead title="How LoanWise decides">
        <p>
          We taught a computer program, called a <strong>model</strong>, by showing it hundreds of old loan applications and
          whether each one got a yes or a no. Now it spots the same patterns in your answers.
        </p>
      </PageHead>

      <section aria-labelledby="flow-title" className="section">
        <h2 id="flow-title" className="section-title">
          From your answers to your result
        </h2>
        <FlowDiagram />
      </section>

      <section aria-labelledby="model-title" className="section">
        <h2 id="model-title" className="section-title">
          The model behind it
        </h2>
        {state.status === 'loading' && (
          <div className="chart-grid">
            <div className="chart-card"><Skeleton lines={5} /></div>
            <div className="chart-card"><Skeleton lines={5} /></div>
          </div>
        )}
        {state.status === 'error' && (
          <div className="notice">
            <span className="notice-icon" aria-hidden="true">
              <ServerCrash size={28} />
            </span>
            <div>
              <p className="notice-title">The model details aren&rsquo;t ready yet</p>
              <p>{state.message} The explanation above still applies.</p>
            </div>
            <button type="button" className="btn btn-ghost" onClick={loadInfo}>
              <RefreshCw size={20} aria-hidden="true" /> Try again
            </button>
          </div>
        )}
        {state.status === 'ready' && (
          <>
            {ds && (
              <div className="dataset">
                <p>
                  It learned from <strong>{groupIN(ds.rows)}</strong> past loan applications.
                </p>
                <div className="split" role="img" aria-label={`${ds.approved} were approved and ${ds.rejected} were not`}>
                  <span className="split-yes" style={{ flexGrow: ds.approved }}>
                    {groupIN(ds.approved)} got a yes
                  </span>
                  <span className="split-no" style={{ flexGrow: ds.rejected }}>
                    {groupIN(ds.rejected)} got a no
                  </span>
                </div>
              </div>
            )}
            <div className="chart-grid">
              {models.length > 0 && <ModelChart models={models} chosen={info.chosen_model} />}
              {Array.isArray(info.feature_importance) && info.feature_importance.length > 0 && <Factors items={info.feature_importance} />}
            </div>
            {info.trained_at && <p className="muted small">Model last trained on {niceDate(info.trained_at)}.</p>}
          </>
        )}
      </section>

      <section className="section cta-band">
        <h2>Ready to try it?</h2>
        <Link to="/check" className="btn btn-primary btn-xl">
          Check my loan chances
          <ArrowRight size={24} aria-hidden="true" />
        </Link>
      </section>
      <Disclaimer compact />
    </div>
  );
}
