// Every question in the wizard, in plain English, plus layer-1 validation.
// Values stored here match the API contract exactly (see docs/API.md),
// except `credit_choice`, which is UI-only and maps to `credit_history`.

export const TERM_YEARS = [1, 3, 5, 7, 10, 15, 20, 25, 30, 40];
export const MAX_MONEY = 10_000_000; // ₹1 crore
export const MIN_LOAN = 1_000;

export const EMPTY = {
  gender: '',
  married: '',
  dependents: '',
  education: '',
  self_employed: '',
  applicant_income: '',
  coapplicant_income: '',
  credit_choice: '', // 'yes' | 'no' | 'never'
  loan_amount: '',
  loan_term: '',
  property_area: '',
};

export const STEPS = [
  {
    id: 'you',
    title: 'About you',
    short: 'You',
    intro: 'A few quick taps about you and your family.',
    fields: ['gender', 'married', 'dependents', 'education', 'self_employed'],
  },
  {
    id: 'money',
    title: 'Your money',
    short: 'Money',
    intro: 'How much comes in each month, and how you have handled loans before.',
    fields: ['applicant_income', 'coapplicant_income', 'credit_choice'],
  },
  {
    id: 'loan',
    title: 'Your loan',
    short: 'Loan',
    intro: 'Tell us about the loan you want.',
    fields: ['loan_amount', 'loan_term', 'property_area'],
  },
];

/** Map the UI's credit answer to the contract value. */
export function creditToApi(choice) {
  if (choice === 'no') return 'bad';
  if (choice === 'yes' || choice === 'never') return 'good';
  return '';
}
export function creditFromApi(value) {
  if (value === 'bad') return 'no';
  if (value === 'good') return 'yes';
  return '';
}

const digits = (v) => String(v ?? '').replace(/[^\d]/g, '');

/** Validate one field given all answers. Returns a message or ''. */
export function validateField(name, a) {
  const v = a[name];
  switch (name) {
    case 'gender':
      return v ? '' : 'Please tap "Man" or "Woman".';
    case 'married':
      return v ? '' : 'Please tap "Yes" or "No".';
    case 'dependents':
      return v ? '' : 'Please tap how many people depend on you. Tap "None" if nobody does.';
    case 'education':
      return v ? '' : 'Please tap whether you finished college.';
    case 'self_employed':
      return v ? '' : 'Please tap how you earn your money.';
    case 'credit_choice':
      return v ? '' : 'Please tap one answer about past loans.';
    case 'loan_term':
      return v ? '' : 'Please tap how many years you want to pay the loan back over.';
    case 'property_area':
      return v ? '' : 'Please tap where the house is.';
    case 'applicant_income': {
      if (digits(v) === '') return 'Please type how much you earn each month. Type 0 if you earn nothing.';
      const n = Number(digits(v));
      if (n > MAX_MONEY) return 'That is more than ₹1 crore a month. Please check the number. Did you type the yearly amount?';
      const co = Number(digits(a.coapplicant_income) || 0);
      if (n === 0 && co === 0 && digits(a.coapplicant_income) !== '')
        return 'Someone has to earn money for a loan. Type your income here, or the other person\'s income below.';
      return '';
    }
    case 'coapplicant_income': {
      if (digits(v) === '') return 'Please type the other person\'s monthly income. Type 0 if no one else is helping.';
      const n = Number(digits(v));
      if (n > MAX_MONEY) return 'That is more than ₹1 crore a month. Please check the number.';
      return '';
    }
    case 'loan_amount': {
      if (digits(v) === '') return 'Please type how much money you want to borrow.';
      const n = Number(digits(v));
      if (n < MIN_LOAN) return 'The smallest loan we can check is ₹1,000.';
      if (n > MAX_MONEY) return 'The biggest loan we can check is ₹1,00,00,000 (1 crore).';
      return '';
    }
    default:
      return '';
  }
}

export function validateStep(stepIndex, a) {
  const errs = {};
  for (const f of STEPS[stepIndex].fields) {
    const m = validateField(f, a);
    if (m) errs[f] = m;
  }
  return errs;
}

export function validateAll(a) {
  return STEPS.reduce((acc, _, i) => ({ ...acc, ...validateStep(i, a) }), {});
}

/** Build the request body exactly as the contract wants it. */
export function toPayload(a) {
  return {
    gender: a.gender,
    married: a.married,
    dependents: a.dependents,
    education: a.education,
    self_employed: a.self_employed,
    applicant_income: Number(digits(a.applicant_income) || 0),
    coapplicant_income: Number(digits(a.coapplicant_income) || 0),
    loan_amount: Number(digits(a.loan_amount) || 0),
    loan_term: Number(a.loan_term),
    credit_history: creditToApi(a.credit_choice),
    property_area: a.property_area,
  };
}

/** Accept a /api/sample (or history `inputs`) object and turn it into wizard answers. */
export function fromPayload(p = {}) {
  const pick = (k, allowed) => (allowed.includes(String(p[k])) ? String(p[k]) : '');
  const money = (k) => (p[k] === null || p[k] === undefined || p[k] === '' || Number.isNaN(Number(p[k])) ? '' : String(Math.round(Number(p[k]))));
  const term = Number(p.loan_term);
  return {
    gender: pick('gender', ['Male', 'Female']),
    married: pick('married', ['Yes', 'No']),
    dependents: pick('dependents', ['0', '1', '2', '3+']),
    education: pick('education', ['Graduate', 'Not Graduate']),
    self_employed: pick('self_employed', ['Yes', 'No']),
    applicant_income: money('applicant_income'),
    coapplicant_income: money('coapplicant_income'),
    loan_amount: money('loan_amount'),
    loan_term: TERM_YEARS.map((y) => y * 12).includes(term) ? String(term) : '',
    credit_choice: creditFromApi(p.credit_history),
    property_area: pick('property_area', ['Urban', 'Semiurban', 'Rural']),
  };
}

/** Field -> which step it lives on (used to jump to server errors). */
export const FIELD_STEP = Object.fromEntries(STEPS.flatMap((s, i) => s.fields.map((f) => [f, i])));
// server uses credit_history; we show it on credit_choice
FIELD_STEP.credit_history = 1;
