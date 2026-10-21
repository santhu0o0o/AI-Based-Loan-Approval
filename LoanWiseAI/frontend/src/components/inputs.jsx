import { AnimatePresence, motion } from 'framer-motion';
import { CircleAlert, CircleHelp, X } from 'lucide-react';
import { useEffect, useId, useRef, useState } from 'react';
import { groupIN, inWords } from '../lib/format.js';

/* ---------- "?" explainer: tap to open, tap / Esc to close ---------- */
function useHelp() {
  const [open, setOpen] = useState(false);
  const id = useId();
  const btn = useRef(null);
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setOpen(false);
        btn.current?.focus();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);
  return { open, setOpen, id, btn };
}

function HelpButton({ help, label }) {
  return (
    <button
      ref={help.btn}
      type="button"
      className={`help-btn${help.open ? ' is-open' : ''}`}
      aria-expanded={help.open}
      aria-controls={help.id}
      onClick={() => help.setOpen((o) => !o)}
    >
      <CircleHelp size={22} aria-hidden="true" />
      <span className="sr-only">What does &ldquo;{label}&rdquo; mean?</span>
    </button>
  );
}

function HelpBubble({ help, children }) {
  return (
    <div id={help.id}>
      <AnimatePresence initial={false}>
        {help.open && (
          <motion.div
            className="help-bubble"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.22 }}
          >
            <div className="help-bubble-inner">
              <p>{children}</p>
              <button type="button" className="help-close" onClick={() => help.setOpen(false)}>
                <X size={18} aria-hidden="true" /> Got it
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function FieldError({ id, message }) {
  return (
    <div id={id} className="field-error-slot" aria-live="polite">
      <AnimatePresence initial={false}>
        {message && (
          <motion.p
            key={message}
            className="field-error"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
          >
            <CircleAlert size={20} aria-hidden="true" />
            <span>{message}</span>
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}

/* Shared question wrapper: big question, optional ?, hint, error. */
function Question({ labelId, label, helpLabel, help, hint, error, errorId, children, className = '', ...rest }) {
  const h = useHelp();
  return (
    <div className={`question${error ? ' has-error' : ''} ${className}`} {...rest}>
      <div className="question-head">
        <span id={labelId} className="question-label">
          {label}
        </span>
        {help && <HelpButton help={h} label={helpLabel || label} />}
      </div>
      {help && <HelpBubble help={h}>{help}</HelpBubble>}
      {hint && <p className="question-hint">{hint}</p>}
      {children}
      <FieldError id={errorId} message={error} />
    </div>
  );
}

/* ---------- Big tappable choice cards (native radios underneath) ---------- */
export function ChoiceGroup({ name, label, help, hint, options, value, onChange, error, columns = 2, note }) {
  const base = useId();
  const errorId = `${base}-err`;
  return (
    <Question
      labelId={`${base}-label`}
      label={label}
      help={help}
      hint={hint}
      error={error}
      errorId={errorId}
      data-field={name}
    >
      <div className={`choices cols-${columns}`} role="radiogroup" aria-labelledby={`${base}-label`} aria-describedby={error ? errorId : undefined}>
        {options.map((o) => {
          const Icon = o.icon;
          const checked = value === o.value;
          return (
            <label key={o.value} className={`choice${checked ? ' is-checked' : ''}`}>
              <input
                type="radio"
                name={name}
                value={o.value}
                checked={checked}
                onChange={() => onChange(o.value)}
                aria-invalid={error ? 'true' : undefined}
              />
              {Icon && (
                <span className="choice-icon" aria-hidden="true">
                  <Icon size={26} />
                </span>
              )}
              <span className="choice-text">
                <span className="choice-label">{o.label}</span>
                {o.sub && <span className="choice-sub">{o.sub}</span>}
              </span>
              <span className="choice-tick" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path d="m5 12.5 4.5 4.5L19 7.5" fill="none" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
            </label>
          );
        })}
      </div>
      <AnimatePresence initial={false}>
        {note && (
          <motion.p className="choice-note" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
            {note}
          </motion.p>
        )}
      </AnimatePresence>
    </Question>
  );
}

/* ---------- ₹ amount field: digits only, live Indian grouping ---------- */
export function MoneyInput({ name, label, help, hint, example, value, onChange, onBlur, error, suffix, quick }) {
  const base = useId();
  const inputId = `${base}-input`;
  const errorId = `${base}-err`;
  const hintId = `${base}-hint`;
  const ref = useRef(null);
  const pendingCaret = useRef(null);

  // Keep the caret in the same place relative to the digits after re-formatting.
  useEffect(() => {
    const el = ref.current;
    if (!el || pendingCaret.current == null) return;
    const digitsRight = pendingCaret.current;
    pendingCaret.current = null;
    let pos = el.value.length;
    let seen = 0;
    while (pos > 0 && seen < digitsRight) {
      pos -= 1;
      if (/\d/.test(el.value[pos])) seen += 1;
    }
    if (digitsRight === 0) pos = el.value.length;
    el.setSelectionRange(pos, pos);
  });

  const handle = (e) => {
    const raw = e.target.value;
    const caret = e.target.selectionStart ?? raw.length;
    pendingCaret.current = raw.slice(caret).replace(/\D/g, '').length;
    const digits = raw.replace(/\D/g, '').replace(/^0+(?=\d)/, '').slice(0, 9);
    onChange(digits);
  };

  const words = value !== '' && Number(value) >= 1000 ? inWords(value) : '';
  return (
    <Question labelId={`${base}-label`} label={<label htmlFor={inputId}>{label}</label>} helpLabel={label} help={help} error={error} errorId={errorId} data-field={name}>
      <div className="money-row">
        <div className={`money${error ? ' is-invalid' : ''}`}>
          <span className="money-prefix" aria-hidden="true">₹</span>
          <input
            ref={ref}
            id={inputId}
            name={name}
            type="text"
            inputMode="numeric"
            size={1}
            autoComplete="off"
            enterKeyHint="next"
            placeholder={example ? groupIN(example) : '0'}
            value={groupIN(value)}
            onChange={handle}
            onBlur={onBlur}
            onKeyDown={(e) => {
              if (e.key.length === 1 && !/\d/.test(e.key) && !e.ctrlKey && !e.metaKey) e.preventDefault();
            }}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={`${hintId}${error ? ` ${errorId}` : ''}`}
          />
          {suffix && <span className="money-suffix">{suffix}</span>}
          {error && <CircleAlert className="money-alert" size={22} aria-hidden="true" />}
        </div>
        {quick && (
          <button type="button" className={`quick-chip${value === quick.value ? ' is-on' : ''}`} onClick={() => onChange(quick.value)}>
            {quick.label}
          </button>
        )}
      </div>
      <p id={hintId} className="question-hint money-hint">
        {words ? (
          <span className="money-words">
            That&rsquo;s <strong>₹{words}</strong>
            {suffix ? ` ${suffix}` : ''}.
          </span>
        ) : (
          <span>{hint}</span>
        )}
        {example && <span className="money-example">Example: ₹{groupIN(example)}</span>}
      </p>
    </Question>
  );
}
