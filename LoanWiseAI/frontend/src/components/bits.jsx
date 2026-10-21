import { animate, motion, useReducedMotion } from 'framer-motion';
import { GraduationCap } from 'lucide-react';
import { useEffect, useState } from 'react';

export function Disclaimer({ compact = false }) {
  return (
    <aside className={`disclaimer${compact ? ' is-compact' : ''}`} aria-label="Important note">
      <span className="disclaimer-icon" aria-hidden="true">
        <GraduationCap size={compact ? 22 : 28} />
      </span>
      <p>
        <strong>This is a school project, not a bank.</strong> Our answer is a guess made by a computer that learned from
        614 old loan applications. A real bank will look at many more things before saying yes or no.
      </p>
    </aside>
  );
}

export function Skeleton({ lines = 3, className = '' }) {
  return (
    <div className={`skeleton ${className}`} aria-hidden="true">
      {Array.from({ length: lines }, (_, i) => (
        <span key={i} className="skeleton-line" style={{ width: `${92 - ((i * 17) % 40)}%` }} />
      ))}
    </div>
  );
}

/** Count up to a number once (respects reduced motion). */
export function useCountUp(target, { duration = 1.2, delay = 0.3 } = {}) {
  const reduce = useReducedMotion();
  const [v, setV] = useState(reduce ? target : 0);
  useEffect(() => {
    if (reduce) {
      setV(target);
      return undefined;
    }
    const c = animate(0, target, { duration, delay, ease: [0.2, 0.8, 0.2, 1], onUpdate: setV });
    return () => c.stop();
  }, [target, reduce, duration, delay]);
  return v;
}

/** Ring gauge: how sure the model is. value in 0..1 */
export function ConfidenceRing({ value, label, tone }) {
  const pct = Math.max(0, Math.min(1, Number(value) || 0));
  const reduce = useReducedMotion();
  const shown = useCountUp(Math.round(pct * 100));
  const R = 52;
  const L = 2 * Math.PI * R;
  return (
    <div className={`ring ring-${tone}`}>
      <svg viewBox="0 0 128 128" width="128" height="128" aria-hidden="true">
        <circle cx="64" cy="64" r={R} fill="none" className="ring-track" strokeWidth="12" />
        {[...Array(20)].map((_, i) => {
          const a = (i / 20) * Math.PI * 2 - Math.PI / 2;
          return <line key={i} x1={64 + Math.cos(a) * 38} y1={64 + Math.sin(a) * 38} x2={64 + Math.cos(a) * 41} y2={64 + Math.sin(a) * 41} className="ring-tick" />;
        })}
        <motion.circle
          cx="64"
          cy="64"
          r={R}
          fill="none"
          className="ring-value"
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={L}
          initial={{ strokeDashoffset: reduce ? L * (1 - pct) : L }}
          animate={{ strokeDashoffset: L * (1 - pct) }}
          transition={reduce ? { duration: 0 } : { delay: 0.3, duration: 1.2, ease: [0.2, 0.8, 0.2, 1] }}
          transform="rotate(-90 64 64)"
        />
      </svg>
      <div className="ring-center">
        <span className="ring-num">{Math.round(shown)}%</span>
        <span className="ring-label">{label}</span>
      </div>
    </div>
  );
}

export function PageHead({ title, children, art }) {
  return (
    <div className={`page-head${art ? ' has-art' : ''}`}>
      <div>
        <h1>{title}</h1>
        {children && <div className="page-lede">{children}</div>}
      </div>
      {art}
    </div>
  );
}
