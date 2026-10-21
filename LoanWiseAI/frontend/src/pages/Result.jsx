import { motion, useReducedMotion } from 'framer-motion';
import { ArrowRight, Calculator, ClipboardCheck, Info, PencilLine, RotateCcw, ThumbsDown, ThumbsUp, Wrench } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { EmptyArt, Petals, SproutArt, VerdictStamp } from '../components/art.jsx';
import { ConfidenceRing, Disclaimer, useCountUp } from '../components/bits.jsx';
import { groupIN, rupees, yearsLabel } from '../lib/format.js';
import { KEYS, load, remove } from '../lib/storage.js';

const CONF_WORDS = {
  High: 'We are quite sure about this answer.',
  Medium: 'We are fairly sure, but it could go either way.',
  Low: 'This one is close. Small changes could flip the answer.',
};

const REASON_ICON = { positive: ThumbsUp, negative: ThumbsDown, neutral: Info };
const REASON_WORD = { positive: 'Helps you', negative: 'Hurts your chances', neutral: 'Good to know' };

function Emi({ value, answers }) {
  const n = useCountUp(Math.round(Number(value) || 0), { delay: 0.6, duration: 1 });
  if (value == null || Number.isNaN(Number(value))) return null;
  return (
    <section className="result-emi" aria-labelledby="emi-title">
      <span className="emi-icon" aria-hidden="true">
        <Calculator size={26} />
      </span>
      <div>
        <h2 id="emi-title">Your monthly payment would be about</h2>
        <p className="emi-amount">
          ₹{groupIN(n)}
          <span> a month</span>
        </p>
        {answers?.loan_amount && answers?.loan_term && (
          <p className="emi-note">
            For a loan of {rupees(answers.loan_amount)} paid back over {yearsLabel(answers.loan_term)}. This is a rough guess. The
            bank&rsquo;s real interest rate will change it.
          </p>
        )}
      </div>
    </section>
  );
}

export default function Result() {
  const location = useLocation();
  const navigate = useNavigate();
  const reduce = useReducedMotion();
  const saved = location.state?.result ? location.state : load(KEYS.result);
  const result = saved?.result;
  const answers = saved?.answers;

  if (!result) {
    return (
      <div className="wrap narrow empty-state">
        <EmptyArt />
        <h1>No result to show yet</h1>
        <p>Answer the questions first, and your result will show up here.</p>
        <Link to="/check" className="btn btn-primary btn-xl">
          Check my loan chances
          <ArrowRight size={24} aria-hidden="true" />
        </Link>
      </div>
    );
  }

  const approved = !!result.approved;
  const tone = approved ? 'good' : 'soft';
  const label = result.confidence_label || (result.confidence >= 0.75 ? 'High' : result.confidence >= 0.6 ? 'Medium' : 'Low');
  const reasons = Array.isArray(result.reasons) ? result.reasons : [];
  const warnings = Array.isArray(result.warnings) ? result.warnings : [];
  const stampText = approved ? 'Likely approved' : 'Not likely yet';
  const headline =
    result.headline || (approved ? 'Great news! Your loan is likely to be approved.' : 'Your loan may not be approved right now.');

  const tryAgain = () => navigate('/check', { state: { step: 0 } });
  const fresh = () => {
    remove(KEYS.answers);
    remove(KEYS.step);
    navigate('/check', { state: { step: 0, fresh: Date.now() } });
  };

  const item = (i) => ({
    initial: reduce ? false : { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    transition: { delay: 0.9 + i * 0.08, duration: 0.35 },
  });

  return (
    <div className={`result result-${tone}`}>
      {approved && <Petals />}
      <div className="wrap result-grid">
        <motion.section
          className="slip"
          aria-labelledby="verdict"
          initial={reduce ? false : { opacity: 0, y: 16 }}
          animate={reduce ? {} : { opacity: 1, y: 0, x: [0, 0, -3, 3, -1, 0] }}
          transition={{ duration: 0.9, times: [0, 0.4, 0.5, 0.6, 0.7, 1] }}
        >
          <div className="slip-perf" aria-hidden="true" />
          <div className="slip-body">
            <p className="slip-kicker">Your result{result.id != null ? `, check number ${result.id}` : ''}</p>
            <div className="slip-stamp">
              <VerdictStamp approved={approved} label={stampText} />
            </div>
            <h1 id="verdict" className="slip-headline">
              {headline}
            </h1>
            {!approved && (
              <div className="slip-kind">
                <SproutArt />
                <p>
                  A &ldquo;no&rdquo; today is not a &ldquo;no&rdquo; forever. The reasons below show what you can change, like
                  borrowing a little less or adding someone&rsquo;s income.
                </p>
              </div>
            )}
            <div className="slip-sure">
              <ConfidenceRing value={result.confidence} label={label} tone={tone} />
              <div>
                <h2>How sure are we?</h2>
                <p className="sure-label">{label} confidence</p>
                <p>{CONF_WORDS[label] || CONF_WORDS.Medium}</p>
              </div>
            </div>
          </div>
        </motion.section>

        <div className="result-side">
          {reasons.length > 0 && (
            <section className="panel" aria-labelledby="why-title">
              <h2 id="why-title" className="panel-title">
                Why we said this
              </h2>
              <ul className="reasons">
                {reasons.map((r, i) => {
                  const type = REASON_ICON[r.type] ? r.type : 'neutral';
                  const Icon = REASON_ICON[type];
                  return (
                    <motion.li key={i} className={`reason reason-${type}`} {...item(i)}>
                      <span className="reason-icon" aria-hidden="true">
                        <Icon size={20} />
                      </span>
                      <span>
                        <span className="sr-only">{REASON_WORD[type]}: </span>
                        {r.text}
                      </span>
                    </motion.li>
                  );
                })}
              </ul>
            </section>
          )}

          {warnings.length > 0 && (
            <section className="panel panel-warn" aria-labelledby="fix-title">
              <h2 id="fix-title" className="panel-title">
                <Wrench size={22} aria-hidden="true" /> Things we fixed for you
              </h2>
              <ul className="warn-list">
                {warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </section>
          )}

          <Emi value={result.emi_estimate} answers={answers} />

          <div className="result-actions">
            <button type="button" className="btn btn-primary btn-lg" onClick={tryAgain}>
              <PencilLine size={22} aria-hidden="true" />
              Try again with changes
            </button>
            <button type="button" className="btn btn-ghost btn-lg" onClick={fresh}>
              <RotateCcw size={22} aria-hidden="true" />
              Start fresh
            </button>
          </div>
          <p className="result-history-link">
            <ClipboardCheck size={18} aria-hidden="true" />
            <Link to="/history" className="text-link">
              See all your past checks
            </Link>
          </p>
        </div>
      </div>
      <div className="wrap">
        <Disclaimer compact />
      </div>
    </div>
  );
}
