import { AnimatePresence, motion } from 'framer-motion';
import { ArrowRight, CircleCheck, CircleX, FileDown, RefreshCw, ServerCrash, Trash2, TriangleAlert } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { EmptyArt } from '../components/art.jsx';
import { PageHead, Skeleton } from '../components/bits.jsx';
import { useToast } from '../components/toast.jsx';
import { niceDate, percent, rupees, yearsLabel } from '../lib/format.js';

function Verdict({ approved, text }) {
  const Icon = approved ? CircleCheck : CircleX;
  return (
    <span className={`verdict-pill ${approved ? 'is-yes' : 'is-no'}`}>
      <Icon size={18} aria-hidden="true" />
      {text || (approved ? 'Likely Approved' : 'Likely Not Approved')}
    </span>
  );
}

export default function History() {
  const toast = useToast();
  const [state, setState] = useState({ status: 'loading', items: [] });
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const confirmRef = useRef(null);
  const clearBtnRef = useRef(null);

  const fetchItems = useCallback(async () => {
    setState((s) => ({ ...s, status: 'loading' }));
    try {
      const data = await api.history(50);
      setState({ status: 'ready', items: Array.isArray(data.items) ? data.items : [] });
    } catch (err) {
      setState({ status: 'error', items: [], message: err.message });
    }
  }, []);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  useEffect(() => {
    if (confirming) confirmRef.current?.focus();
  }, [confirming]);

  const clearAll = async () => {
    setDeleting(true);
    try {
      await api.clearHistory();
      setState({ status: 'ready', items: [] });
      setConfirming(false);
      toast.show({ kind: 'success', message: 'All past checks were deleted.' });
    } catch (err) {
      toast.show({ kind: 'error', message: err.message });
    } finally {
      setDeleting(false);
    }
  };

  const downloadPdf = async (id) => {
    try {
      const blob = await api.downloadHistoryPdf(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `loanwise-assessment-report-${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.show({ kind: 'success', message: `Report #${id} downloaded.` });
    } catch (err) {
      toast.show({ kind: 'error', message: err.message || 'Could not download PDF.' });
    }
  };

  const items = state.items;

  return (
    <div className="wrap">
      <PageHead title="Your past checks">
        <p>Every time you check your chances, we keep a note here so you can compare.</p>
      </PageHead>

      {state.status === 'loading' && (
        <div className="history-list" aria-busy="true">
          <p className="sr-only" role="status">
            Loading your past checks
          </p>
          {[0, 1, 2].map((i) => (
            <div key={i} className="history-card">
              <Skeleton lines={3} />
            </div>
          ))}
        </div>
      )}

      {state.status === 'error' && (
        <div className="notice" role="alert">
          <span className="notice-icon" aria-hidden="true">
            <ServerCrash size={28} />
          </span>
          <div>
            <p className="notice-title">We couldn&rsquo;t load your past checks</p>
            <p>{state.message}</p>
          </div>
          <button type="button" className="btn btn-ghost" onClick={fetchItems}>
            <RefreshCw size={20} aria-hidden="true" /> Try again
          </button>
        </div>
      )}

      {state.status === 'ready' && items.length === 0 && (
        <div className="empty-state">
          <EmptyArt />
          <h2>No checks yet</h2>
          <p>When you check your loan chances, your answers and result will show up here.</p>
          <Link to="/check" className="btn btn-primary btn-xl">
            Check my loan chances
            <ArrowRight size={24} aria-hidden="true" />
          </Link>
        </div>
      )}

      {state.status === 'ready' && items.length > 0 && (
        <>
          <div className="history-bar">
            <p>
              <strong>{items.length}</strong> {items.length === 1 ? 'check' : 'checks'}, newest first
            </p>
            {!confirming && (
              <button ref={clearBtnRef} type="button" className="btn btn-danger-ghost" onClick={() => setConfirming(true)}>
                <Trash2 size={20} aria-hidden="true" />
                Delete all
              </button>
            )}
          </div>

          <AnimatePresence>
            {confirming && (
              <motion.div
                className="confirm"
                role="alertdialog"
                aria-labelledby="confirm-title"
                aria-describedby="confirm-desc"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                onKeyDown={(e) => {
                  if (e.key === 'Escape') {
                    setConfirming(false);
                    requestAnimationFrame(() => clearBtnRef.current?.focus());
                  }
                }}
              >
                <div className="confirm-inner">
                  <TriangleAlert size={28} aria-hidden="true" className="confirm-icon" />
                  <div>
                    <p id="confirm-title" className="confirm-title">
                      Delete all {items.length} past {items.length === 1 ? 'check' : 'checks'}?
                    </p>
                    <p id="confirm-desc">You can&rsquo;t undo this.</p>
                  </div>
                  <div className="confirm-actions">
                    <button ref={confirmRef} type="button" className="btn btn-ghost" onClick={() => setConfirming(false)} disabled={deleting}>
                      No, keep them
                    </button>
                    <button type="button" className="btn btn-danger" onClick={clearAll} disabled={deleting}>
                      <Trash2 size={20} aria-hidden="true" />
                      {deleting ? 'Deleting…' : 'Yes, delete all'}
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <ul className="history-list">
            {items.map((it) => {
              const inp = it.inputs || {};
              const income = Number(inp.applicant_income || 0) + Number(inp.coapplicant_income || 0);
              return (
                <li key={it.id} className={`history-card ${it.approved ? 'is-yes' : 'is-no'}`}>
                  <div className="history-top">
                    <Verdict approved={it.approved} text={it.verdict} />
                    <span className="history-date">{niceDate(it.created_at)}</span>
                  </div>
                  <dl className="history-facts">
                    <div>
                      <dt>Loan</dt>
                      <dd>{rupees(inp.loan_amount)}</dd>
                    </div>
                    <div>
                      <dt>Over</dt>
                      <dd>{inp.loan_term ? yearsLabel(inp.loan_term) : '—'}</dd>
                    </div>
                    <div>
                      <dt>Family income a month</dt>
                      <dd>{rupees(income)}</dd>
                    </div>
                    <div>
                      <dt>How sure</dt>
                      <dd>{it.confidence != null ? percent(it.confidence) : '—'}</dd>
                    </div>
                  </dl>
                  <div className="history-actions">
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={() => downloadPdf(it.id)}
                      title="Download assessment PDF report"
                    >
                      <FileDown size={16} aria-hidden="true" />
                      PDF Report
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        </>
      )}
    </div>
  );
}
