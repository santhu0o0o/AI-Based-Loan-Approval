import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Briefcase,
  Building2,
  CircleAlert,
  CircleOff,
  GraduationCap,
  HeartHandshake,
  House,
  RotateCcw,
  Store,
  ThumbsDown,
  ThumbsUp,
  Trees,
  User,
  Users,
  UsersRound,
  WandSparkles,
  Baby,
  Sparkles,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { CoinSpinner, ManIcon, WomanIcon } from '../components/art.jsx';
import { ChoiceGroup, MoneyInput } from '../components/inputs.jsx';
import { useToast } from '../components/toast.jsx';
import { EMPTY, FIELD_STEP, STEPS, TERM_YEARS, fromPayload, toPayload, validateAll, validateField, validateStep } from '../lib/fields.js';
import { KEYS, load, remove, save } from '../lib/storage.js';

const OPTIONS = {
  gender: [
    { value: 'Male', label: 'Man', icon: ManIcon },
    { value: 'Female', label: 'Woman', icon: WomanIcon },
  ],
  married: [
    { value: 'Yes', label: 'Yes, married', icon: HeartHandshake },
    { value: 'No', label: 'No, not married', icon: User },
  ],
  dependents: [
    { value: '0', label: 'None', sub: 'Just me', icon: CircleOff },
    { value: '1', label: '1 person', icon: Baby },
    { value: '2', label: '2 people', icon: Users },
    { value: '3+', label: '3 or more', icon: UsersRound },
  ],
  education: [
    { value: 'Graduate', label: 'Yes, I graduated', sub: 'Finished a college degree', icon: GraduationCap },
    { value: 'Not Graduate', label: 'No', sub: 'Did not finish college', icon: BookOpen },
  ],
  self_employed: [
    { value: 'No', label: 'I get a salary', sub: 'Someone else pays me', icon: Briefcase },
    { value: 'Yes', label: 'I work for myself', sub: 'My own shop or business', icon: Store },
  ],
  credit_choice: [
    { value: 'yes', label: 'Yes, always on time', icon: ThumbsUp },
    { value: 'no', label: 'No, I was late or missed some', icon: ThumbsDown },
    { value: 'never', label: 'I never had a loan or card', icon: Sparkles },
  ],
  property_area: [
    { value: 'Urban', label: 'In a city', sub: 'Big town, lots of buildings', icon: Building2 },
    { value: 'Semiurban', label: 'Near a city', sub: 'Small town or edge of a city', icon: House },
    { value: 'Rural', label: 'In a village', sub: 'Countryside, farms', icon: Trees },
  ],
};

const CREDIT_NOTES = {
  never: 'That’s okay. You haven’t missed any payments, so we count this as a clean record.',
  no: 'Thanks for being honest. Late payments lower your chances, but your result will show what else can help.',
};

