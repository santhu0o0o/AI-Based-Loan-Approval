import { AnimatePresence, motion } from 'framer-motion';
import { CircleCheck, Info, WifiOff, X } from 'lucide-react';
import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react';

const ToastCtx = createContext({ show: () => {}, dismiss: () => {} });
export const useToast = () => useContext(ToastCtx);

const ICONS = { error: WifiOff, success: CircleCheck, info: Info };

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const seq = useRef(0);
  const dismiss = useCallback((id) => setToasts((t) => t.filter((x) => x.id !== id)), []);
  const show = useCallback(
    ({ kind = 'info', title, message, duration = kind === 'error' ? 9000 : 5000 }) => {
      const id = ++seq.current;
      // Never stack the same message twice.
      setToasts((t) => [...t.filter((x) => x.message !== message), { id, kind, title, message }].slice(-3));
      if (duration) setTimeout(() => dismiss(id), duration);
      return id;
    },
    [dismiss],
  );
  const value = useMemo(() => ({ show, dismiss }), [show, dismiss]);
  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div className="toasts" aria-live="assertive" aria-atomic="false">
        <AnimatePresence initial={false}>
          {toasts.map((t) => {
            const Icon = ICONS[t.kind] || Info;
            return (
              <motion.div
                key={t.id}
                layout
                className={`toast toast-${t.kind}`}
                role={t.kind === 'error' ? 'alert' : 'status'}
                initial={{ opacity: 0, y: 24, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 12, scale: 0.96 }}
                transition={{ type: 'spring', stiffness: 380, damping: 30 }}
              >
                <span className="toast-icon" aria-hidden="true">
                  <Icon size={22} />
                </span>
                <div className="toast-body">
                  {t.title && <p className="toast-title">{t.title}</p>}
                  <p>{t.message}</p>
                </div>
                <button type="button" className="toast-close" onClick={() => dismiss(t.id)}>
                  <X size={20} aria-hidden="true" />
                  <span className="sr-only">Close message</span>
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastCtx.Provider>
  );
}
