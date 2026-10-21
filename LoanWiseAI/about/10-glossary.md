# 10 · Glossary

> **In short:** this is an A to Z list of every word you will meet in LoanWise AI, whether it comes from computing, artificial intelligence, statistics or banking. You do not need any background to use it. Each entry says in plain words what the thing is and what it does. When a definition uses another special word, that word links to its own entry. Most entries end with **In this project:**, which says where the idea appears, with real numbers and a link to the file or chapter that goes deeper. If you are completely new to artificial intelligence, read [00 · AI from zero](00-ai-from-zero.md) first. Numbers come from `artifacts/models/model_info.json`, `data/raw/loan.csv` and the code, as of the training run on 2026-10-20.

**Jump to:** [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) · [W](#w)

**Start here if you are new:** [data](#data) → [dataset](#dataset) → [row](#row) and [column](#column) → [feature](#feature) and [label](#label) → [machine learning](#machine-learning) → [training](#training) → [model](#model) → [prediction](#prediction) → [probability](#probability) → [accuracy](#accuracy).

---

## A

<a id="accuracy"></a>
**Accuracy**
The share of a [model](#model)'s answers that turned out to be right, worked out as `number of correct answers ÷ number of answers`. It can look good even when the model is not very useful, if one answer is much more common than the other (see [class imbalance](#class-imbalance)).
*Example:* the model was right about 105 of 123 test applications, so its accuracy is 105 ÷ 123 = 0.8537, or 85.37 %.
*In this project:* the main score used to compare the three models. On the 123-row [hold-out set](#hold-out-set) all three score 0.8537; with [cross-validation](#cross-validation) they score 0.7983 ([Logistic Regression](#logistic-regression)), 0.7962 ([Random Forest](#random-forest)) and 0.7840 ([Decision Tree](#decision-tree)). See [../src/loanwise/ml/evaluation.py](../src/loanwise/ml/evaluation.py) and [06 · Training and evaluation](06-training-and-evaluation.md).

<a id="affordability"></a>
**Affordability**
Whether a borrower can realistically pay the monthly instalments out of their income and still live.
*In this project:* measured in two places. The model sees it as the [EMI-to-income ratio](#emi-to-income-ratio). The [guardrails](#guardrail) recalculate it from the applicant's real numbers and reject loans whose monthly payment would be more than 65 % of income ([../src/loanwise/domain/guardrails.py](../src/loanwise/domain/guardrails.py)).

<a id="algorithm"></a>
**Algorithm**
A precise, step-by-step method for doing a task, written so that a computer can follow it exactly. In [machine learning](#machine-learning), an algorithm is the method that looks at past examples and produces a [model](#model).
*In this project:* three algorithms were tried: [Logistic Regression](#logistic-regression), [Decision Tree](#decision-tree) and [Random Forest](#random-forest). See [05 · Algorithms](05-algorithms.md).

<a id="amortised-emi"></a>
**Amortised EMI**
A fixed monthly payment calculated so that, after the last payment, the borrower has repaid both the [principal](#principal) and all the [interest](#interest-rate). The formula is `EMI = P × r × (1 + r)^n ÷ ((1 + r)^n − 1)`, where `P` is the amount borrowed, `r` the interest rate per month and `n` the number of months.
*Example:* ₹25,00,000 borrowed over 240 months at 9 % a year gives an EMI of about ₹22,493.
*In this project:* `estimate_emi()` in [../src/loanwise/domain/guardrails.py](../src/loanwise/domain/guardrails.py) uses an assumed 9 % a year. This is the `emi_estimate` the user sees. The model itself uses a simpler version (see [EMI](#emi)).

<a id="api"></a>
**API (Application Programming Interface)**
A fixed set of [requests](#request-and-response) that one [program](#code) agrees to accept from other programs, and the exact form of the answers it gives back. A web API receives those requests over the internet using [HTTP](#http).
*In this project:* the [server](#server) offers a web API at addresses beginning with `/api`, for example `POST /api/predict` to check a loan. The browser page uses it to get its answers. See [../docs/API.md](../docs/API.md) and [08 · Backend](08-backend.md).

<a id="app-factory"></a>
**App factory**
A [function](#function) whose job is to build and return a complete, configured web application each time it is called, instead of the application being created once, automatically, when the [code](#code) is loaded. It lets tests build applications with different settings.
*In this project:* `create_app(settings=None, *, model=None)` in [../src/loanwise/api/\_\_init\_\_.py](../src/loanwise/api/__init__.py). Tests call it with a fake model or a temporary [database](#database); `wsgi.py` calls it once for the real server.

<a id="artifact"></a>
**Artifact (artefact)**
A [file](#file) that one step of a project produces and a later step uses.
*In this project:* `artifacts/models/loan_model.pkl` (the trained [model](#model)), `artifacts/models/model_info.json` (the training report) and the four chart images in `artifacts/reports/eda/`.

<a id="artificial-intelligence"></a>
**Artificial intelligence (AI)**
The general name for computer [programs](#code) that do tasks which normally need human judgement, such as recognising speech, translating text or estimating an outcome from information. Most AI today is built with [machine learning](#machine-learning): the program's behaviour comes from patterns found in past [data](#data), not from rules a person typed in one by one. An AI program does not think, feel or understand; it calculates.
*In this project:* the "AI" in LoanWise AI is one [machine-learning](#machine-learning) [model](#model) that turns 11 answers about an applicant into a [probability](#probability) of approval, plus hand-written [guardrail](#guardrail) rules. See [00 · AI from zero](00-ai-from-zero.md).

<a id="average"></a>
**Average (mean)**
The total of a list of numbers divided by how many numbers there are. One very large value can pull it up a lot.
*Example:* the mean monthly applicant income in the training data is ₹5,403, but one applicant earns ₹81,000, which pulls the mean well above the [median](#median) of ₹3,812.50.

## B

<a id="bagging"></a>
**Bagging (bootstrap aggregating)**
A way of building one [model](#model) out of many. Each smaller model is trained on a different random selection of [rows](#row) (picked with repeats allowed), and the final answer is the average of all their answers. Averaging makes the result less sensitive to the particular rows that were used.
*In this project:* the [Random Forest](#random-forest) is 300 [decision trees](#decision-tree) built this way ([../src/loanwise/ml/pipelines.py](../src/loanwise/ml/pipelines.py)).

<a id="baseline"></a>
**Baseline**
The score you would get with the simplest possible method. A [model](#model) is only useful if it beats it.
*In this project:* answering "approved" for everyone is right for 85 of the 123 test rows, an [accuracy](#accuracy) of 0.6911. The model's 0.8537 is compared against that. A second simple method, "approve if [credit history](#credit-history) is good", also scores exactly 0.8537 on the same rows.

<a id="binary-classification"></a>
**Binary classification**
A [prediction](#prediction) task with exactly two possible answers.
*In this project:* approved (`Loan_Status = "Y"`, stored as 1) or rejected (`"N"`, stored as 0). See [../src/loanwise/ml/data.py](../src/loanwise/ml/data.py).

<a id="blueprint"></a>
**Blueprint (Flask)**
In [Flask](#flask), a named group of [endpoints](#endpoint) that are added to the application together, usually sharing the start of their web address.
*In this project:* three groups under `/api` (`predict`, `history`, `meta`) and a fourth, `spa`, that sends the website's pages. The `spa` group is added last so it cannot take over `/api` addresses. See [../src/loanwise/api/routes/](../src/loanwise/api/routes/) and [../src/loanwise/api/spa.py](../src/loanwise/api/spa.py).

<a id="browser"></a>
**Browser**
The program on a phone or computer that opens [websites](#website), such as Chrome, Safari, Edge or Firefox. It downloads pages from a [server](#server), shows them, and runs the [JavaScript](#javascript) [code](#code) inside them.
*In this project:* the loan form runs in the user's browser and sends the answers to the LoanWise server.

## C

<a id="calibration"></a>
**Calibration**
How closely a [model](#model)'s [probabilities](#probability) match what really happens. A model is well calibrated if, among all applicants it gives 0.8, about 80 out of every 100 are in fact approved.
*In this project:* not done, so the reported [confidence](#confidence) is the model's own score and has not been checked against real approval rates ([../docs/MODEL_CARD.md](../docs/MODEL_CARD.md)).

<a id="categorical-feature"></a>
**Categorical feature**
A [feature](#feature) whose values are names of groups rather than amounts. You cannot add or average them.
*In this project:* six: Gender, Married, Dependents, Education, Self_Employed and Property_Area ([../src/loanwise/domain/schemas.py](../src/loanwise/domain/schemas.py)). They are turned into numbers by [one-hot encoding](#one-hot-encoding).

<a id="class"></a>
**Class**
One of the possible answers in a [classification](#binary-classification) task.
*In this project:* two classes, "approved" and "rejected".

<a id="class-imbalance"></a>
**Class imbalance**
When one [class](#class) appears much more often than the other in the [data](#data). It makes [accuracy](#accuracy) look better than the model's real skill.
*In this project:* 422 approved and 192 rejected applications, so 68.7 % are approved. [Stratification](#stratification) keeps that mix in every split, and the 0.6911 [baseline](#baseline) is always reported next to accuracy.

<a id="classifier"></a>
**Classifier**
A [model](#model) whose answer is a [class](#class), usually together with a [probability](#probability) for each class.
*In this project:* the three candidates are scikit-learn's `LogisticRegression`, `DecisionTreeClassifier` and `RandomForestClassifier`.

<a id="co-applicant"></a>
**Co-applicant**
A second person, often a husband, wife or parent, who applies for the loan jointly and whose income also counts towards paying it back.
*In this project:* `coapplicant_income`, in rupees per month, is optional; left blank, it counts as 0. Total income is applicant plus co-applicant, and at least one of them must be above zero ([../src/loanwise/domain/validation.py](../src/loanwise/domain/validation.py)).

<a id="code"></a>
**Code (computer program)**
Written instructions, in a [programming language](#programming-language), that tell a computer exactly what to do, step by step. A program is a collection of such instructions that does a job.
*In this project:* the server code is in [Python](#python) under [../src/loanwise/](../src/loanwise/); the website code is in [JavaScript](#javascript) under [../frontend/src/](../frontend/src/).

<a id="coefficient"></a>
**Coefficient (weight)**
In a [Logistic Regression](#logistic-regression), the number that a [feature](#feature) is multiplied by before everything is added up. A positive coefficient pushes towards "approved", a negative one towards "rejected", and a larger size (ignoring the sign) means a stronger push.
*In this project:* after [scaling](#scaling), Credit_History has +1.157, the [EMI-to-income ratio](#emi-to-income-ratio) −0.218 and loan term −0.193. The starting value, the [intercept](#intercept), is +0.672.

<a id="column"></a>
**Column**
In a table, one vertical list that holds the same kind of information for every [row](#row).
*Example:* the `ApplicantIncome` column holds the monthly income of each of the 614 applicants.
*In this project:* `loan.csv` has 13 columns: an ID, 11 [features](#feature) and the [label](#label) `Loan_Status`.

<a id="component"></a>
**Component (React)**
In [React](#react), a [function](#function) that produces one part of a web page, such as a button, a form question or a whole page, and redraws that part when its information changes.
*In this project:* page components in [../frontend/src/pages/](../frontend/src/pages/) (Home, Check, Result, HowItWorks, History, NotFound) and shared ones such as inputs and pop-up messages in [../frontend/src/components/](../frontend/src/components/). See [09 · Frontend](09-frontend.md).

<a id="confidence"></a>
**Confidence**
How sure the system says it is about its answer, as a number from 0 to 1.
*In this project:* the model's [probability](#probability) for the answer it gave (for a rejection, `1 − P(approve)`), then adjusted by the [guardrails](#guardrail): at least 0.90 when a rule forces a rejection, at most 0.65 when the model approves someone with bad credit. Shown as **High** (0.75 or more), **Medium** (0.60 or more) or **Low**. *Example:* a graduate earning ₹45,000 a month asking for ₹25 lakh over 20 years with good credit gets "Likely Approved", confidence 0.69, Medium.

<a id="confusion-matrix"></a>
**Confusion matrix**
A small table that counts four kinds of results: [true positives, true negatives](#true-positive), [false positives and false negatives](#false-positive).
*In this project:* on the 123 test rows, all three models get 84 approvals right, 21 rejections right, wrongly approve 17 people who were rejected, and wrongly reject 1 person who was approved. See [06 · Training and evaluation](06-training-and-evaluation.md).

<a id="cors"></a>
**CORS (Cross-Origin Resource Sharing)**
A [browser](#browser) safety rule. A web page may only read answers from a [server](#server) at a different [origin](#origin) if that server sends back special permission lines with its answer.
*In this project:* the server gives permission only to pages from `localhost` or `127.0.0.1` (the user's own computer), on any port, for `/api` addresses. Look-alikes such as `localhost.evil.com` are refused. Changeable with `LOANWISE_CORS_ORIGINS`. Code: `is_allowed_origin()` in [../src/loanwise/api/\_\_init\_\_.py](../src/loanwise/api/__init__.py).

<a id="credit-history"></a>
**Credit history**
A record of whether a person has paid back past loans and credit-card bills on time.
*In this project:* `Credit_History` is 1.0 (good, meets the lender's guidelines) or 0.0 (bad); the API takes `"good"` or `"bad"`. It is the strongest [feature](#feature): 79.6 % of applicants with good history were approved, against 7.9 % with bad. The website's answer "I never had a loan or card" is sent as `"good"`, and the 50 blank values in the training data are filled in as 1 ([imputation](#imputation)).

<a id="crore"></a>
**Crore**
An Indian number word: 1 crore = 1,00,00,000 (ten million). It equals 100 [lakh](#lakh).
*In this project:* the largest monthly income and the largest loan accepted are both ₹1,00,00,000 ([../src/loanwise/domain/schemas.py](../src/loanwise/domain/schemas.py)). Users may type "1 crore" or "1 cr".

<a id="cross-validation"></a>
**Cross-validation (k-fold)**
A way to measure a [model](#model) more reliably. The [training](#training) rows are cut into k equal parts. The model is trained on all parts but one and tested on the part left out, and this is repeated k times so each part is left out once. The k scores are then [averaged](#average).
*In this project:* k = 5, on the 491 training rows, with [stratification](#stratification). It is used both to tune [hyperparameters](#hyperparameter) and to pick the winning model ([../src/loanwise/ml/evaluation.py](../src/loanwise/ml/evaluation.py)).

<a id="csv"></a>
**CSV (comma-separated values)**
A [file](#file) that stores a table as plain text: one [row](#row) per line, with commas between the values.
*In this project:* `data/raw/loan.csv` (614 rows with answers) and `data/raw/test.csv` (367 rows without the `Loan_Status` [label](#label)).

## D

<a id="data"></a>
**Data**
Recorded facts, such as numbers, words or dates, stored so that a computer can read and process them.
*In this project:* the facts about past loan applications (income, loan size, credit history and so on, and whether each was approved), plus the answers a user types into the form.

<a id="data-leakage"></a>
**Data leakage**
A mistake where information the [model](#model) should not have during [training](#training), especially information from the rows used to test it, gets used anyway. The test score then looks better than real-life performance will be.
*In this project:* avoided by doing all preparation inside the [pipeline](#pipeline), so it is redone separately inside each [cross-validation](#cross-validation) part; by choosing the model with cross-validation only; and by using the [hold-out set](#hold-out-set) only to report results.

<a id="database"></a>
**Database**
Software that stores [data](#data) in an organised way on disk, so it can be added to, searched and deleted reliably, even by several users at once.
*In this project:* an [SQLite](#sqlite) database at `instance/loanwise.db` keeps the history of past checks.

<a id="dataset"></a>
**Dataset**
A collection of [data](#data) about many cases, usually laid out as a table of [rows](#row) and [columns](#column).
*In this project:* the training dataset is `data/raw/loan.csv`: 614 past applications (rows) with 13 columns. See [03 · The Dataset](03-dataset.md).

<a id="debt-to-income-ratio"></a>
**Debt-to-income ratio (DTI)**
All of a person's monthly loan payments divided by their monthly income. Lenders use it to judge [affordability](#affordability).
*In this project:* the dataset has no information about existing loans, so the [EMI-to-income ratio](#emi-to-income-ratio) for the new loan is used instead.

<a id="decision-threshold"></a>
**Decision threshold**
The [probability](#probability) at or above which the answer is "yes".
*In this project:* 0.5 (`APPROVAL_THRESHOLD`). A probability of approval of 0.5 or more means "Likely Approved", unless a [guardrail](#guardrail) overrides it.

<a id="decision-tree"></a>
**Decision Tree**
A [model](#model) made of a series of yes/no questions about the [features](#feature), such as "Is credit history good?" Each answer leads to another question or to a final group of training rows, called a leaf; the answer is the share of approved rows in that leaf.
*In this project:* the second candidate. The best version asks at most 2 questions in a row (`max_depth = 2`) and needs at least 10 rows per leaf. Its [cross-validation](#cross-validation) [accuracy](#accuracy) was the lowest, 0.7840. See [05 · Algorithms](05-algorithms.md).

<a id="dependents"></a>
**Dependents**
People who rely on the applicant for money, such as children or elderly parents.
*In this project:* one of `"0"`, `"1"`, `"2"` or `"3+"`. The form accepts words or numbers; 3 or more become `"3+"` and more than 30 is rejected as a likely typing mistake.

<a id="docker"></a>
**Docker**
A tool that packs a program together with everything it needs to run (the right version of [Python](#python), [libraries](#library), [files](#file)) into one bundle called an image, which then runs the same way on any computer that has Docker.
*In this project:* the [../Dockerfile](../Dockerfile) builds the website with Node.js, then builds a Python 3.12 image that runs the server with [gunicorn](#gunicorn) as a restricted user and checks `/api/health` every 30 seconds. See [08 · Backend](08-backend.md).

## E

<a id="eda"></a>
**EDA (exploratory data analysis)**
Looking at a [dataset](#dataset) before building a [model](#model): counting values, finding blanks, drawing charts and comparing groups.
*In this project:* [../src/loanwise/ml/eda.py](../src/loanwise/ml/eda.py) prints a summary and saves four charts (class balance, approval rate by group, income distribution, missing values) to `artifacts/reports/eda/`.

<a id="emi"></a>
**EMI (equated monthly instalment)**
The fixed amount a borrower pays the lender every month until the loan is repaid.
*In this project:* there are two versions. The **model** uses `loan in ₹ ÷ number of months`, which ignores [interest](#interest-rate); it only needs to go up when the loan goes up and down when the term gets longer ([../src/loanwise/ml/features.py](../src/loanwise/ml/features.py)). The **guardrails** and the result screen use the realistic [amortised EMI](#amortised-emi) at 9 % a year.

<a id="emi-to-income-ratio"></a>
**EMI-to-income ratio**
The monthly instalment divided by the monthly income. A lower number means the loan is easier to afford.
*Example:* an EMI of ₹22,493 on an income of ₹45,000 is a ratio of 0.50, or 50 %.
*In this project:* the only way income and loan size reach the model, as `log1p(clip(EMI ÷ total income, 0, 10))` (see [log transform](#log-transform)). The [guardrails](#guardrail) use the amortised version: above 65 % forces a rejection, 45 % to 65 % is called "a big stretch", 30 % or less is "easy".

<a id="endpoint"></a>
**Endpoint**
One web address on a [server](#server), together with one kind of [request](#request-and-response) (such as GET to read or POST to send), that the server knows how to answer.
*In this project:* six: `POST /api/predict`, `GET /api/history`, `DELETE /api/history`, `GET /api/model-info`, `GET /api/health`, `GET /api/sample`.

<a id="ensemble"></a>
**Ensemble**
A [model](#model) whose answer combines the answers of several other models.
*In this project:* the [Random Forest](#random-forest).

<a id="environment-variable"></a>
**Environment variable (settings)**
A named value, such as `LOANWISE_PORT=5000`, that is set outside a program and read by it when it starts. It lets the same [code](#code) behave differently on a laptop, in tests and on a live server without editing the code.
*In this project:* `Settings` in [../src/loanwise/config.py](../src/loanwise/config.py) reads `LOANWISE_*` variables (where the model and database are, which port to use, how big a request may be, and so on). All have defaults. See [../.env.example](../.env.example).

<a id="esbuild"></a>
**esbuild**
A tool that takes many [JavaScript](#javascript) and style [files](#file) and combines them into a few small files that a [browser](#browser) can download quickly.
*In this project:* `npm run build` ([../frontend/scripts/build.mjs](../frontend/scripts/build.mjs)) writes the finished website to `frontend/dist`. `npm run dev` ([../frontend/scripts/dev.mjs](../frontend/scripts/dev.mjs)) runs a development copy on port 5173 that forwards `/api` requests to the server on port 5000.

## F

<a id="f1-score"></a>
**F1 score**
One number that combines [precision](#precision) and [recall](#recall): `2 × precision × recall ÷ (precision + recall)`. It is high only when both are high.
*In this project:* 0.9032 for all three models on the test rows.

<a id="false-positive"></a>
**False positive / false negative**
Two kinds of wrong answer. A false positive is a "yes" given when the truth was "no". A false negative is a "no" given when the truth was "yes".
*In this project:* "yes" means approved. On the 123 test rows there are 17 false positives (applications that were rejected, but the model said approved) and 1 false negative.

<a id="feature"></a>
**Feature**
One piece of information about each case that a [model](#model) uses to make its [prediction](#prediction). In a table, each feature is one [column](#column).
*Example:* monthly income, loan amount and credit history are features of a loan application.
*In this project:* the user gives 11 features. After preparation the [Logistic Regression](#logistic-regression) works with 18 numbers per applicant: 3 [numeric features](#numeric-feature) (credit history, loan term, EMI-to-income ratio) and 15 [one-hot](#one-hot-encoding) columns.

<a id="feature-engineering"></a>
**Feature engineering**
Calculating new [features](#feature) from the original ones, so that the [model](#model) gets information in a more useful or safer form.
*In this project:* `add_engineered_features()` calculates total income, [EMI](#emi), the [EMI-to-income ratio](#emi-to-income-ratio) and its capped log. Only the capped log ratio is passed to the model; the raw incomes and loan amount are deliberately left out (see [monotonicity](#monotonicity)). See [04 · Data preparation and features](04-data-preparation-and-features.md).

<a id="feature-importance"></a>
**Feature importance**
A score for how much each [feature](#feature) affects a [model](#model)'s answers.
*In this project:* the size of each [Logistic Regression](#logistic-regression) [coefficient](#coefficient) (sign ignored), with the [one-hot](#one-hot-encoding) columns of one feature added together, keeping the top 8 and rescaling them to add up to 1. Credit History 0.3292, Property Area 0.2234, Number of Dependents 0.1302, Marital Status 0.1143, Education 0.0701, EMI-to-Income Ratio 0.0621, Loan Term 0.0550, Gender 0.0158. Self Employed comes ninth, so it is not listed. Shown on the How it works page.

<a id="file"></a>
**File**
A named piece of stored information on a disk, such as a document, an image, a table or a program.
*Example:* `loan_model.pkl` is the file holding the trained model.

<a id="flask"></a>
**Flask**
A [Python](#python) [library](#library) for writing [servers](#server) that answer web [requests](#request-and-response).
*In this project:* Flask 3.1 runs the [API](#api) and sends the website's files. See [../src/loanwise/api/](../src/loanwise/api/) and [08 · Backend](08-backend.md).

<a id="framer-motion"></a>
**framer-motion**
A [JavaScript](#javascript) [library](#library) for animating parts of a [React](#react) page, for example making a page fade in.
*In this project:* version 11.11.17. It animates page changes, error messages and pop-up notices. It is set to respect the user's "reduce motion" setting on their device ([../frontend/src/App.jsx](../frontend/src/App.jsx)).

<a id="frontend-and-backend"></a>
**Frontend and backend**
The frontend is the part of a system that runs on the user's device and that they see and touch: the pages in the [browser](#browser). The backend is the part that runs on the [server](#server): it receives requests, does the calculations and stores data.
*In this project:* frontend in [../frontend/](../frontend/) ([React](#react)); backend in [../src/loanwise/](../src/loanwise/) ([Python](#python) and [Flask](#flask)).

<a id="function"></a>
**Function**
A named block of [code](#code) that takes some inputs, does one job and gives back a result.
*Example:* `estimate_emi(principal, months)` takes a loan amount and a number of months and returns the monthly payment.

<a id="functiontransformer"></a>
**FunctionTransformer**
A [scikit-learn](#scikit-learn) tool that turns an ordinary [Python](#python) [function](#function) into one step of a [pipeline](#pipeline).
*In this project:* used for the cleaning step and the [feature-engineering](#feature-engineering) step. Because the saved model refers to those functions by their location, they must stay in `loanwise.ml.features`.

## G

<a id="gini-impurity"></a>
**Gini impurity**
A number that measures how mixed a group of rows is: 0 when every row has the same answer, and 0.5 when the group is exactly half approved and half rejected. A [decision tree](#decision-tree) chooses each question so that the groups it creates are as unmixed as possible.
*In this project:* the default measure used by the [Decision Tree](#decision-tree) and [Random Forest](#random-forest).

<a id="grid-search"></a>
**Grid search**
Trying every combination from a short list of [hyperparameter](#hyperparameter) values and keeping the combination that scores best in [cross-validation](#cross-validation).
*In this project:* `GridSearchCV`. Logistic Regression tries 4 values of `C`; the Decision Tree tries 12 combinations; the Random Forest tries 9.

<a id="guardrail"></a>
**Guardrail**
A fixed rule, written by a person, that is checked after the [model](#model) answers and can change or soften that answer.
*In this project:* four rules in [../src/loanwise/domain/guardrails.py](../src/loanwise/domain/guardrails.py). R1: monthly payment above 65 % of income → rejected. R2: loan more than 60 months of total income → rejected. R3: bad credit → listed as a reason, and confidence capped at 0.65 if the model still approves. R4: payment between 45 % and 65 % of income → "big stretch" warning. They never turn a rejection into an approval. See [07 · Validation and guardrails](07-validation-and-guardrails.md).

<a id="gunicorn"></a>
**gunicorn**
A program that runs a [Python](#python) web application on a live [server](#server), using several copies of it at once so it can answer many users.
*In this project:* `gunicorn wsgi:app`, with 2 copies by default (`GUNICORN_WORKERS`). See [WSGI](#wsgi).

## H

<a id="health-check"></a>
**Health check**
A simple web address that answers quickly to show a service is running.
*In this project:* `GET /api/health` answers `{"ok": true, "model_loaded": true}` (or `false` if no model is available).

<a id="hold-out-set"></a>
**Hold-out set (test split)**
A part of the [dataset](#dataset) that is put aside before [training](#training) and used only once, at the end, to measure how well the [model](#model) does on rows it has never seen.
*In this project:* 20 % of `loan.csv`: 123 rows, 85 approved and 38 rejected. It is used only for reporting, never for choosing. It is not the same thing as the file `test.csv`, which has no answers.

<a id="hot-reload"></a>
**Hot reload (model)**
Loading a new version of a [file](#file) while the program keeps running, with no restart.
*In this project:* `ModelRegistry` ([../src/loanwise/services/model_registry.py](../src/loanwise/services/model_registry.py)) checks whether the model file has changed; if so, it loads the new one. If loading fails, it keeps using the old model.

<a id="http"></a>
**HTTP (Hypertext Transfer Protocol)**
The set of rules [browsers](#browser) and [servers](#server) follow to send [requests and responses](#request-and-response) over the internet. Each request names a method, such as GET (read something) or POST (send something), and a web address.

<a id="http-status-code"></a>
**HTTP status code**
A three-digit number at the start of every [HTTP](#http) response that says how the request went.
*In this project:* **200** success; **400** the server could not read the request; **404** no such address; **405** wrong method for that address; **413** request bigger than 32 KB; **422** the request was readable but some answers are invalid (the reply lists each one); **503** the model, its report or the example data is not available; **500** an unexpected error (recorded in the logs, never shown). See [../src/loanwise/api/errors.py](../src/loanwise/api/errors.py).

<a id="hyperparameter"></a>
**Hyperparameter**
A setting of an [algorithm](#algorithm) that a person chooses before [training](#training), rather than something the algorithm learns from the [data](#data). Examples are how many questions a [decision tree](#decision-tree) may ask in a row, or how strong the [regularisation](#regularisation) is.
*In this project:* chosen by [grid search](#grid-search). Winners: `C = 0.1` for Logistic Regression; depth 2 and at least 10 rows per leaf for the Decision Tree; depth 4 and at least 5 rows per leaf for the Random Forest.

## I

<a id="imputation"></a>
**Imputation**
Filling in [missing values](#missing-value) with a reasonable stand-in so a [model](#model) can use the row.
*In this project:* done inside the [pipeline](#pipeline). Blank group answers and blank credit history get the most common value (so blank credit history becomes 1, good); other blank numbers get the [median](#median). Blanks in `loan.csv`: Credit_History 50, Self_Employed 32, LoanAmount 22, Dependents 15, Loan_Amount_Term 14, Gender 13, Married 3.

<a id="integration-test"></a>
**Integration test**
An automatic [test](#test) that checks several parts of a system working together, for example sending a real request to the server and checking the answer.
*In this project:* 28 integration tests in [../tests/integration/](../tests/integration/), including the server with a fake model, a broken model, no model and the real model.

<a id="intercept"></a>
**Intercept**
The fixed starting number in a [Logistic Regression](#logistic-regression), added before the [features](#feature)' contributions.
*In this project:* +0.672.

<a id="interest-rate"></a>
**Interest rate**
The extra money a lender charges for a loan, given as a percentage of the amount still owed, per year.
*In this project:* the dataset contains no interest rates, so the [guardrails](#guardrail) assume 9 % a year when estimating the monthly payment.

## J

<a id="javascript"></a>
**JavaScript**
A [programming language](#programming-language) that [browsers](#browser) can run. It makes web pages respond to clicks and typing and lets them talk to [servers](#server).
*In this project:* the website is written in JavaScript using [React](#react).

<a id="joblib"></a>
**joblib**
A [Python](#python) [library](#library) for saving a trained [model](#model) to a [file](#file) and loading it again.
*In this project:* training saves `loan_model.pkl` with joblib; the server loads it with joblib. See [pickle](#pickle).

<a id="json"></a>
**JSON (JavaScript Object Notation)**
A plain-text way of writing structured [data](#data) as named values, for example `{"loan_term": 360, "credit_history": "good"}`. Almost every programming language can read and write it.
*In this project:* every [API](#api) request and response, and the `model_info.json` report.

## L

<a id="label"></a>
**Label (target)**
The answer that a [model](#model) is trained to predict, recorded for each past case in the [dataset](#dataset).
*In this project:* the `Loan_Status` [column](#column): `Y` (approved) for 422 rows and `N` (rejected) for 192.

<a id="lakh"></a>
**Lakh**
An Indian number word: 1 lakh = 1,00,000 (one hundred thousand). Indian writing puts commas after the first three digits and then after every two, so ₹25,00,000 is 25 lakh.
*In this project:* users may type "2.5 lakh", "2 lac" or "2L"; the server reads it as ₹2,50,000 and tells the user so. `format_inr()` writes every amount in this style ([../src/loanwise/domain/formatting.py](../src/loanwise/domain/formatting.py)).

<a id="library"></a>
**Library**
A collection of ready-made [code](#code) that other programs can use, so that common jobs do not have to be written from scratch.
*In this project:* [scikit-learn](#scikit-learn) for machine learning, [pandas](#pandas) for tables, [Flask](#flask) for the server, [React](#react) for the website, among others.

<a id="loan-term"></a>
**Loan term (tenure)**
How long the borrower has to repay the loan, counted in months.
*In this project:* one of 12, 36, 60, 84, 120, 180, 240, 300, 360 or 480 months. "30 years" is accepted and read as 360. In the data, 512 of 614 loans are for 360 months.

<a id="log-odds"></a>
**Log-odds**
Another way of writing a [probability](#probability) `p`, as `log(p ÷ (1 − p))`. A probability of 0.5 has log-odds 0; higher probabilities have positive log-odds and lower ones negative. [Logistic Regression](#logistic-regression) first calculates log-odds, then turns them into a probability with the [sigmoid](#sigmoid).

<a id="log-transform"></a>
**Log transform**
Replacing a number with its logarithm, which shrinks large numbers much more than small ones. `log1p(x)` means `log(1 + x)` and works when `x` is 0.
*In this project:* applied to the [EMI-to-income ratio](#emi-to-income-ratio) after it is capped at 10, so a few extreme applicants cannot dominate the model.

<a id="logistic-regression"></a>
**Logistic Regression**
A [classification](#binary-classification) [algorithm](#algorithm). It multiplies each [feature](#feature) by a [coefficient](#coefficient), adds the results to the [intercept](#intercept) to get the [log-odds](#log-odds), and turns that total into a [probability](#probability) between 0 and 1 with the [sigmoid](#sigmoid). [Training](#training) finds the coefficients that best match the past approvals.
*In this project:* the chosen model, with `C = 0.1` ([regularisation](#regularisation)). [Cross-validation](#cross-validation) accuracy 0.7983. See [05 · Algorithms](05-algorithms.md).

<a id="principal"></a>
**Loan amount (principal)**
The sum of money borrowed, not counting [interest](#interest-rate).
*In this project:* the user types it in full rupees, from ₹1,000 to ₹1,00,00,000. The dataset stores it in thousands of rupees, so the server divides by 1,000 before giving it to the model. The median in the data is 128, meaning ₹1,28,000.

## M

<a id="machine-learning"></a>
**Machine learning**
A way of building computer programs in which the program's rules are worked out automatically from past examples, instead of being written by hand. An [algorithm](#algorithm) looks at many past cases where the answer is known, finds the patterns that best connect the information to the answer, and stores them as a [model](#model). The model then applies those patterns to new cases.
*In this project:* the algorithm looked at 614 past loan applications and their outcomes and produced a model that estimates approval for a new applicant. See [00 · AI from zero](00-ai-from-zero.md).

<a id="median"></a>
**Median**
The middle value when a list of numbers is sorted from smallest to largest. Unlike the [average](#average), it is not pulled up or down by a few extreme values.
*In this project:* the stand-in for blank numbers ([imputation](#imputation)). Medians in the data: applicant income ₹3,812.50 a month, co-applicant income ₹1,188.50, loan amount 128 thousand, term 360 months.

<a id="missing-value"></a>
**Missing value**
A blank in a [dataset](#dataset): a place where the information was not recorded.
*In this project:* 7 of the 11 input [columns](#column) have blanks; see [imputation](#imputation).

<a id="model"></a>
**Model**
The result of [training](#training): a stored set of numbers and rules that turns a case's [features](#feature) into a [prediction](#prediction). It can be saved to a [file](#file) and used again and again.
*In this project:* a [Logistic Regression](#logistic-regression) together with all its data-preparation steps (a [pipeline](#pipeline)), saved as `artifacts/models/loan_model.pkl`. Given 11 answers, it returns the [probability](#probability) of approval.

<a id="model-card"></a>
**Model card**
A short document that states what a [model](#model) is for, how it was built, how well it scores and where it should not be trusted.
*In this project:* [../docs/MODEL_CARD.md](../docs/MODEL_CARD.md).

<a id="model-registry"></a>
**Model registry**
The part of a program that knows where the current [model](#model) is stored, loads it and hands it to the code that needs it.
*In this project:* `ModelRegistry` in [../src/loanwise/services/model_registry.py](../src/loanwise/services/model_registry.py). It loads the model on first use and supports [hot reload](#hot-reload).

<a id="monotonicity"></a>
**Monotonic constraint / monotonicity**
A requirement that an answer only ever moves in one direction when one input goes up. Here it means: more income must never lower the chance of approval, and a bigger loan must never raise it.
*In this project:* guaranteed in three ways. (1) Income and loan size reach the model only through the [EMI-to-income ratio](#emi-to-income-ratio). (2) The tree models are given `monotonic_cst`, which forbids them from learning the wrong direction. (3) Before saving, `check_monotonicity()` tests three sample applicants with 60 incomes from ₹1,000 to ₹1 crore a month and 60 loan sizes from ₹10,000 to ₹1 crore (12 checks in total); if any check moves the wrong way, training stops and nothing is saved. See [04 · Data preparation and features](04-data-preparation-and-features.md).

<a id="mypy"></a>
**mypy**
A tool that reads [Python](#python) [code](#code) without running it and reports places where the kind of value used does not match what was declared (for example, text passed where a number is expected).
*In this project:* run in its strictest mode with `make typecheck` ([../pyproject.toml](../pyproject.toml)).

## N

<a id="nan"></a>
**NaN (not a number)**
A special computer value meaning "no valid number here". It is often used to mark a [missing value](#missing-value).
*In this project:* blanks in the training data become NaN and are then filled in. If a user or program sends NaN or infinity as an answer, the server rejects that answer.

<a id="normalisation"></a>
**Normalisation**
Rescaling a list of numbers so that they add up to 1.
*In this project:* applied to the top 8 [feature importances](#feature-importance).

<a id="numeric-feature"></a>
**Numeric feature**
A [feature](#feature) whose values are amounts that can be compared and calculated with, such as income or number of months.
*In this project:* the user gives five (applicant income, co-applicant income, loan amount, loan term, credit history); the model uses three (credit history, loan term, EMI-to-income ratio).

## O

<a id="one-hot-encoding"></a>
**One-hot encoding**
Turning a [categorical feature](#categorical-feature) into several columns of 0 or 1, one column per possible value, with a 1 in the column that matches.
*Example:* Property_Area "Urban" becomes Rural = 0, Semiurban = 0, Urban = 1.
*In this project:* the six categorical features become 15 columns. An unexpected value becomes all zeros instead of causing an error.

<a id="origin"></a>
**Origin**
The first part of a web address that identifies a site: the scheme (`http` or `https`), the host name and the port, such as `http://localhost:5173`. [Browsers](#browser) use it to decide which pages may talk to which [servers](#server) (see [CORS](#cors)).

<a id="overfitting"></a>
**Overfitting**
When a [model](#model) matches its [training](#training) rows so closely, including their random quirks, that it does worse on new rows.
*In this project:* kept low with small [hyperparameter](#hyperparameter) lists, shallow trees, [regularisation](#regularisation), and by choosing the model with [cross-validation](#cross-validation).

<a id="override"></a>
**Override**
When a [guardrail](#guardrail) replaces the [model](#model)'s answer.
*In this project:* rules R1 and R2 force "Likely Rejected", set `guardrail_applied: true` and report a confidence of at least 0.90.

## P

<a id="pandas"></a>
**pandas**
A [Python](#python) [library](#library) for working with tables of [data](#data) (it calls a table a DataFrame).
*In this project:* reads the [CSV](#csv) files. The model is always given a one-row pandas table with exactly 11 columns.

<a id="percentage"></a>
**Percentage, and how it relates to probability**
A percentage is a number out of 100. A [probability](#probability) is the same idea written as a number from 0 to 1, so a probability of 0.69 and a chance of 69 % mean the same thing. This documentation uses both.
*Example:* 422 approvals out of 614 applications is 422 ÷ 614 = 0.687, which is 68.7 %.

<a id="pickle"></a>
**Pickle**
[Python](#python)'s built-in way of saving a program object, such as a trained [model](#model), to a [file](#file) and loading it back later. Loading a pickle can run [code](#code), so only files from a trusted source should be loaded, and the same [library](#library) versions must be installed when loading.
*In this project:* `loan_model.pkl` is a pickle made with [joblib](#joblib). That is why [scikit-learn](#scikit-learn) is fixed at exactly version 1.9.1.

<a id="pipeline"></a>
**Pipeline (scikit-learn)**
A chain of steps, ending in a [model](#model), that is trained, saved and used as one object. Each step passes its output to the next.
*In this project:* clean the 11 inputs → fill blanks ([imputation](#imputation)) → [feature engineering](#feature-engineering) → [scaling](#scaling) and [one-hot encoding](#one-hot-encoding) → model. The saved file accepts the raw 11 answers, so the server cannot skip a step. See [../src/loanwise/ml/pipelines.py](../src/loanwise/ml/pipelines.py).

<a id="precision"></a>
**Precision**
Of all the cases a [model](#model) answered "yes" to, the share that really were "yes": `true positives ÷ (true positives + false positives)`.
*In this project:* 84 ÷ 101 = 0.8317 on the test rows.

<a id="predict-proba"></a>
**predict_proba**
The [scikit-learn](#scikit-learn) [function](#function) that returns a [model](#model)'s [probability](#probability) for each [class](#class).
*In this project:* `predict_proba(X)[:, 1]` is the probability of approval. If it fails or returns NaN, the server answers with status 500.

<a id="prediction"></a>
**Prediction**
The answer a [model](#model) gives for a new case. In machine learning, "prediction" means an estimate based on patterns in past [data](#data), not a statement about the future that is known to be true.
*In this project:* the probability that an application would be approved, turned into "Likely Approved" or "Likely Rejected".

<a id="probability"></a>
**Probability**
A number from 0 to 1 that says how likely something is: 0 means it will not happen, 1 means it certainly will, and 0.5 means even chances. Multiply by 100 to get a [percentage](#percentage).
*In this project:* the model returns the probability of approval. It is stored in the history but not sent to the user; the user sees [confidence](#confidence) instead.

<a id="programming-language"></a>
**Programming language**
A strict written language with exact rules, used to write [code](#code) that a computer can carry out. [Python](#python) and [JavaScript](#javascript) are two examples.

<a id="property-area"></a>
**Property area**
Where the house being bought is: Urban (city), Semiurban (edge of a city or small town) or Rural (village).
*In this project:* the second most important [feature](#feature) (0.2234). Approval rates in the data: Semiurban 76.8 %, Urban 65.8 %, Rural 61.5 %.

<a id="python"></a>
**Python**
A widely used [programming language](#programming-language), popular for [data](#data) work and [machine learning](#machine-learning).
*In this project:* the server, the training and the tests are written in Python (version 3.10 or newer).

## R

<a id="random-forest"></a>
**Random Forest**
A [model](#model) made of many [decision trees](#decision-tree). Each tree is trained on a different random selection of rows and, at each question, may only choose from a random subset of [features](#feature). The forest's answer is the [average](#average) of all the trees' answers (see [bagging](#bagging)).
*In this project:* the third candidate: 300 trees, at most 4 questions deep, at least 5 rows per leaf. [Cross-validation](#cross-validation) accuracy 0.7962, a close second. See [05 · Algorithms](05-algorithms.md).

<a id="react"></a>
**React**
A [JavaScript](#javascript) [library](#library) for building web pages out of [components](#component) that redraw themselves when their information changes.
*In this project:* React 19 with React Router, which switches between the pages `/`, `/check`, `/result`, `/how-it-works` and `/history`. See [09 · Frontend](09-frontend.md).

<a id="recall"></a>
**Recall**
Of all the cases that really were "yes", the share the [model](#model) answered "yes" to: `true positives ÷ (true positives + false negatives)`.
*In this project:* 84 ÷ 85 = 0.9882. High recall with lower [precision](#precision) means the model approves nearly everyone with good credit, including some who were in fact rejected.

<a id="regularisation"></a>
**Regularisation**
A penalty added during [training](#training) that keeps [coefficients](#coefficient) small, so the [model](#model) does not lean too hard on any one [feature](#feature). In scikit-learn's Logistic Regression, a smaller `C` means a stronger penalty.
*In this project:* `C = 0.1`, chosen from 0.01, 0.1, 1 and 10.

<a id="repository-pattern"></a>
**Repository pattern**
Putting all the [code](#code) that reads and writes a [database](#database) into one place with a few simple actions (add, list, clear), so the rest of the program never deals with the database directly.
*In this project:* `HistoryRepository` in [../src/loanwise/storage/history_repository.py](../src/loanwise/storage/history_repository.py).

<a id="request-and-response"></a>
**Request and response**
A request is a message a [browser](#browser) or program sends to a [server](#server) asking for something; the response is the server's reply. Both travel using [HTTP](#http).
*In this project:* the form sends a request with the 11 answers to `/api/predict`; the response contains the verdict, confidence, reasons and estimated EMI.

<a id="row"></a>
**Row**
In a table, one horizontal line that holds all the information about one case.
*Example:* row `LP001002` in `loan.csv` is one past applicant: male, not married, graduate, ₹5,849 a month, approved.
*In this project:* `loan.csv` has 614 rows, one per past application.

<a id="ruff"></a>
**ruff**
A tool that reads [Python](#python) [code](#code) and reports style problems, likely mistakes and some security risks, and can tidy the formatting automatically.
*In this project:* `make lint` and `make format` ([../pyproject.toml](../pyproject.toml)).

## S

<a id="sanitizer"></a>
**Sanitizer**
[Code](#code) that takes answers that have already been checked and converts them into exactly the form the next step needs.
*In this project:* `to_model_frame()` in [../src/loanwise/domain/sanitizer.py](../src/loanwise/domain/sanitizer.py) renames the fields to the dataset's column names, divides the loan by 1,000, turns `"good"`/`"bad"` into 1.0/0.0, and warns the user if total monthly income is above ₹5,00,000 (they may have typed a yearly figure).

<a id="sanity-check"></a>
**Sanity check (training)**
A quick final test that a saved result actually works.
*In this project:* [../src/loanwise/ml/sanity.py](../src/loanwise/ml/sanity.py) starts a fresh copy of Python, loads the saved model the same way the server does, and scores four test applicants (good profile, bad credit, everything blank, ₹90 lakh income) and five example rows from `test.csv`.

<a id="scaling"></a>
**Scaling (standardisation)**
Converting a [numeric feature](#numeric-feature) so that its [average](#average) is 0 and its [standard deviation](#standard-deviation) is 1. This puts features measured in very different units on the same footing.
*In this project:* applied to the three numeric model columns, for [Logistic Regression](#logistic-regression) only. Tree models do not need it.

<a id="scikit-learn"></a>
**scikit-learn**
The most widely used [Python](#python) [library](#library) for [machine learning](#machine-learning).
*In this project:* fixed at exactly version 1.9.1, because the saved model can only be loaded reliably by the version that created it.

<a id="self-employed"></a>
**Self-employed**
Running one's own business instead of earning a salary from an employer.
*In this project:* `Self_Employed` Yes/No. Approval rates are almost the same in the data (68.3 % for Yes, 68.6 % for No), and it ranks ninth in importance.

<a id="server"></a>
**Server**
A computer, or a program running on one, that waits for [requests](#request-and-response) from other devices over a network and answers them.
*In this project:* the LoanWise server is a [Python](#python) program that sends the website to the [browser](#browser) and answers its `/api` requests. It can run on the user's own computer (`./run.sh`) or on a hosted machine.

<a id="sigmoid"></a>
**Sigmoid (logistic function)**
The formula `1 ÷ (1 + e^(−z))`, which turns any number `z` into a number between 0 and 1. Large positive `z` gives close to 1, large negative `z` gives close to 0, and `z = 0` gives 0.5.
*In this project:* the last step of the [Logistic Regression](#logistic-regression): it turns the [log-odds](#log-odds) into the probability of approval.

<a id="spa"></a>
**SPA (single-page application)**
A [website](#website) that loads one page once and then changes what is shown using [JavaScript](#javascript), without asking the [server](#server) for a whole new page each time.
*In this project:* the [React](#react) website. The server sends `index.html` for any non-`/api` address so that refreshing a page such as `/history` still works ([../src/loanwise/api/spa.py](../src/loanwise/api/spa.py)).

<a id="sqlite"></a>
**SQLite**
A small [database](#database) that keeps everything in a single [file](#file) and needs no separate database server.
*In this project:* past checks are stored in `instance/loanwise.db`, in a table called `predictions`. That suits one server; several servers would need a shared database.

<a id="standard-deviation"></a>
**Standard deviation**
A number that says how spread out a list of values is around their [average](#average). Small means the values are close together.
*In this project:* the five [cross-validation](#cross-validation) scores of each model have a standard deviation of about 0.045, which is larger than the gaps between the models. See [variance](#variance).

<a id="statistics"></a>
**Statistics**
The branch of mathematics that collects, summarises and draws conclusions from [data](#data), including how much those conclusions can be trusted.
*In this project:* [averages](#average), [medians](#median), approval rates by group, [standard deviations](#standard-deviation) and all the scores such as [accuracy](#accuracy) and [precision](#precision) are statistics.

<a id="stratification"></a>
**Stratification**
Splitting [data](#data) so that each part has the same mix of [classes](#class) as the whole.
*In this project:* every split keeps about 68.7 % approved. With only 192 rejections, an unstratified split could by chance get far too few.

## T

<a id="test"></a>
**Test (software)**
A small program that runs part of the [code](#code) with known inputs and checks that the result is what it should be. Tests are run automatically after every change.
*In this project:* 90 tests: 62 [unit tests](#unit-test) and 28 [integration tests](#integration-test). Run with `make test`.

<a id="train-serve-skew"></a>
**Train/serve skew**
When data is prepared one way during [training](#training) and a different way when the live server uses the [model](#model), so the model receives something it was not trained on and gives worse answers without any error.
*In this project:* prevented by keeping all preparation inside the saved [pipeline](#pipeline); defining every field, value and unit once in [../src/loanwise/domain/schemas.py](../src/loanwise/domain/schemas.py); converting units only in the [sanitizer](#sanitizer); a test that the field lists match; fixing the scikit-learn version; and the [sanity check](#sanity-check).

<a id="training"></a>
**Training**
The process in which an [algorithm](#algorithm) looks at past cases whose answers are known and adjusts a [model](#model)'s numbers until its answers match those past answers as well as possible.
*In this project:* `python3 scripts/train_model.py` (or `make train`) trains three models, picks one, checks it and saves it. It takes about a minute.

<a id="training-split"></a>
**Training split**
The part of the [dataset](#dataset) used to [train](#training) and choose models.
*In this project:* 80 % of `loan.csv`, 491 rows. After the winner is chosen it is retrained on all 614 rows before saving.

<a id="true-positive"></a>
**True positive / true negative**
Two kinds of correct answer: "yes" when the truth was "yes" (true positive), and "no" when the truth was "no" (true negative).
*In this project:* 84 true positives and 21 true negatives on the 123 test rows.

## U

<a id="unit-test"></a>
**Unit test**
A [test](#test) of one small piece of [code](#code) on its own, without a real network or [database](#database).
*In this project:* 62 unit tests in [../tests/unit/](../tests/unit/), covering validation, the sanitizer, guardrails, features, settings, CORS and services.

<a id="url"></a>
**URL (web address)**
The text that identifies a page or [endpoint](#endpoint) on the internet, such as `http://127.0.0.1:5000/api/health`.

## V

<a id="validation"></a>
**Validation (input)**
Checking that the information a user typed is complete and makes sense before using it.
*In this project:* first in the [browser](#browser) for instant feedback ([../frontend/src/lib/fields.js](../frontend/src/lib/fields.js)), then on the [server](#server), which is the check that counts ([../src/loanwise/domain/validation.py](../src/loanwise/domain/validation.py)). It accepts everyday formats ("₹ 25,000", "25k", "2 lakh", "30 years") and refuses blanks, negative numbers, words in number fields and out-of-range values, listing every problem at once. Not to be confused with [cross-validation](#cross-validation).

<a id="variance"></a>
**Variance (of a model's score)**
How much a [model](#model)'s score changes when it is trained or tested on a different selection of rows.
*In this project:* high, because the dataset is small: the [standard deviation](#standard-deviation) across the five cross-validation parts (about 0.045) is larger than the differences between the three models.

<a id="verdict"></a>
**Verdict**
The headline result shown to the user.
*In this project:* "Likely Approved" or "Likely Rejected", with a one-sentence headline and 3 to 5 plain-English reasons ([../src/loanwise/domain/messages.py](../src/loanwise/domain/messages.py)).

<a id="virtual-environment"></a>
**Virtual environment**
A folder holding a private set of [Python](#python) [libraries](#library) for one project, so that the versions it needs do not clash with other projects on the same computer.
*In this project:* `run.sh` and `run.bat` create `.venv` on the first run.

## W

<a id="website"></a>
**Website**
A set of pages, stored on a [server](#server), that people open in a [browser](#browser) by typing or clicking a [URL](#url).
*In this project:* the LoanWise website has a home page, the three-step loan form, a result page, a "How it works" page and a history of past checks.

<a id="wsgi"></a>
**WSGI (Web Server Gateway Interface)**
The agreed standard for how a program that runs web servers, such as [gunicorn](#gunicorn), hands requests to a [Python](#python) web application, such as one built with [Flask](#flask).
*In this project:* [../wsgi.py](../wsgi.py) creates the application as `app`; gunicorn runs `wsgi:app`.

---

[← Back to index](README.md) · [Next → 11 · FAQ and viva prep](11-faq-and-viva-prep.md)