export default function Check() {
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const reduce = useReducedMotion();

  const [answers, setAnswers] = useState(() => ({ ...EMPTY, ...load(KEYS.answers, {}) }));
  const [step, setStep] = useState(() => Math.min(Math.max(Number(load(KEYS.step, 0)) || 0, 0), STEPS.length - 1));
  const [dir, setDir] = useState(1);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [banner, setBanner] = useState('');
  const [busy, setBusy] = useState(false);
  const [filling, setFilling] = useState(false);
  const topRef = useRef(null);
  const firstRender = useRef(true);

  // Server 422 errors handed over from the result page, or jump to a step.
  useEffect(() => {
    const s = location.state;
    if (s?.step != null) setStep(s.step);
  }, [location.state]);

  useEffect(() => save(KEYS.answers, answers), [answers]);
  useEffect(() => save(KEYS.step, step), [step]);

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    topRef.current?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    const h = topRef.current?.querySelector('h1');
    h?.focus({ preventScroll: true });
  }, [step, reduce]);

  const set = useCallback((name, value) => {
    setAnswers((prev) => {
      const next = { ...prev, [name]: value };
      setErrors((e) => {
        const ne = { ...e };
        // Choice taps validate straight away; typed numbers only once already flagged or touched.
        const live = !['applicant_income', 'coapplicant_income', 'loan_amount'].includes(name) || e[name] || touched[name];
        if (live) {
          const m = validateField(name, next);
          if (m) ne[name] = m;
          else delete ne[name];
        }
        // The two incomes depend on each other.
        if ((name === 'coapplicant_income' || name === 'applicant_income') && (e.applicant_income || touched.applicant_income)) {
          const m = validateField('applicant_income', next);
          if (m) ne.applicant_income = m;
          else delete ne.applicant_income;
        }
        return ne;
      });
      return next;
    });
    setBanner('');
  }, [touched]);

  const blur = (name) => () => {
    setTouched((t) => ({ ...t, [name]: true }));
    setErrors((e) => {
      const m = validateField(name, answers);
      const ne = { ...e };
      if (m) ne[name] = m;
      else delete ne[name];
      return ne;
    });
  };

  const focusFirstError = (errs) => {
    const first = STEPS[step].fields.find((f) => errs[f]) || Object.keys(errs)[0];
    requestAnimationFrame(() => {
      const el = document.querySelector(`[data-field="${first}"]`);
      el?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
      el?.querySelector('input')?.focus({ preventScroll: true });
    });
  };

  const goNext = () => {
    const errs = validateStep(step, answers);
    if (Object.keys(errs).length) {
      setErrors((e) => ({ ...e, ...errs }));
      setTouched((t) => ({ ...t, ...Object.fromEntries(Object.keys(errs).map((k) => [k, true])) }));
      const n = Object.keys(errs).length;
      setBanner(n === 1 ? '1 answer needs fixing. Look for the red box.' : `${n} answers need fixing. Look for the red boxes.`);
      focusFirstError(errs);
      return;
    }
    setBanner('');
    setDir(1);
    setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };

  const goBack = () => {
    setBanner('');
    setDir(-1);
    setStep((s) => Math.max(s - 1, 0));
  };

  const allErrors = useMemo(() => validateAll(answers), [answers]);
  const remaining = Object.keys(allErrors).length;

  const submit = async (e) => {
    e?.preventDefault();
    if (step < STEPS.length - 1) return goNext();
    if (remaining) {
      setErrors(allErrors);
      const firstStep = Math.min(...Object.keys(allErrors).map((f) => FIELD_STEP[f] ?? 0));
      if (firstStep !== step) {
        setDir(-1);
        setStep(firstStep);
      }
      setBanner('Some answers are missing. Look for the red boxes.');
      return;
    }
    setBusy(true);
    setBanner('');
    const started = Date.now();
    try {
      const result = await api.predict(toPayload(answers));
      // Give the "checking" moment time to be seen.
      const wait = Math.max(0, 900 - (Date.now() - started));
      await new Promise((r) => setTimeout(r, reduce ? 0 : wait));
      save(KEYS.result, { result, answers });
      navigate('/result', { state: { result, answers } });
    } catch (err) {
      setBusy(false);
      if (err.kind === 'validation') {
        const mapped = {};
        for (const [k, v] of Object.entries(err.errors || {})) mapped[k === 'credit_history' ? 'credit_choice' : k] = v;
        setErrors(mapped);
        const steps = Object.keys(mapped).map((f) => FIELD_STEP[f]).filter((x) => x != null);
        if (steps.length) {
          const s = Math.min(...steps);
          setDir(s < step ? -1 : 1);
          setStep(s);
        }
        setBanner(err.message);
      } else {
        toast.show({ kind: 'error', title: 'Your answers are safe', message: err.message });
      }
    }
  };

  const fillExample = async () => {
    setFilling(true);
    try {
      const sample = await api.sample();
      const filled = fromPayload(sample?.sample || sample?.data || sample);
      const blanks = Object.entries(filled).filter(([, v]) => v === '').length;
      setAnswers(filled);
      setErrors({});
      setTouched({});
      setBanner('');
      setDir(-1);
      setStep(0);
      toast.show({
        kind: 'success',
        title: 'Example filled in',
        message: blanks
          ? `We filled in a real example. ${blanks} answer${blanks > 1 ? 's were' : ' was'} blank in it, so please tap ${blanks > 1 ? 'those' : 'that one'} yourself.`
          : 'We filled in a real example. Look it over, then press Next.',
      });
    } catch (err) {
      toast.show({ kind: 'error', message: err.message });
    } finally {
      setFilling(false);
    }
  };

  const startOver = () => {
    setAnswers({ ...EMPTY });
    setErrors({});
    setTouched({});
    setBanner('');
    setDir(-1);
    setStep(0);
    remove(KEYS.answers);
  };

  const hasAny = Object.values(answers).some((v) => v !== '');
  const S = STEPS[step];
  const last = step === STEPS.length - 1;
  const progress = ((step + (last && !remaining ? 1 : 0.5)) / STEPS.length) * 100;

  return (
    <div className="wizard-wrap" ref={topRef}>
      <div className="wizard-top">
        <div className="wizard-tools">
          <button type="button" className="btn btn-quiet" onClick={fillExample} disabled={filling || busy}>
            <WandSparkles size={20} aria-hidden="true" />
            {filling ? 'Filling…' : 'Fill an example for me'}
          </button>
          {hasAny && (
            <button type="button" className="btn btn-quiet" onClick={startOver} disabled={busy}>
              <RotateCcw size={20} aria-hidden="true" />
              Clear answers
            </button>
          )}
        </div>

        <ol className="stepper" aria-label="Your progress">
          {STEPS.map((s, i) => (
            <li key={s.id} className={`stepper-item${i === step ? ' is-current' : ''}${i < step ? ' is-done' : ''}`} aria-current={i === step ? 'step' : undefined}>
              <span className="stepper-dot" aria-hidden="true">
                {i < step ? (
                  <svg viewBox="0 0 24 24" width="18" height="18">
                    <path d="m5 12.5 4.5 4.5L19 7.5" fill="none" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : (
                  i + 1
                )}
              </span>
              <span className="stepper-label">{s.title}</span>
              <span className="sr-only">{i < step ? ' (done)' : i === step ? ' (you are here)' : ''}</span>
            </li>
          ))}
        </ol>
        <div className="progress" aria-hidden="true">
          <motion.span className="progress-fill" animate={{ width: `${progress}%` }} transition={{ type: 'spring', stiffness: 120, damping: 20 }} />
        </div>
      </div>

      <form className="wizard-card" onSubmit={submit} noValidate>
        <AnimatePresence mode="wait" initial={false} custom={dir}>
          <motion.div
            key={S.id}
            custom={dir}
            variants={{
              enter: (d) => ({ opacity: 0, x: reduce ? 0 : d * 48 }),
              center: { opacity: 1, x: 0 },
              exit: (d) => ({ opacity: 0, x: reduce ? 0 : d * -48 }),
            }}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.28, ease: [0.2, 0.8, 0.2, 1] }}
          >
            <header className="wizard-head">
              <p className="wizard-count">
                Step {step + 1} of {STEPS.length}
              </p>
              <h1 tabIndex={-1}>{S.title}</h1>
              <p className="wizard-intro">{S.intro}</p>
            </header>

            {step === 0 && (
              <div className="questions">
                <ChoiceGroup name="gender" label="Are you a man or a woman?" options={OPTIONS.gender} value={answers.gender} onChange={(v) => set('gender', v)} error={errors.gender} />
                <ChoiceGroup name="married" label="Are you married?" options={OPTIONS.married} value={answers.married} onChange={(v) => set('married', v)} error={errors.married} />
                <ChoiceGroup
                  name="dependents"
                  label="How many people depend on your money?"
                  help="These are people you pay for, like your children or old parents who live with you. Don't count yourself or your husband or wife."
                  options={OPTIONS.dependents}
                  columns={4}
                  value={answers.dependents}
                  onChange={(v) => set('dependents', v)}
                  error={errors.dependents}
                />
                <ChoiceGroup
                  name="education"
                  label="Did you finish college?"
                  help="Tap 'Yes' if you have a degree, like a B.A., B.Com, B.Sc or B.Tech. If you stopped after school, tap 'No'."
                  options={OPTIONS.education}
                  value={answers.education}
                  onChange={(v) => set('education', v)}
                  error={errors.education}
                />
                <ChoiceGroup
                  name="self_employed"
                  label="How do you earn your money?"
                  help="A salary means a company or boss pays you every month. Working for yourself means you run your own shop, business or freelance work."
                  options={OPTIONS.self_employed}
                  value={answers.self_employed}
                  onChange={(v) => set('self_employed', v)}
                  error={errors.self_employed}
                />
              </div>
            )}

            {step === 1 && (
              <div className="questions">
                <MoneyInput
                  name="applicant_income"
                  label="How much do you earn each month?"
                  help="This is the money you get in one month, before you spend any of it. If your pay changes, use a normal month."
                  hint="Type numbers only. We add the commas for you."
                  example={25000}
                  suffix="a month"
                  value={answers.applicant_income}
                  onChange={(v) => set('applicant_income', v)}
                  onBlur={blur('applicant_income')}
                  error={errors.applicant_income}
                />
                <MoneyInput
                  name="coapplicant_income"
                  label="Does someone else help pay the loan? How much do they earn each month?"
                  help="This is a person who signs the loan with you, like your husband, wife, or a parent. Their income can help. If nobody is helping, tap 'No one'."
                  hint="Their monthly income. Type 0 if no one is helping."
                  example={15000}
                  suffix="a month"
                  quick={{ value: '0', label: 'No one' }}
                  value={answers.coapplicant_income}
                  onChange={(v) => set('coapplicant_income', v)}
                  onBlur={blur('coapplicant_income')}
                  error={errors.coapplicant_income}
                />
                <ChoiceGroup
                  name="credit_choice"
                  label="Have you paid back past loans or credit cards on time?"
                  help="Banks look at whether you paid your past loans, phone EMIs or credit card bills by the due date. This is the most important question."
                  options={OPTIONS.credit_choice}
                  columns={3}
                  value={answers.credit_choice}
                  onChange={(v) => set('credit_choice', v)}
                  error={errors.credit_choice}
                  note={CREDIT_NOTES[answers.credit_choice]}
                />
              </div>
            )}

            {step === 2 && (
              <div className="questions">
                <MoneyInput
                  name="loan_amount"
                  label="How much money do you want to borrow?"
                  help="The full amount you want from the bank, not the monthly payment. For example, if the house costs ₹30 lakh and you have ₹5 lakh saved, you need ₹25 lakh."
                  hint="The full loan amount, between ₹1,000 and ₹1 crore."
                  example={500000}
                  value={answers.loan_amount}
                  onChange={(v) => set('loan_amount', v)}
                  onBlur={blur('loan_amount')}
                  error={errors.loan_amount}
                />
                <ChoiceGroup
                  name="loan_term"
                  label="How many years do you want to pay it back over?"
                  help="More years means a smaller payment each month, but you pay for longer. Most home loans are 20 to 30 years."
                  options={TERM_YEARS.map((y) => ({ value: String(y * 12), label: `${y} ${y === 1 ? 'year' : 'years'}` }))}
                  columns={5}
                  value={answers.loan_term}
                  onChange={(v) => set('loan_term', v)}
                  error={errors.loan_term}
                />
                <ChoiceGroup
                  name="property_area"
                  label="Where is the house?"
                  help="Pick the place that best matches where the house you want to buy is."
                  options={OPTIONS.property_area}
                  columns={3}
                  value={answers.property_area}
                  onChange={(v) => set('property_area', v)}
                  error={errors.property_area}
                />
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        <div className="banner-slot" aria-live="assertive">
          <AnimatePresence>
            {banner && (
              <motion.p className="form-banner" role="alert" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <CircleAlert size={22} aria-hidden="true" />
                {banner}
              </motion.p>
            )}
          </AnimatePresence>
        </div>

        <div className="wizard-actions">
          {step > 0 ? (
            <button type="button" className="btn btn-ghost btn-lg" onClick={goBack} disabled={busy}>
              <ArrowLeft size={22} aria-hidden="true" />
              Back
            </button>
          ) : (
            <span />
          )}
          {!last ? (
            <button type="submit" className="btn btn-primary btn-lg">
              Next: {STEPS[step + 1].title}
              <ArrowRight size={22} aria-hidden="true" />
            </button>
          ) : (
            <button type="submit" className="btn btn-primary btn-lg" disabled={!!remaining || busy} aria-describedby="submit-why">
              See my result
              <ArrowRight size={22} aria-hidden="true" />
            </button>
          )}
        </div>
        {last && (
          <p id="submit-why" className={`submit-why${remaining ? '' : ' is-ready'}`}>
            {remaining
              ? `Answer ${remaining === 1 ? 'the last question' : `all ${remaining} remaining questions`} to see your result.`
              : 'All done. Press the button to see your result.'}
          </p>
        )}
      </form>

      <AnimatePresence>
        {busy && (
          <motion.div className="checking" role="status" aria-live="polite" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="checking-card">
              <CoinSpinner size={84} label="Checking your answers" />
              <p className="checking-title">Checking your answers…</p>
              <p>This takes a few seconds.</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
