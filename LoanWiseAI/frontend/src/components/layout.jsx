import { AnimatePresence, motion } from 'framer-motion';
import { ClipboardCheck, History, House, Lightbulb, Menu, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { LogoMark } from './art.jsx';

export const NAV = [
  { to: '/', label: 'Home', icon: House, end: true },
  { to: '/check', label: 'Check my chances', icon: ClipboardCheck },
  { to: '/how-it-works', label: 'How it works', icon: Lightbulb },
  { to: '/history', label: 'Past checks', icon: History },
];

export function Nav() {
  const [open, setOpen] = useState(false);
  const loc = useLocation();
  useEffect(() => setOpen(false), [loc.pathname]);
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => e.key === 'Escape' && setOpen(false);
    document.addEventListener('keydown', onKey);
    document.body.classList.add('no-scroll');
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.classList.remove('no-scroll');
    };
  }, [open]);

  return (
    <header className="site-header">
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <div className="nav-inner">
        <Link to="/" className="brand" aria-label="LoanWise AI, go to home page">
          <LogoMark />
          <span className="brand-name">
            LoanWise <span className="brand-ai">AI</span>
          </span>
        </Link>
        <nav className="nav-links" aria-label="Main">
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}${to === '/check' ? ' nav-cta' : ''}`}>
              <Icon size={20} aria-hidden="true" />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <button
          type="button"
          className="menu-btn"
          aria-expanded={open}
          aria-controls="mobile-menu"
          onClick={() => setOpen((o) => !o)}
        >
          {open ? <X size={26} aria-hidden="true" /> : <Menu size={26} aria-hidden="true" />}
          <span>{open ? 'Close' : 'Menu'}</span>
        </button>
      </div>
      <AnimatePresence>
        {open && (
          <motion.nav
            id="mobile-menu"
            className="mobile-menu"
            aria-label="Main"
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.2 }}
          >
            {NAV.map(({ to, label, icon: Icon, end }, i) => (
              <motion.div key={to} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.04 * i }}>
                <NavLink to={to} end={end} className={({ isActive }) => `mobile-link${isActive ? ' is-active' : ''}`}>
                  <span className="mobile-link-icon">
                    <Icon size={24} aria-hidden="true" />
                  </span>
                  {label}
                </NavLink>
              </motion.div>
            ))}
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <LogoMark size={30} />
          <p>
            <strong>LoanWise AI</strong> is a student project. It makes a guess using past loan data. It is not a bank, and it
            cannot give you a loan.
          </p>
        </div>
        <nav className="footer-links" aria-label="Footer">
          {NAV.map(({ to, label }) => (
            <Link key={to} to={to}>
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}
