// Hand-drawn SVG illustrations. Colors come from CSS custom properties so the
// palette lives in one place (styles.css).
import { motion, useReducedMotion } from 'framer-motion';
import { useId, useMemo } from 'react';

const C = {
  ink: 'var(--ink)',
  inkSoft: 'var(--ink-soft)',
  mari: 'var(--marigold)',
  mariLight: 'var(--marigold-light)',
  mariDeep: 'var(--marigold-deep)',
  leaf: 'var(--leaf)',
  leafSoft: 'var(--leaf-soft)',
  mist: 'var(--mist)',
  line: 'var(--line)',
  paper: 'var(--surface)',
  kum: 'var(--kumkum)',
};

/* ---------- Brand mark: a coin with a roof and a tick ---------- */
export function LogoMark({ size = 36 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-hidden="true" focusable="false">
      <circle cx="20" cy="20" r="19" fill={C.ink} />
      <circle cx="20" cy="20" r="15.5" fill="none" stroke={C.mari} strokeWidth="1.5" strokeDasharray="2 2.4" />
      <path d="M10.5 20.5 20 12l9.5 8.5" fill="none" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
      <path d="m14.5 23.5 4 4 7.5-8" fill="none" stroke={C.mari} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/* ---------- Tiny people icons (lucide-style strokes) ---------- */
export function ManIcon(props) {
  return (
    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>
      <circle cx="12" cy="4.5" r="2.5" />
      <path d="M8 22v-7H6.5v-4.5A2.5 2.5 0 0 1 9 8h6a2.5 2.5 0 0 1 2.5 2.5V15H16v7" />
      <path d="M12 15v7" />
    </svg>
  );
}
export function WomanIcon(props) {
  return (
    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>
      <circle cx="12" cy="4.5" r="2.5" />
      <path d="M9.5 8h5l3.5 9h-12z" />
      <path d="M10 17v5M14 17v5" />
    </svg>
  );
}

/* ---------- Rupee glyph as a path (so it never depends on a font) ---------- */
function Rupee({ x, y, s = 1, color = C.ink }) {
  return (
    <path
      transform={`translate(${x} ${y}) scale(${s})`}
      d="M-9 -14h18M-9 -7h18M-9 -14h5a7 7 0 0 1 0 14h-5l13 14"
      fill="none"
      stroke={color}
      strokeWidth="3.4"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  );
}

/* ---------- Hero: passbook + house + coin, with one stamp moment ---------- */
export function HeroArt() {
  const reduce = useReducedMotion();
  const t = (delay, duration = 0.5) => (reduce ? { duration: 0 } : { delay, duration, ease: [0.2, 0.8, 0.2, 1] });
  const rows = [0, 1, 2];
  return (
    <svg className="hero-art" viewBox="0 0 520 470" role="img" aria-labelledby="hero-art-title">
      <title id="hero-art-title">A loan form with three ticks, a small house, and a gold rupee coin</title>
      {/* soft ground */}
      <ellipse cx="270" cy="438" rx="210" ry="18" fill={C.mist} />
      <circle cx="290" cy="215" r="190" fill={C.mist} opacity="0.7" />
      {/* dotted orbit */}
      <circle cx="290" cy="215" r="160" fill="none" stroke={C.line} strokeWidth="2" strokeDasharray="3 9" />

      {/* passbook / form */}
      <motion.g initial={{ opacity: 0, y: 24, rotate: -8 }} animate={{ opacity: 1, y: 0, rotate: -6 }} transition={t(0.05, 0.7)} style={{ transformOrigin: '250px 230px' }}>
        <rect x="150" y="70" width="230" height="300" rx="18" fill={C.paper} stroke={C.ink} strokeWidth="3" />
        <rect x="150" y="70" width="230" height="58" rx="18" fill={C.ink} />
        <rect x="150" y="110" width="230" height="18" fill={C.ink} />
        <circle cx="182" cy="99" r="12" fill={C.mari} />
        <rect x="204" y="91" width="96" height="8" rx="4" fill="#fff" opacity="0.9" />
        <rect x="204" y="104" width="60" height="6" rx="3" fill="#fff" opacity="0.5" />
        {rows.map((r) => (
          <g key={r} transform={`translate(0 ${r * 52})`}>
            <rect x="176" y="156" width="26" height="26" rx="8" fill={C.leafSoft} />
            <motion.path
              d="m182 169 5 5 9-10"
              fill="none"
              stroke={C.leaf}
              strokeWidth="3.4"
              strokeLinecap="round"
              strokeLinejoin="round"
              initial={{ pathLength: reduce ? 1 : 0 }}
              animate={{ pathLength: 1 }}
              transition={t(0.6 + r * 0.22, 0.4)}
            />
            <rect x="214" y="160" width="120" height="8" rx="4" fill={C.line} />
            <rect x="214" y="174" width="78" height="6" rx="3" fill={C.line} opacity="0.7" />
          </g>
        ))}
        {/* stamp mark */}
        <motion.g
          initial={{ opacity: 0, scale: reduce ? 1 : 1.6 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={reduce ? { duration: 0 } : { delay: 1.55, type: 'spring', stiffness: 420, damping: 18 }}
          style={{ transformOrigin: '240px 326px' }}
        >
          <g transform="rotate(-10 240 326)">
            <rect x="187" y="304" width="106" height="44" rx="10" fill="none" stroke={C.leaf} strokeWidth="3.5" />
            <rect x="193" y="310" width="94" height="32" rx="6" fill="none" stroke={C.leaf} strokeWidth="1.5" />
            <text x="240" y="332" textAnchor="middle" fontFamily="var(--font-display)" fontWeight="800" fontSize="17" fill={C.leaf} letterSpacing="1">
              LIKELY YES
            </text>
          </g>
        </motion.g>
      </motion.g>

      {/* rubber stamp tool: drops, presses, lifts */}
      {!reduce && (
        <motion.g
          initial={{ y: -150, opacity: 0 }}
          animate={{ y: [-150, 0, 0, -170], opacity: [0, 1, 1, 0] }}
          transition={{ delay: 1.0, duration: 1.4, times: [0, 0.38, 0.55, 1], ease: 'easeInOut' }}
        >
          <g transform="translate(240 330) rotate(-10)">
            <rect x="-14" y="-80" width="28" height="44" rx="12" fill={C.mariDeep} />
            <rect x="-30" y="-40" width="60" height="16" rx="6" fill={C.ink} />
            <rect x="-48" y="-26" width="96" height="20" rx="5" fill={C.inkSoft} />
          </g>
        </motion.g>
      )}

      {/* house */}
      <motion.g initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={t(0.25, 0.7)}>
        <rect x="372" y="258" width="20" height="40" rx="3" fill={C.ink} />
        <rect x="340" y="300" width="130" height="128" rx="10" fill={C.mariLight} stroke={C.ink} strokeWidth="3" />
        <path d="M326 310 405 240l79 70" fill="none" stroke={C.ink} strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" />
        <rect x="390" y="358" width="34" height="70" rx="6" fill={C.ink} />
        <circle cx="416" cy="394" r="3" fill={C.mari} />
        <rect x="354" y="330" width="28" height="28" rx="5" fill={C.paper} stroke={C.ink} strokeWidth="3" />
        <rect x="436" y="330" width="22" height="28" rx="5" fill={C.paper} stroke={C.ink} strokeWidth="3" />
      </motion.g>

      {/* coin */}
      <motion.g
        initial={{ opacity: 0, y: 30 }}
        animate={reduce ? { opacity: 1, y: 0 } : { opacity: 1, y: [0, -10, 0] }}
        transition={reduce ? { duration: 0 } : { opacity: { delay: 0.4, duration: 0.5 }, y: { delay: 2.2, duration: 4, repeat: Infinity, ease: 'easeInOut' } }}
      >
        <circle cx="112" cy="352" r="66" fill={C.mariDeep} />
        <circle cx="106" cy="346" r="66" fill={C.mari} stroke={C.ink} strokeWidth="3" />
        <circle cx="106" cy="346" r="50" fill="none" stroke={C.ink} strokeWidth="2" strokeDasharray="4 6" opacity="0.5" />
        <Rupee x={106} y={346} s={1.9} />
      </motion.g>
      {/* small coin stack */}
      <g>
        <ellipse cx="208" cy="420" rx="30" ry="9" fill={C.mariDeep} />
        <rect x="178" y="404" width="60" height="16" fill={C.mariDeep} />
        <ellipse cx="208" cy="404" rx="30" ry="9" fill={C.mari} stroke={C.ink} strokeWidth="2.5" />
        <ellipse cx="208" cy="396" rx="30" ry="9" fill={C.mari} stroke={C.ink} strokeWidth="2.5" />
      </g>
      {/* sparkles */}
      {[
        [70, 120, 1],
        [470, 120, 0.8],
        [490, 210, 0.6],
      ].map(([x, y, s], i) => (
        <motion.path
          key={i}
          d="M0-12 3-3 12 0 3 3 0 12-3 3-12 0-3-3z"
          fill={i === 1 ? C.leaf : C.mari}
          transform={`translate(${x} ${y}) scale(${s})`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={t(1.8 + i * 0.15, 0.4)}
        />
      ))}
    </svg>
  );
}

/* ---------- Result stamp, with an ink-texture filter ---------- */
export function VerdictStamp({ approved, label }) {
  const reduce = useReducedMotion();
  const fid = useId().replace(/:/g, '');
  const color = approved ? C.leaf : C.ink;
  return (
    <motion.svg
      className="verdict-stamp"
      viewBox="0 0 300 130"
      role="img"
      aria-label={`Stamp: ${label}`}
      initial={reduce ? false : { opacity: 0, scale: 2.2, rotate: -2 }}
      animate={{ opacity: 1, scale: 1, rotate: -7 }}
      transition={reduce ? { duration: 0 } : { delay: 0.35, type: 'spring', stiffness: 500, damping: 22, mass: 1.1 }}
    >
      <defs>
        <filter id={`ink-${fid}`} x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n" />
          <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -3.2 2.55" result="holes" />
          <feComposite in="SourceGraphic" in2="holes" operator="in" />
        </filter>
      </defs>
      <g filter={`url(#ink-${fid})`}>
        <rect x="6" y="6" width="288" height="118" rx="18" fill="none" stroke={color} strokeWidth="7" />
        <rect x="18" y="18" width="264" height="94" rx="10" fill="none" stroke={color} strokeWidth="2.5" />
        <text x="150" y="80" textAnchor="middle" fontFamily="var(--font-display)" fontWeight="800" fontSize={label.length > 14 ? 27 : 34} fill={color} letterSpacing="1.5">
          {label.toUpperCase()}
        </text>
      </g>
    </motion.svg>
  );
}

/* ---------- Marigold petals for approvals ---------- */
export function Petals({ count = 30 }) {
  const reduce = useReducedMotion();
  const petals = useMemo(
    () =>
      Array.from({ length: count }, (_, i) => {
        const r = (n) => {
          const x = Math.sin(i * 97.13 + n * 13.7) * 10000;
          return x - Math.floor(x);
        };
        return {
          left: r(1) * 100,
          size: 10 + r(2) * 14,
          delay: r(3) * 0.9,
          dur: 2.6 + r(4) * 2,
          drift: (r(5) - 0.5) * 120,
          spin: (r(6) - 0.5) * 720,
          kind: i % 7 === 0 ? 'leaf' : i % 3 === 0 ? 'deep' : 'mari',
        };
      }),
    [count],
  );
  if (reduce) return null;
  const fill = { leaf: C.leaf, deep: C.mariDeep, mari: C.mari };
  return (
    <div className="petals" aria-hidden="true">
      {petals.map((p, i) => (
        <motion.svg
          key={i}
          viewBox="0 0 20 28"
          width={p.size}
          height={p.size * 1.4}
          style={{ left: `${p.left}%` }}
          initial={{ y: '-10vh', x: 0, rotate: 0, opacity: 0 }}
          animate={{ y: '75vh', x: p.drift, rotate: p.spin, opacity: [0, 1, 1, 0] }}
          transition={{ delay: 0.5 + p.delay, duration: p.dur, ease: [0.3, 0.1, 0.4, 1], times: [0, 0.1, 0.8, 1] }}
        >
          {p.kind === 'leaf' ? (
            <path d="M10 1C2 9 2 19 10 27 18 19 18 9 10 1z" fill={fill.leaf} />
          ) : (
            <path d="M10 27C3 22 1 13 4 5c2-4 4-4 6-1 2-3 4-3 6 1 3 8 1 17-6 22z" fill={fill[p.kind]} />
          )}
        </motion.svg>
      ))}
    </div>
  );
}

/* ---------- Gentle sprout for "not likely" ---------- */
export function SproutArt() {
  const reduce = useReducedMotion();
  const grow = (d, delay) => ({
    initial: { pathLength: reduce ? 1 : 0 },
    animate: { pathLength: 1 },
    transition: reduce ? { duration: 0 } : { delay, duration: 0.8, ease: 'easeOut' },
  });
  return (
    <svg className="sprout-art" viewBox="0 0 220 200" role="img" aria-label="A small plant growing in a pot">
      <circle cx="110" cy="96" r="84" fill={C.mist} />
      <g stroke={C.mari} strokeWidth="4" strokeLinecap="round" opacity="0.9">
        {[...Array(7)].map((_, i) => {
          const a = (-160 + i * 23) * (Math.PI / 180);
          return <line key={i} x1={168 + Math.cos(a) * 22} y1={46 + Math.sin(a) * 22} x2={168 + Math.cos(a) * 32} y2={46 + Math.sin(a) * 32} />;
        })}
      </g>
      <circle cx="168" cy="46" r="14" fill={C.mari} />
      <motion.path d="M110 150V92" fill="none" stroke={C.leaf} strokeWidth="5" strokeLinecap="round" {...grow('', 0.3)} />
      <motion.path d="M110 112c-6-20-24-26-40-22 2 18 18 28 40 22z" fill={C.leafSoft} stroke={C.leaf} strokeWidth="4" strokeLinejoin="round" {...grow('', 0.9)} />
      <motion.path d="M110 98c4-22 22-32 42-28-2 22-20 32-42 28z" fill={C.leafSoft} stroke={C.leaf} strokeWidth="4" strokeLinejoin="round" {...grow('', 1.2)} />
      <path d="M72 148h76l-9 40H81z" fill={C.mariLight} stroke={C.ink} strokeWidth="4" strokeLinejoin="round" />
      <rect x="66" y="140" width="88" height="14" rx="5" fill={C.ink} />
    </svg>
  );
}

/* ---------- Empty passbook for History ---------- */
export function EmptyArt() {
  return (
    <svg className="empty-art" viewBox="0 0 260 200" role="img" aria-label="An empty notebook with no entries yet">
      <ellipse cx="130" cy="184" rx="100" ry="10" fill={C.mist} />
      <path d="M30 40c30-10 70-10 100 4v130c-30-14-70-14-100-4z" fill={C.paper} stroke={C.ink} strokeWidth="4" strokeLinejoin="round" />
      <path d="M230 40c-30-10-70-10-100 4v130c30-14 70-14 100-4z" fill={C.paper} stroke={C.ink} strokeWidth="4" strokeLinejoin="round" />
      {[0, 1, 2, 3].map((i) => (
        <g key={i}>
          <line x1="48" y1={70 + i * 22} x2="114" y2={74 + i * 22} stroke={C.line} strokeWidth="4" strokeLinecap="round" strokeDasharray="1 9" />
          <line x1="146" y1={74 + i * 22} x2="212" y2={70 + i * 22} stroke={C.line} strokeWidth="4" strokeLinecap="round" strokeDasharray="1 9" />
        </g>
      ))}
      <g transform="rotate(35 196 40)">
        <rect x="186" y="-4" width="18" height="78" rx="4" fill={C.mari} stroke={C.ink} strokeWidth="3.5" />
        <path d="M186 74h18l-9 18z" fill={C.mariLight} stroke={C.ink} strokeWidth="3.5" strokeLinejoin="round" />
      </g>
    </svg>
  );
}

/* ---------- Lost signpost for 404 ---------- */
export function LostArt() {
  const reduce = useReducedMotion();
  return (
    <svg className="lost-art" viewBox="0 0 280 220" role="img" aria-label="A signpost pointing two different ways">
      <ellipse cx="140" cy="204" rx="110" ry="10" fill={C.mist} />
      <rect x="132" y="40" width="16" height="164" rx="4" fill={C.ink} />
      <motion.g initial={reduce ? false : { rotate: -4 }} animate={reduce ? {} : { rotate: [-4, 3, -4] }} transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }} style={{ transformOrigin: '140px 70px' }}>
        <path d="M60 52h132l20 18-20 18H60z" fill={C.mari} stroke={C.ink} strokeWidth="4" strokeLinejoin="round" />
        <text x="126" y="78" textAnchor="middle" fontFamily="var(--font-display)" fontWeight="800" fontSize="22" fill={C.ink}>Home?</text>
      </motion.g>
      <path d="M220 108H90l-20 18 20 18h130z" fill={C.paper} stroke={C.ink} strokeWidth="4" strokeLinejoin="round" />
      <text x="152" y="134" textAnchor="middle" fontFamily="var(--font-display)" fontWeight="800" fontSize="22" fill={C.ink}>404</text>
    </svg>
  );
}

/* ---------- Coin flip spinner ---------- */
export function CoinSpinner({ size = 64, label = 'Loading' }) {
  return (
    <span className="coin-spinner" role="status" aria-label={label} style={{ width: size, height: size }}>
      <svg viewBox="0 0 64 64" width={size} height={size} aria-hidden="true">
        <circle cx="32" cy="32" r="29" fill={C.mari} stroke={C.ink} strokeWidth="3" />
        <circle cx="32" cy="32" r="22" fill="none" stroke={C.ink} strokeWidth="1.5" strokeDasharray="3 4" opacity="0.5" />
        <Rupee x={32} y={32} s={0.95} />
      </svg>
    </span>
  );
}
