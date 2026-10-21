const inr = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 });

/** 500000 -> "5,00,000" */
export const groupIN = (n) => (n === '' || n == null || Number.isNaN(Number(n)) ? '' : inr.format(Math.round(Number(n))));

/** 500000 -> "₹5,00,000" */
export const rupees = (n) => (n === '' || n == null ? '—' : `₹${groupIN(n)}`);

/** Plain words for big numbers, Indian style: 250000 -> "2.5 lakh" */
export function inWords(n) {
  const v = Number(n);
  if (!v || Number.isNaN(v)) return '';
  const trim = (x) => String(Number(x.toFixed(2)));
  if (v >= 1e7) return `${trim(v / 1e7)} crore`;
  if (v >= 1e5) return `${trim(v / 1e5)} lakh`;
  if (v >= 1e3) return `${trim(v / 1e3)} thousand`;
  return String(v);
}

export const percent = (x) => `${Math.round(Number(x) * 100)}%`;

export function niceDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return String(iso);
  return d.toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit' });
}

export const yearsLabel = (months) => {
  const y = Math.round(Number(months) / 12);
  return `${y} ${y === 1 ? 'year' : 'years'}`;
};
