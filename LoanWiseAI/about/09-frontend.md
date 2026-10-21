# 09 · Frontend

> **In short.** The **frontend** is the part of LoanWise AI you see: the pages, questions, buttons and the result. It is a set of files your browser downloads from the LoanWise server and then runs on your own phone or computer. Its look is based on an Indian bank **passbook and rubber stamp**: the verdict is stamped onto a paper slip in indigo or green. Every screen was written for someone who has never applied for a loan: three short screens of big buttons to tap, money boxes that only accept digits and add commas for you, a "?" button that explains every difficult question, red messages under any question that needs fixing, and a result that says the verdict in a sentence, how sure it is, why, and the monthly payment. Part A walks through every screen in plain words, with screenshots. Part B, for the technically curious, covers how it is built: React components, page addresses, saving answers in the tab, talking to the server, number formatting, animations, accessibility details and the esbuild build.

---

## Contents

**Part A: the plain story**

- [A1. The words you need](#a1-the-words-you-need)
- [A2. Design concept](#a2-design-concept)
- [A3. Page-by-page walkthrough](#a3-page-by-page-walkthrough)
- [A4. Making it usable for everyone](#a4-making-it-usable-for-everyone)

**Part B: for the technically curious**

- [B1. Folder and component structure](#b1-folder-and-component-structure)
- [B2. Routing](#b2-routing)
- [B3. State and persistence](#b3-state-and-persistence)
- [B4. The API client](#b4-the-api-client)
- [B5. Layer-1 validation](#b5-layer-1-validation)
- [B6. Indian number formatting](#b6-indian-number-formatting)
- [B7. Animations and reduced motion](#b7-animations-and-reduced-motion)
- [B8. SVG illustrations](#b8-svg-illustrations)
- [B9. Accessibility in detail](#b9-accessibility-in-detail)
- [B10. Build tooling: esbuild instead of Vite](#b10-build-tooling-esbuild-instead-of-vite)
- [B11. How to develop and build](#b11-how-to-develop-and-build)
- [B12. Limitations](#b12-limitations)

---

# Part A: the plain story

## A1. The words you need

| Word | Meaning in this chapter |
|---|---|
| **Browser** | The app used to open websites: Chrome, Safari, Edge, Firefox. |
| **Frontend** | The part of a system that people see and use. Here: the LoanWise website. |
| **Backend** or **server** | The program on the LoanWise computer that does the checking and prediction. See [08](08-backend.md). |
| **HTML** | The text format that describes what is on a web page: headings, paragraphs, buttons, input boxes. |
| **CSS** | The text format that describes how a page looks: colours, fonts, sizes, spacing, layout. |
| **JavaScript** | The programming language browsers run. It makes pages react: checking answers as you type, switching screens, sending answers to the server. |
| **React** | A JavaScript library (ready-made code) for building pages out of reusable parts called **components**. A component is one self-contained part of the screen, for example "a question with its buttons and error message". When the data behind it changes, React redraws only the parts that changed. |
| **Single-page app** | A website where the browser loads one page once, and moving between screens is done by JavaScript without loading a new page from the server. LoanWise's screens `/`, `/check`, `/result`, `/how-it-works` and `/history` all work this way. |
| **Address** (URL) | The text in the address bar, for example `/check`. Each screen has its own. |
| **Validation** | Checking that an answer is present and makes sense. |
| **Toast** | A small message box that slides in at the bottom of the screen and disappears on its own. |
| **Screen reader** | Software that reads the screen aloud, used by people who are blind or have low vision. |
| **Accessibility** | Making the website usable by everyone, including people who use a screen reader, use only a keyboard, have low vision or are sensitive to motion. |
| **Animation** | Movement on screen, for example the stamp dropping onto the slip. |

## A2. Design concept

### A2.1 The idea: passbook and rubber stamp

Many first-time borrowers in India have dealt with a bank mainly through a **passbook** and a counter clerk who **stamps** documents. The interface borrows that familiar, trustworthy imagery instead of a generic "fintech dashboard":

* The result appears on a **paper slip** with a perforated top edge.
* The verdict is a **rubber stamp** ("LIKELY APPROVED" / "NOT LIKELY YET") that lands with a small spring and a shake, with an SVG noise filter that gives it uneven ink.
* Approvals get a light shower of **marigold petals** (a celebratory flower in India); rejections get a **sprout in a pot** and the line "A 'no' today is not a 'no' forever."

### A2.2 Colours

Defined once as CSS custom properties in [../frontend/src/styles.css](../frontend/src/styles.css) and reused by the SVG art.

| Token | Hex | Role | Why |
|---|---|---|---|
| `--ink` | `#1d2675` | Brand, headings, stamp for "not yet" | Stamp-pad indigo; serious and trustworthy without being black |
| `--text` | `#1c2142` | Body text | Near-black with an indigo tint |
| `--paper` | `#f4f5fb` | Page background | Cool paper, softer than pure white |
| `--mist` | `#e5e7f6` | Washes behind art | The lavender of the ₹100 note |
| `--marigold` | `#f5a81c` | Primary buttons, accents, petals | Warm, festive, high-visibility call to action |
| `--leaf` | `#0d7a54` | Approval stamp and positive reasons | Green for "yes" without the alarmism of traffic-light red/green |
| `--kumkum` | `#b8243d` | Errors | A deep vermilion; clearly "attention" but less aggressive than pure red |

Rejections are deliberately shown in **indigo, not red**: a rejection is not an error by the user, and the tone (`result-soft`) is meant to be kind.

Measured contrast ratios (WCAG 2 formula, computed for this document): body text on paper 14.3:1, ink on paper 12.2:1, muted text on paper 6.1:1, error red on white 6.3:1, leaf on white 5.3:1, ink on the marigold primary button 6.6:1. All exceed the 4.5:1 AA requirement for normal text.

### A2.3 Typefaces

| Font | Used for | Why |
|---|---|---|
| **Baloo 2** (Ek Type, an Indian type foundry), variable weight 400-800 | Headings, buttons, numbers | Friendly, rounded, designed in India with Devanagari companions; feels local rather than corporate |
| **Atkinson Hyperlegible** (Braille Institute), regular and bold | Body text | Designed specifically for low-vision readers: letters that are easy to confuse (I/l/1, O/0, rn/m) are deliberately distinct |

A detail worth mentioning in a viva: Atkinson Hyperlegible's zero has a slash, which many readers mistake for "Ø". The `@font-face` rules therefore set a `unicode-range` that **excludes digits** (U+0030-0039), so numbers fall back to Baloo 2. Money always reads as plain digits. Both fonts are self-hosted `.woff` files under SIL Open Font License ([../frontend/src/assets/fonts](../frontend/src/assets/fonts)), so the app works offline and makes no third-party font requests. `font-display: swap` shows text immediately in a system font while the custom one loads.

### A2.4 "Built for the dumbest person alive"

The client's brief was that anyone, with no financial or technical background, must be able to use the app. Concretely in the frontend this meant:

* Questions in everyday words: "How many people depend on your money?", "Did you finish college?", "How do you earn your money?" rather than "Dependents", "Education", "Self_Employed".
* Every jargon-ish question has a "?" button with a plain explanation (e.g. what counts as a dependent, what a co-applicant is, loan amount vs monthly payment).
* Taps instead of typing for 8 of the 11 answers; numbers only for the 3 money fields.
* Money typed as digits only, with commas added automatically and the amount in words underneath ("That's ₹25 lakh a month.").
* One idea per screen step; the button says where it goes ("Next: Your money").
* Errors say exactly what to do ("Please tap 'Yes' or 'No'.") on the exact field, all at once.
* A "Fill an example for me" button for people who just want to see what happens.
* The result leads with a sentence, not a number.

See [01-what-and-why.md](01-what-and-why.md) for how this principle shaped the whole project.

---

## A3. Page-by-page walkthrough

Screenshots are in [../docs/screenshots](../docs/screenshots), taken at computer-screen size (1440 × 900 pixels) and phone size (390 × 844 pixels). Each screen has its own address, shown after its name.

One caution. The screenshots were taken with a **stand-in server** ([../frontend/scripts/mock-api.mjs](../frontend/scripts/mock-api.mjs)): a small fake server that returns made-up results, used to design the screens without running the real prediction program. So the reason sentences and numbers on the result screenshots are made up. The layout and behaviour are the same as with the real server. The real server's reply for the same person is shown in [02](02-how-it-works-end-to-end.md#step-9-the-server-sends-the-response).

### Home `/`

![Home](../docs/screenshots/home-desktop.png)

The first screen. A single question as the headline ("Will the bank say yes to your home loan?"), one big button ("Check my loan chances"), and a reassurance line: "Free. No sign-up. Nothing is sent to any bank." Below: a three-tile "How it works" strip and the disclaimer. The hero illustration is a passbook, a house and a coin with one stamp moment. Phone: [home-mobile.png](../docs/screenshots/home-mobile.png), menu: [mobile-menu-mobile.png](../docs/screenshots/mobile-menu-mobile.png).

### Check (the wizard) `/check`

The questions are split over three screens, called steps. A row of numbered circles at the top shows which step you are on, with a bar that fills up as you go. This step-by-step form is often called a **wizard**.

| Step | Title | Questions |
|---|---|---|
| 1 | About you | Man or woman; married; how many people depend on your money (None / 1 / 2 / 3 or more); did you finish college; how do you earn your money (salary / work for myself) |
| 2 | Your money | Monthly income; co-applicant's monthly income (with a "No one" chip); paid past loans on time (Yes / No, late / Never had a loan or card) |
| 3 | Your loan | How much to borrow; how many years (10 cards: 1 to 40 years); where the house is (city / near a city / village) |

| Empty | Errors after pressing Next | Money step with help open | Ready to submit |
|---|---|---|---|
| ![](../docs/screenshots/check-empty-desktop.png) | ![](../docs/screenshots/check-errors-desktop.png) | ![](../docs/screenshots/check-money-desktop.png) | ![](../docs/screenshots/check-loan-ready-desktop.png) |

Behaviours:

* **Fill an example for me** asks the server for a real past application (from the example file) and fills in every answer with it, then goes back to step 1 and shows a short message. If the example had blank answers, the message says how many you need to tap yourself.
* **Clear answers** appears once anything has been answered.
* Choosing "No, I was late" or "I never had a loan" shows a gentle note under the question.
* While waiting for the server, the screen shows "Checking your answers…" with a spinning coin, for at least 0.9 seconds so the moment is noticeable (no wait if "reduce motion" is on).
* If the server finds a problem the website missed (it replies with status 422, "some answers need fixing"), the form jumps back to that step and shows the server's message under the question: [server-422-desktop.png](../docs/screenshots/server-422-desktop.png).
* If the server cannot be reached, a message box titled **"Your answers are safe"** explains, and nothing typed is lost: [network-error-desktop.png](../docs/screenshots/network-error-desktop.png).

### Result `/result`

| Approved | Not likely yet |
|---|---|
| ![](../docs/screenshots/result-approved-desktop.png) | ![](../docs/screenshots/result-rejected-desktop.png) |

Left: the slip with "Your result, check number N", the stamp, the headline, a confidence ring (percentage plus "High/Medium/Low") and one sentence on what that means. Right: "Why we said this" (reasons with thumbs up / thumbs down / info icons), "Things we fixed for you" (server warnings, if any), the monthly payment card ("Your monthly payment would be about ₹22,493 a month … This is a rough guess. The bank's real interest rate will change it."), and two actions: **Try again with changes** (back to the wizard with answers kept) and **Start fresh** (answers cleared). If someone opens `/result` directly with nothing saved, a friendly empty state links to the wizard.

### How it works `/how-it-works`

![How it works](../docs/screenshots/how-it-works-desktop.png)

A four-node animated flow (You answer → We check them → The model decides → You get an answer), then real figures read from the training report on the server: the dataset split (614 applications, 422 yes, 192 no) as a bar, a bar chart comparing the models by accuracy or F1 (toggle) with a "We use this one" badge on the chosen model, and the six answers that most influence the model, translated into plain words (for example "Credit History" → "Paid past loans on time"). If the server cannot be reached it shows a notice with a retry button and keeps the explanation: [how-it-works-no-api-desktop.png](../docs/screenshots/how-it-works-no-api-desktop.png).

### Past checks `/history`

| List | Delete confirmation | Empty |
|---|---|---|
| ![](../docs/screenshots/history-desktop.png) | ![](../docs/screenshots/history-confirm-desktop.png) | ![](../docs/screenshots/history-empty-desktop.png) |

Up to 50 past checks from the server, newest first. Each card shows: verdict pill, date in Indian format, loan, term in years, total family income and "how sure". **Delete all** opens an inline confirmation ("Delete all 3 past checks? You can't undo this.") with focus moved to the safe choice, "No, keep them". While loading, grey placeholder cards are shown; if loading fails, a notice with a "Try again" button.

### Not found `*`

![Not found](../docs/screenshots/not-found-desktop.png) Any unknown address shows a "lost" illustration and a button home.

---

## A4. Making it usable for everyone

These are the things a user notices, without the technical terms. Part B, section B9, lists how each is built.

* **Large text and clear letters.** The main text is 18 pixels high and uses a typeface designed for people with low vision.
* **Strong colour contrast.** Every text colour was measured against its background and is easy to read (all at least 4.5 times as bright or dark as the background, the international minimum for normal text).
* **Colour is never the only signal.** "Helps you" and "hurts your chances" reasons have different icons, not just different colours.
* **Large buttons.** The main buttons are 44 to 48 pixels tall and the answer cards 58 to 68 pixels, so they are easy to tap with a thumb.
* **Works with a keyboard alone.** Tab moves between controls, arrow keys move between choices, Escape closes pop-ups. A "Skip to main content" link appears first for keyboard users.
* **Works with a screen reader.** Every question, button and error is announced. When an error appears, it is read out. The result reasons are read with "Helps you:", "Hurts your chances:" or "Good to know:" in front.
* **Respects "reduce motion".** If you have turned on "reduce motion" in your phone or computer settings, the falling petals, sliding screens and counting numbers are switched off and results appear instantly.
* **Nothing lost on refresh.** If you refresh the page or the connection drops, your answers stay. They are deleted when you close the tab.
* **Number keypad on phones.** Money boxes open the number keypad, not the full keyboard.

---

# Part B: for the technically curious

Everything below is engineering detail. A non-technical reader can stop here without losing the story.

## B1. Folder and component structure

```
frontend/
├── index.html               template; <!--STYLES--> and <!--SCRIPTS--> are replaced at build
├── package.json             5 runtime deps, 1 dev dep (esbuild)
├── public/favicon.svg       copied into dist as-is
├── scripts/
│   ├── esbuild.config.mjs   shared build options + renderHtml() (injects hashed asset tags)
│   ├── build.mjs            npm run build -> dist/
│   ├── dev.mjs              npm run dev -> watch, live reload, /api proxy
│   ├── mock-api.mjs         npm run mock -> fake API + dist on :5055, for UI work without Python
│   └── screenshots.mjs      npm run shots -> Playwright screenshots of every state
├── src/
│   ├── main.jsx             createRoot + <BrowserRouter> + <StrictMode>
│   ├── App.jsx              routes, page titles, page transitions, MotionConfig, ToastProvider
│   ├── api.js               fetch wrapper with timeouts and friendly ApiError
│   ├── styles.css           all styles (~2,100 lines), design tokens on :root
│   ├── lib/
│   │   ├── fields.js        wizard steps, layer-1 rules, payload <-> answers mapping
│   │   ├── format.js        Indian grouping, ₹, "2.5 lakh", dates, percent, years
│   │   └── storage.js       sessionStorage helpers that never throw
│   ├── components/
│   │   ├── inputs.jsx       ChoiceGroup, MoneyInput, FieldError, "?" help bubble
│   │   ├── layout.jsx       Nav (desktop + mobile menu), Footer, skip link
│   │   ├── bits.jsx         Disclaimer, Skeleton, ConfidenceRing, useCountUp, PageHead
│   │   ├── toast.jsx        ToastProvider / useToast (max 3, de-duplicated)
│   │   └── art.jsx          hand-drawn SVGs: logo, hero, stamp, petals, sprout, empty, lost, coin spinner
│   ├── pages/               Home, Check, Result, HowItWorks, History, NotFound
│   └── assets/fonts/        Baloo 2 and Atkinson Hyperlegible .woff + licences
└── dist/                    pre-built output committed so Node is optional for users
```

Runtime dependencies ([../frontend/package.json](../frontend/package.json)): `react` and `react-dom` ^19.2.8, `react-router-dom` 6.28.0, `framer-motion` 11.11.17, `lucide-react` 0.460.0 (icons). Dev: `esbuild` ^0.28.2. That is the entire toolchain.

The production bundle (from `frontend/dist/assets`): JS 414 KB minified (before gzip), CSS 32 KB, three fonts 19-38 KB each.

---

## B2. Routing

[../frontend/src/App.jsx](../frontend/src/App.jsx):

| Path | Component | `document.title` |
|---|---|---|
| `/` | `Home` | LoanWise AI: check your loan chances |
| `/check` | `Check` | Check my chances \| LoanWise AI |
| `/result` | `Result` | Your result \| LoanWise AI |
| `/how-it-works` | `HowItWorks` | How it works \| LoanWise AI |
| `/history` | `History` | Past checks \| LoanWise AI |
| `*` | `NotFound` | Page not found \| LoanWise AI |

Each route is wrapped in `<Page>`, a framer-motion fade/slide, inside `<AnimatePresence mode="wait">` keyed by pathname, so the old page fades out before the new one fades in. On every navigation the title is updated and the window scrolls to the top. Data passes between pages through router `state` (e.g. the result object from Check to Result) with sessionStorage as the fallback after a refresh.

Server side, Flask's SPA fallback ([../src/loanwise/api/spa.py](../src/loanwise/api/spa.py)) returns `index.html` for any non-file, non-API path, so deep links work.

---

## B3. State and persistence

There is no global state library. Each page keeps its own React state; three pieces are mirrored to `sessionStorage` through [../frontend/src/lib/storage.js](../frontend/src/lib/storage.js):

| Key | Written by | Contains | Why |
|---|---|---|---|
| `loanwise:answers` | Check, on every change | The 11 wizard answers | A refresh, an accidental back, or a network error never loses typing |
| `loanwise:step` | Check | Current step index (clamped 0..2 on load) | Reopen on the step you were on |
| `loanwise:result` | Check, after a successful predict | `{result, answers}` | `/result` survives a refresh |

Every storage call is wrapped in `try/catch`. In private browsing or when storage is blocked, the app still works; it just forgets on reload. sessionStorage (not localStorage) was chosen because loan answers are personal: they disappear when the tab closes, which suits a shared or family computer. "Start fresh" removes answers and step; "Clear answers" resets the form.

Answers in state are kept in UI form (strings, `credit_choice` with three options). `toPayload()` converts them to the API contract (numbers, `credit_history` good/bad) only at submit time; `fromPayload()` does the reverse for samples, validating each value against the allowed list so a bad sample can never put the form into an impossible state.

---

## B4. The API client

[../frontend/src/api.js](../frontend/src/api.js) is a thin `fetch` wrapper. Every failure becomes an `ApiError` with a `kind` the UI can act on and a message a person can read:

| Situation | `kind` | Message |
|---|---|---|
| No response (server down, offline) | `network` | We couldn't reach the server. Is it running? |
| Request exceeded its timeout | `timeout` | The server is taking too long to answer. Please try again in a moment. |
| 422 | `validation` | Server's `message`, plus `errors` per field |
| 502 / 503 / 504, or 404 with no JSON body (a proxy with no backend) | `network` | We couldn't reach the server. Is it running? |
| Other non-OK with a JSON body | `server` | Server's `message` |
| Non-OK and unreadable body | `bad-response` | Something went wrong on our side. Please try again. |

Timeouts use `AbortController`: 15 s by default, 20 s for `predict`, 5 s for `health`.

| Method | Call |
|---|---|
| `api.predict(answers)` | `POST /api/predict` |
| `api.sample()` | `GET /api/sample` |
| `api.history(limit = 50)` | `GET /api/history?limit=50` |
| `api.clearHistory()` | `DELETE /api/history` |
| `api.modelInfo()` | `GET /api/model-info` |
| `api.health()` | `GET /api/health` |

All calls use relative URLs (`/api/...`), so the same build works behind Flask, the dev proxy, the mock server or any domain.

---

## B5. Layer-1 validation

Full rule table and messages: [07-validation-and-guardrails.md, section B1](07-validation-and-guardrails.md#b1-layer-1-the-browser-form). Summary of how it is wired:

* `validateField(name, answers)` returns one message or `''`; `validateStep(i, answers)` and `validateAll(answers)` collect them.
* Choice questions validate as soon as they are tapped. Money fields validate on blur, then live once touched.
* **Next** validates the step, shows a count banner ("2 answers need fixing. Look for the red boxes."), scrolls to and focuses the first problem.
* **See my result** stays disabled until `validateAll` is empty, with a live line under it saying how many questions remain.
* Server 422 errors are mapped back to fields (`credit_history` → `credit_choice`) and the wizard jumps to the earliest affected step.

The UI never trusts itself: the server re-validates everything (layer 2).

---

## B6. Indian number formatting

[../frontend/src/lib/format.js](../frontend/src/lib/format.js) uses the browser's built-in `Intl.NumberFormat('en-IN')`, which groups digits the Indian way: the last three digits, then pairs.

| Function | Input | Output |
|---|---|---|
| `groupIN` | 2500000 | `25,00,000` |
| `rupees` | 2500000 | `₹25,00,000` (and `—` for empty) |
| `inWords` | 2500000 / 250000 / 48000 / 10000000 | `25 lakh` / `2.5 lakh` / `48 thousand` / `1 crore` |
| `percent` | 0.8521 | `85%` |
| `yearsLabel` | 240 | `20 years` (`1 year` for 12) |
| `niceDate` | ISO string | e.g. `21 Oct 2026, 3:57 pm` (en-IN locale) |

The server has a matching `format_inr()` in [../src/loanwise/domain/formatting.py](../src/loanwise/domain/formatting.py) for the messages it writes.

`MoneyInput` re-formats on every keystroke and keeps the caret in the right place: before re-rendering it counts how many digits are to the right of the caret, then after formatting walks back from the end until it has passed that many digits. Without this, inserting a comma would throw the cursor to the end of the field.

---

## B7. Animations and reduced motion

Animations use **framer-motion**. They exist to make cause and effect obvious (the stamp lands, the payment counts up), not as decoration.

| Animation | Where |
|---|---|
| Page fade/slide (0.28 s) | Every route change |
| Wizard steps slide left/right according to direction | Check |
| Spring-animated progress bar | Check |
| Error messages and help bubbles fade/expand in | Inputs |
| Stamp drops with a spring from 2.2× scale and rotates to −7°; the slip shakes slightly | Result |
| Confidence ring draws and the percentage counts up; EMI counts up | Result |
| Reasons stagger in | Result |
| Marigold petals fall (30 petals, deterministic pseudo-random paths) | Result, approved only |
| Sprout draws itself (`pathLength`) | Result, not approved |
| Flow nodes pop in on scroll; a dot travels along the connector | How it works |
| Bar charts grow | How it works |
| Toasts spring in; at most 3; duplicates removed | Everywhere |

**Reduced motion** is respected at three levels:

1. `<MotionConfig reducedMotion="user">` in `App.jsx` tells framer-motion to drop transform animations when the operating system's "reduce motion" setting is on.
2. Components call `useReducedMotion()` and skip or shorten effects explicitly: no petals at all, the stamp appears in place, count-ups show the final number immediately, the wizard does not slide, the travelling dot is not rendered, the "checking" delay is 0, and scrolling is instant.
3. A CSS `@media (prefers-reduced-motion: reduce)` rule cuts all CSS animations and transitions to 0.01 ms.

---

## B8. SVG illustrations

All artwork is hand-written SVG in [../frontend/src/components/art.jsx](../frontend/src/components/art.jsx): no image files, no icon fonts, no external requests. Colours come from the CSS variables, so the palette lives in one place.

| Component | What it draws |
|---|---|
| `LogoMark` | A coin with a dashed marigold rim, a roof and a tick (also the favicon) |
| `ManIcon`, `WomanIcon` | Simple figures in the Lucide icon style, for the gender cards |
| `Rupee` | The ₹ sign as a path, so it never depends on a font having the glyph |
| `HeroArt` | Passbook, house and coin with a stamp moment (home page) |
| `VerdictStamp` | Double-bordered stamp with the label; an `feTurbulence` + `feColorMatrix` filter knocks out specks to imitate uneven ink |
| `Petals` | Marigold petals and leaves for approvals |
| `SproutArt` | Plant in a pot with sun rays, for "not likely yet" |
| `EmptyArt`, `LostArt` | Empty states and 404 |
| `CoinSpinner` | Loading indicator while checking |

Decorative SVGs have `aria-hidden="true"`; meaningful ones (`VerdictStamp`, `SproutArt`) have `role="img"` and an `aria-label` such as "Stamp: Likely approved". Interface icons come from `lucide-react`.

---

## B9. Accessibility in detail

| Area | What is done |
|---|---|
| **Semantic HTML** | `<header>`, `<nav aria-label="Main">`, `<main id="main">`, `<footer>`, `<section aria-labelledby>`, headings in order, `<ol>` for steps, `<dl>` for history facts |
| **Skip link** | "Skip to main content" is the first focusable element |
| **Native controls** | Choice cards are real `<input type="radio">` inside `<label>`, grouped in `role="radiogroup"` with `aria-labelledby`; arrow keys, Space and screen readers work as expected. Money fields have a real `<label for>` |
| **Errors** | Each field's error is in an `aria-live="polite"` region and linked by `aria-describedby`; fields get `aria-invalid="true"`. The form banner is `role="alert"` in an `aria-live="assertive"` slot |
| **Focus management** | On step change, focus moves to the step heading (`tabIndex={-1}`); on errors, to the first invalid field; in the delete confirmation, to "No, keep them"; Escape closes help bubbles, the mobile menu and the confirmation, returning focus to the trigger |
| **Visible focus** | `:focus-visible` draws a 3 px paper + 3 px ink double ring; choice cards show it via `:has(input:focus-visible)` |
| **Status announcements** | The checking overlay is `role="status"`; toasts are `role="alert"` (errors) or `role="status"`; history loading has a screen-reader-only "Loading your past checks" |
| **Screen-reader text** | `.sr-only` spans: stepper "(done)" / "(you are here)", reason prefixes "Helps you:" / "Hurts your chances:" / "Good to know:", "What does '…' mean?" on help buttons, "Close message" on toasts |
| **Contrast** | All text pairs ≥ 4.5:1 (see A2.2); state is never shown by colour alone (icons + words) |
| **Forced colours** | `@media (forced-colors: active)` adds a `Highlight` outline to the selected card and borders to buttons for Windows High Contrast |
| **Touch targets** | Main buttons 44-48 px high (`.btn`, `.btn-quiet`, nav links, menu button); small secondary controls ("Got it", the metric toggle) 40 px; choice cards 58-68 px |
| **Readable type** | Base font size 18 px (`1.125rem`), line height 1.6, Atkinson Hyperlegible for body |
| **Mobile** | `inputMode="numeric"` brings up the number keypad; layouts reflow at 920/860/760/720/560/460/420 px; the screenshot script checks for horizontal overflow at 390 px |
| **Language** | `<html lang="en-IN">`; `<noscript>` message if JavaScript is off |

What has **not** been done: no formal audit with a screen reader user or an automated axe/Lighthouse run is recorded in the repository. The measures above are by construction.

---

## B10. Build tooling: esbuild instead of Vite

**What a bundler does.** The browser cannot efficiently load 200 separate JSX files and React's source. A bundler converts JSX to plain JavaScript, follows every `import`, combines everything into one file, minifies it, gives it a content hash in its name (so browsers can cache it forever), and copies fonts and images.

**Vite** is the usual choice for a React app in 2026. This project uses **esbuild directly** (Vite itself uses esbuild internally for development). The repository does not record a written rationale, so the following are the practical reasons that follow from the code:

| Consideration | esbuild directly |
|---|---|
| Dependencies | One dev dependency (`esbuild`), a single native binary. Vite adds a larger dependency tree, which matters for a student's laptop, a locked-down corporate network, and supply-chain review |
| What the app needs | JSX, CSS import, font files, minification, hashing, a dev proxy. All of this is about 150 lines of scripts in [../frontend/scripts](../frontend/scripts) |
| Speed | A full production build takes well under a second |
| Transparency | Every build step is visible in plain Node scripts that an engineer can read in five minutes; no plugin configuration to learn |
| Trade-off | No hot module replacement (the dev server does a full page reload on change), no plugin ecosystem; fine for an app of this size |

How it works:

* [esbuild.config.mjs](../frontend/scripts/esbuild.config.mjs): entry `src/main.jsx`, `bundle`, `format: 'esm'`, `target: 'es2020'`, automatic JSX runtime, loaders for `.woff/.woff2/.svg/.png` as files, `[name]-[hash]` names in production, minify in production, inline source maps in development, `process.env.NODE_ENV` defined. `useDefineForClassFields: false` is set because framer-motion relies on TypeScript's legacy class-field semantics. `renderHtml()` replaces `<!--STYLES-->` and `<!--SCRIPTS-->` in `index.html` with the hashed file names from esbuild's metafile.
* [build.mjs](../frontend/scripts/build.mjs): wipes `dist/`, builds, writes `dist/index.html`, copies `public/`, prints file sizes.
* [dev.mjs](../frontend/scripts/dev.mjs): esbuild watch mode plus its built-in server on port `PORT + 1000`, wrapped in a tiny Node HTTP server on `PORT` (default **5173**) that proxies `/api/*` to `API_TARGET` (default `http://localhost:5000`), serves `public/` files, and injects an `EventSource('/esbuild')` script that reloads the page when a rebuild finishes. If Flask is not running, the proxy answers 502 with `{"ok": false, "message": "We couldn't reach the server. Is it running?"}`, which `api.js` maps to the network error.

Note: [../docs/API.md](../docs/API.md) still says "Vite dev proxies /api → 5000"; the dev proxy is in fact `frontend/scripts/dev.mjs` (esbuild), with the same port and behaviour.

---

## B11. How to develop and build

You only need Node.js (18+) to **change** the frontend; a pre-built `frontend/dist` ships with the repository and `./run.sh` builds it automatically if it is missing.

```bash
cd frontend
npm install

# Live-reload UI on http://localhost:5173, /api proxied to Flask on :5000
npm run dev                       # start Flask separately: python3 scripts/run_server.py

# Point the dev server at another backend (e.g. the mock)
API_TARGET=http://localhost:5055 npm run dev

# UI work without Python: fake API + built dist on http://localhost:5055
npm run build && npm run mock     # MOCK_EMPTY=1 for empty history, MOCK_NO_MODEL=1 for a 503 model-info

# Production build -> frontend/dist (Flask serves it at /)
npm run build

# Regenerate docs/screenshots (needs Playwright + Chromium, and the mock running)
npm run shots
```

The mock API is a "throwaway" helper for UI work: its validation messages, reasons and verdict wording ("Likely Not Approved") differ from the real backend's, and it has a test hook (a loan of exactly ₹4,04,040 returns a 422) used for the server-error screenshot. Always confirm behaviour against the real Flask API.

---

## B12. Limitations

* **Screenshots show mock data.** Wording on the result screenshots differs from the real API (for example, real reasons say "The monthly payment (about ₹22,493) is 32% of your income — manageable, but not small.").
* **No automated frontend tests.** Behaviour is checked by the screenshot script (which also reports page errors, console errors and horizontal overflow) and by the backend integration tests of the API contract. A component test suite (Vitest/Testing Library) or Playwright assertions would be the next step.
* **Layer-1 rules are duplicated** from the Python limits; see [07, section B10](07-validation-and-guardrails.md#b10-limitations-and-honest-caveats).
* **English only**, although the fonts and number formats are Indian. Hindi and other languages would need a translation layer for both UI and server messages.
* **No dark mode** and no offline/PWA support.
* **Bundle size** (414 KB minified JS) is dominated by React and framer-motion; code-splitting the How-it-works and History pages would reduce first load.

---

[Next → 10 · Glossary](10-glossary.md)  
[← Back to index](README.md)
