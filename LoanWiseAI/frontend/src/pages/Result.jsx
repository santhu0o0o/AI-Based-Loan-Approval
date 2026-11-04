import { motion, useReducedMotion } from 'framer-motion';
import {
  ArrowRight,
  Calculator,
  CheckCircle2,
  ClipboardCheck,
  FileDown,
  Info,
  Lightbulb,
  PencilLine,
  Printer,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  TrendingUp,
  Wrench,
} from 'lucide-react';
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { EmptyArt, Petals, SproutArt, VerdictStamp } from '../components/art.jsx';
import { ConfidenceRing, Disclaimer, useCountUp } from '../components/bits.jsx';
import { useToast } from '../components/toast.jsx';
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
  const toast = useToast();
  const reduce = useReducedMotion();
  const [downloading, setDownloading] = useState(false);

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
  const suggestions = Array.isArray(result.improvement_suggestions) ? result.improvement_suggestions : [];
  const metrics = result.financial_metrics || {};
  const detailedExplanation = result.detailed_explanation || '';
  const stampText = approved ? 'Likely approved' : 'Not likely yet';
  const headline =
    result.headline || (approved ? 'Great news! Your loan is likely to be approved.' : 'Your loan may not be approved right now.');

  const tryAgain = () => navigate('/check', { state: { step: 0 } });
  const fresh = () => {
    remove(KEYS.answers);
    remove(KEYS.step);
    navigate('/check', { state: { step: 0, fresh: Date.now() } });
  };

  const handleDownloadPdf = async () => {
    if (downloading) return;
    try {
      setDownloading(true);
      const blob = await api.downloadReportPdf({
        answers: answers || {},
        result: result,
        id: result.id,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `loanwise-assessment-report-${result.id || 'check'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.show({
        kind: 'success',
        title: 'Report Downloaded',
        message: 'Your official assessment report PDF has been saved.',
      });
    } catch (err) {
      toast.show({
        kind: 'error',
        title: 'Download Failed',
        message: err.message || 'Could not generate PDF report. Please try again.',
      });
    } finally {
      setDownloading(false);
    }
  };

  const handlePrint = () => {
    window.print();
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
        <div className="result-left-col">
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
                    A &ldquo;no&rdquo; today is not a &ldquo;no&rdquo; forever. The actionable suggestions below show
                    what you can change, like borrowing a little less or extending your loan term.
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

          {/* Quick PDF Download Card */}
          <section className="pdf-card" aria-label="Download Official Report">
            <div className="pdf-card-content">
              <div className="pdf-icon-wrap" aria-hidden="true">
                <FileDown size={28} />
              </div>
              <div>
                <h2>Download Official Report</h2>
                <p>Get a formal PDF document containing your full underwriting assessment, reasons, and personalized improvement plan.</p>
              </div>
            </div>
            <div className="pdf-card-actions">
              <button
                type="button"
                className="btn btn-primary btn-lg"
                onClick={handleDownloadPdf}
                disabled={downloading}
              >
                <FileDown size={20} aria-hidden="true" />
                {downloading ? 'Preparing PDF…' : 'Download PDF Report'}
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={handlePrint}
                title="Print assessment slip"
              >
                <Printer size={18} aria-hidden="true" />
                Print
              </button>
            </div>
          </section>

          {/* Key Financial Snapshot */}
          {metrics.total_income > 0 && (
            <section className="metrics-card" aria-label="Financial Snapshot">
              <h2 className="metrics-title">
                <TrendingUp size={20} aria-hidden="true" />
                Financial Health Snapshot
              </h2>
              <div className="metrics-grid">
                <div className="metric-box">
                  <span className="metric-label">Monthly Household Income</span>
                  <span className="metric-value">₹{groupIN(Math.round(metrics.total_income))}</span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Debt-to-Income (DTI)</span>
                  <span className={`metric-value ${metrics.emi_to_income_ratio > 0.45 ? 'is-warn' : 'is-good'}`}>
                    {metrics.emi_to_income_pct}
                  </span>
                  <span className="metric-sub">{metrics.affordability_band}</span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Loan vs Annual Income</span>
                  <span className="metric-value">{metrics.loan_to_income_years} years</span>
                  <span className="metric-sub">{metrics.loan_to_income_years <= 3 ? 'Sensible size' : 'Heavy multiple'}</span>
                </div>
                {metrics.max_safe_loan_amount > 0 && (
                  <div className="metric-box">
                    <span className="metric-label">Recommended Safe Loan</span>
                    <span className="metric-value">₹{groupIN(Math.round(metrics.max_safe_loan_amount))}</span>
                    <span className="metric-sub">Under 40% income ceiling</span>
                  </div>
                )}
              </div>
            </section>
          )}
        </div>

        <div className="result-side">
          {/* Actionable Improvement Suggestions (Specially highlighted for rejections!) */}
          {suggestions.length > 0 && (
            <section
              className={`panel ${approved ? 'panel-tips' : 'panel-action-plan'}`}
              aria-labelledby="plan-title"
            >
              <h2 id="plan-title" className="panel-title">
                {approved ? (
                  <>
                    <ShieldCheck size={24} aria-hidden="true" className="title-icon-good" />
                    Recommended Next Steps Before Disbursement
                  </>
                ) : (
                  <>
                    <Lightbulb size={24} aria-hidden="true" className="title-icon-action" />
                    How to Alter Your Application to Get Approved
                  </>
                )}
              </h2>
              <p className="panel-lead">
                {approved
                  ? 'Follow these prudent guidelines to ensure smooth final loan approval and disbursement with the bank:'
                  : 'Based on our underwriting criteria, here are the most effective concrete changes you can make to qualify for loan approval:'}
              </p>
              <div className="suggestions-list">
                {suggestions.map((s, idx) => (
                  <div key={idx} className="suggestion-card">
                    <div className="suggestion-header">
                      <span className="suggestion-badge">{s.category || 'Adjustment'}</span>
                      <h3 className="suggestion-title">{s.title}</h3>
                    </div>
                    <p className="suggestion-desc">{s.description}</p>
                    <div className="suggestion-action-box">
                      <strong>Recommended Action: </strong>
                      <span>{s.action}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Primary Reasons List */}
          {reasons.length > 0 && (
            <section className="panel" aria-labelledby="why-title">
              <h2 id="why-title" className="panel-title">
                Key Decision Factors
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

          {/* Detailed Narrative Explanation */}
          {detailedExplanation && (
            <section className="panel panel-analysis" aria-labelledby="analysis-title">
              <h2 id="analysis-title" className="panel-title">
                <Sparkles size={22} aria-hidden="true" />
                Detailed Underwriting Analysis
              </h2>
              <div className="explanation-paragraphs">
                {detailedExplanation.split('\n\n').map((para, i) => (
                  <p key={i}>{para}</p>
                ))}
              </div>
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
            <button
              type="button"
              className="btn btn-primary btn-lg"
              onClick={handleDownloadPdf}
              disabled={downloading}
            >
              <FileDown size={22} aria-hidden="true" />
              {downloading ? 'Preparing PDF…' : 'Download PDF Report'}
            </button>
            <button type="button" className="btn btn-ghost btn-lg" onClick={tryAgain}>
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
