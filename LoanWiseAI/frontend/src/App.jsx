import { AnimatePresence, MotionConfig, motion } from 'framer-motion';
import { useEffect } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import { Footer, Nav } from './components/layout.jsx';
import { ToastProvider } from './components/toast.jsx';
import Check from './pages/Check.jsx';
import History from './pages/History.jsx';
import Home from './pages/Home.jsx';
import HowItWorks from './pages/HowItWorks.jsx';
import NotFound from './pages/NotFound.jsx';
import Result from './pages/Result.jsx';

const TITLES = {
  '/': 'LoanWise AI: check your loan chances',
  '/check': 'Check my chances | LoanWise AI',
  '/result': 'Your result | LoanWise AI',
  '/how-it-works': 'How it works | LoanWise AI',
  '/history': 'Past checks | LoanWise AI',
};

function Page({ children }) {
  return (
    <motion.div
      className="page"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.28, ease: [0.2, 0.8, 0.2, 1] }}
    >
      {children}
    </motion.div>
  );
}

export default function App() {
  const location = useLocation();
  useEffect(() => {
    document.title = TITLES[location.pathname] || 'Page not found | LoanWise AI';
    window.scrollTo({ top: 0 });
  }, [location.pathname]);

  return (
    <MotionConfig reducedMotion="user">
      <ToastProvider>
        <Nav />
        <main id="main" tabIndex={-1}>
          <AnimatePresence mode="wait" initial={false}>
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={<Page><Home /></Page>} />
              <Route path="/check" element={<Page><Check /></Page>} />
              <Route path="/result" element={<Page><Result /></Page>} />
              <Route path="/how-it-works" element={<Page><HowItWorks /></Page>} />
              <Route path="/history" element={<Page><History /></Page>} />
              <Route path="*" element={<Page><NotFound /></Page>} />
            </Routes>
          </AnimatePresence>
        </main>
        <Footer />
      </ToastProvider>
    </MotionConfig>
  );
}
