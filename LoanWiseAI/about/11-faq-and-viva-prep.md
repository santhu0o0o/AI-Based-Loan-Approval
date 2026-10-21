# 11 · FAQ and Viva Prep

> **In short:** 65 questions: eight that a complete beginner would ask, then 57 that an examiner, interviewer or senior engineer is likely to ask about LoanWise AI, each with a short model answer built on the project's real numbers and design decisions, and a link to the chapter that goes deeper. Several are trick questions with a false or loaded premise; the answers say so. The page ends with a two-minute elevator pitch to memorise and a ten-slide presentation outline. All metrics come from `artifacts/models/model_info.json` (training run 2026-10-20); the confusion matrix and best hyperparameters were re-derived by re-running `evaluate_models()` on the same split.

**Key numbers to know by heart**

| What | Value |
|---|---|
| Labelled rows | 614 (422 approved, 192 rejected, 68.7 % approved) |
| Train / hold-out split | 491 / 123 rows, stratified, `random_state=42` |
| Chosen model | Logistic Regression, `C = 0.1` |
| 5-fold CV accuracy | LR 0.7983 ± 0.0457 · RF 0.7962 ± 0.0436 · DT 0.7840 ± 0.0461 |
| Hold-out (all three models) | accuracy 0.8537, precision 0.8317, recall 0.9882, F1 0.9032 |
| Always-approve baseline | 0.6911 |
| Hold-out confusion matrix | 84 TP, 17 FP, 21 TN, 1 FN |
| Approval rate by credit history | good 79.6 % · bad 7.9 % |
| Top feature | Credit History, importance 0.3292 |
| Guardrails | EMI > 65 % of income → reject; loan > 60 × monthly income → reject |
| Tests | 90 (62 unit, 28 integration) |

**Sections:** [Beginner questions](#questions-a-complete-beginner-would-ask) · [Project & motivation](#project--motivation) · [Dataset](#dataset) · [Preprocessing & features](#preprocessing--features) · [Algorithms](#algorithms) · [Training & evaluation](#training--evaluation) · [Results & interpretation](#results--interpretation) · [Validation, guardrails & edge cases](#validation-guardrails--edge-cases) · [Backend & API](#backend--api) · [Frontend & UX](#frontend--ux) · [Ethics, fairness & limitations](#ethics-fairness--limitations) · [Deployment & scaling](#deployment--scaling) · [What would you do with more time?](#what-would-you-do-with-more-time) · [Elevator pitch](#two-minute-elevator-pitch) · [Slide outline](#ten-slide-presentation-outline)

---

## Questions a complete beginner would ask

These answers assume no knowledge of computers or artificial intelligence. Words in links are explained in the [glossary](10-glossary.md); [00 · AI from zero](00-ai-from-zero.md) covers the basics step by step.

### B1. What is AI?
"AI" ([artificial intelligence](10-glossary.md#artificial-intelligence)) is the name for computer programs that produce answers people would normally need judgement for, such as "is this loan likely to be approved?". The kind used here is [machine learning](10-glossary.md#machine-learning): instead of a person writing every rule, the computer works out the rules from past examples. In LoanWise AI, the "AI" part is one calculation that takes your 11 answers and returns a number between 0 and 1: the estimated [probability](10-glossary.md#probability) that a lender would approve the loan. It does not think, have opinions or know anything beyond those 11 answers and the patterns it found in past applications.

### B2. Is this a robot? Is someone watching my answers?
No. There is no robot and no person reviewing your answers. LoanWise AI is a website: a page in your [browser](10-glossary.md#browser) that sends your answers to a program on a [server](10-glossary.md#server). That program does arithmetic on them and sends back the result, usually in well under a second. The same answers always give the same result, unless the model is retrained.

### B3. How can a computer "learn"?
It is given 614 past loan applications where the outcome is known (422 approved, 192 rejected). It starts with a formula that gives each piece of information a number, called a [weight](10-glossary.md#coefficient), and then repeatedly adjusts those weights until the formula's answers match the past outcomes as closely as possible. That adjustment process is called [training](10-glossary.md#training). When it finishes, the weights are saved; for example, good credit history ended up with the largest positive weight (+1.157), because in the past 79.6 % of people with good credit were approved against 7.9 % with bad. "Learning" here means nothing more than finding those numbers.

### B4. Does it understand me?
No. It never sees your name, does not read sentences, and cannot take into account anything outside the 11 questions. It only uses the numbers and choices you enter: for example "₹45,000 a month", "graduate", "good credit". If something important about your situation is not one of those 11 questions (your existing loans, for instance), it simply does not know about it.

### B5. Where does the answer come from?
From two things, one after the other. First, the trained [model](10-glossary.md#model) turns your answers into a probability of approval; 0.5 or more means "Likely Approved". Second, a few fixed rules written by a person check the result against your real numbers: if the monthly payment would be more than 65 % of your income, or the loan is more than five years of your income, the answer becomes "Likely Rejected" whatever the model said. The page then shows the verdict, how confident it is (High, Medium or Low), 3 to 5 reasons in plain words, and an estimated monthly payment.

### B6. Can it be wrong?
Yes, and you should expect it sometimes. On 123 past applications it had never seen, it was right 105 times and wrong 18 times (85 % correct). Most of its mistakes were saying "approved" for people who had in fact been rejected (17 of the 18). It learned from only 614 old applications, so it can be further off for situations that were rare in that data, such as very high incomes or very large loans. Treat it as a rough first check, not as an answer.

### B7. Who decides whether I get the loan?
The bank or lender, always. LoanWise AI is not connected to any bank and cannot approve or refuse anything. It gives an estimate of what a lender in the past data would probably have done, so that you can see whether your plan looks realistic and what might help, such as a smaller loan or a longer repayment period.

### B8. Is my data stored?
Partly. The website never asks for your name, phone number, address or any ID. Your answers are kept in your browser while the tab is open, so a refresh does not lose them, and are cleared when you close it. Each check (your 11 answers and the result) is also saved in a small [database](10-glossary.md#database) file on the server running LoanWise, so the History page can list past checks. Anyone who can open that site can see and clear that history with the "clear" button; there are no user accounts. If LoanWise runs on your own computer (`./run.sh`), that file stays on your computer at `instance/loanwise.db`.

## Project & motivation

### Q1. What does LoanWise AI do, in one or two sentences?
It estimates whether a home-loan application is likely to be approved and explains why in plain English. A user fills in 11 answers in a three-step web form; a Flask API validates them, scores them with a scikit-learn Logistic Regression pipeline, applies common-sense affordability rules, and returns a verdict, a confidence label, 3 to 5 reasons and an estimated monthly payment. → [01 · What and why](01-what-and-why.md)

### Q2. Who is it for, and why build it?
It is designed for someone with no financial or technical background who wants to know, before visiting a bank, whether a loan is realistic. That is why the form accepts everyday input ("25k", "2 lakh", "30 years"), every message is plain English, and no stack trace or technical error is ever shown. It is an educational self-assessment tool, not a lending decision, and the README and model card say so explicitly. → [../README.md](../README.md), [../docs/MODEL_CARD.md](../docs/MODEL_CARD.md)

### Q3. Walk me through what happens when I press "Check my chances".
The React form runs layer-1 checks and sends JSON to `POST /api/predict`. Flask decodes the body (400 if unreadable), then `PredictionService` runs layer-2 validation (422 with every field error if anything is wrong), gets the model from `ModelRegistry` (503 if none), and the sanitizer builds the exact 11-column DataFrame in dataset units. The pipeline returns P(approve); the guardrails combine it with the applicant's real numbers to produce the verdict, confidence and reasons. The result is saved to SQLite and returned with status 200. → [02 · How it works end to end](02-how-it-works-end-to-end.md), [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)

### Q4. Is this a real credit-decision system?
No. It is trained on 614 historical rows of unknown provenance, has no information about existing debts, employment length, collateral or interest rates, and its probabilities are not calibrated. It also uses Gender and Marital status, which a real lender generally could not. The honest description is "an educational estimate with sensible safety rails", and the UI and docs present it that way. → [Q51](#q51-isnt-using-gender-discriminatory)

## Dataset

### Q5. Describe the dataset.
`data/raw/loan.csv` has 614 labelled applications and 13 columns: `Loan_ID`, 11 inputs and the target `Loan_Status` (Y/N). The inputs are six categoricals (Gender, Married, Dependents, Education, Self_Employed, Property_Area) and five numerics (ApplicantIncome, CoapplicantIncome, LoanAmount, Loan_Amount_Term, Credit_History). 422 rows are approved and 192 rejected. Incomes are skewed: median applicant income is ₹3,812.5 a month but the maximum is ₹81,000. → [03-dataset.md](03-dataset.md)

### Q6. Why not use `test.csv` to evaluate the model?
Because it has no labels. `data/raw/test.csv` has 367 rows and 12 columns: the same inputs but no `Loan_Status`, so there is nothing to compare predictions against. The project therefore holds out 20 % of the labelled `loan.csv` (123 rows) as its test set. `test.csv` is used only for the "Fill example" button (`GET /api/sample`) and for the post-training smoke test that loads the saved model and scores its first five rows. → [03-dataset.md](03-dataset.md), [../src/loanwise/services/sample_service.py](../src/loanwise/services/sample_service.py)

### Q7. Why is income monthly but loan amount in thousands?
That is how the source dataset stores them: `ApplicantIncome` and `CoapplicantIncome` are monthly rupees, while `LoanAmount` is in thousands of rupees (median 128, meaning ₹1,28,000). The model must see the same units it was trained on, so the API takes the loan in full rupees, which is natural for users, and the sanitizer divides by `LOAN_AMOUNT_UNIT = 1000` before scoring. Inside the pipeline the loan is multiplied back by 1000 to compute the EMI-to-income ratio in consistent rupees. The units are defined once in [../src/loanwise/domain/schemas.py](../src/loanwise/domain/schemas.py) so the conversion cannot drift. → [04 · Data preparation and features](04-data-preparation-and-features.md)

### Q8. Which values are missing, and how did you handle them?
Credit_History 50, Self_Employed 32, LoanAmount 22, Dependents 15, Loan_Amount_Term 14, Gender 13 and Married 3. Imputation happens inside the pipeline: the most frequent value for categoricals and for Credit_History (which is 0/1, so a median of 1 or a mean of 0.84 would be odd), and the median for the other numerics. Doing it inside the pipeline means each CV fold learns its own fill values, so no information leaks from the validation fold. One consequence worth admitting: missing credit history becomes "good" (in the data, 74 % of those rows were in fact approved). → [04 · Data preparation and features](04-data-preparation-and-features.md)

### Q9. Is the data imbalanced, and what did you do about it?
Moderately: 68.7 % approved. I stratified both the train/test split and the CV folds so every fold keeps that ratio, and I report the always-approve baseline (0.6911 on the hold-out) alongside accuracy. I did not resample or re-weight classes, which is a reasonable next experiment if the goal were to catch more rejections (see [Q28](#q28-why-is-accuracy-alone-misleading-here)).

### Q10. What did the exploratory analysis show?
Credit history dominates: 79.6 % approval with good history versus 7.9 % with bad. Property area matters next (Semiurban 76.8 %, Urban 65.8 %, Rural 61.5 %), and graduates are approved more often (70.8 % vs 61.2 %). Self-employment makes almost no difference (68.3 % vs 68.6 %). Training writes four charts to `artifacts/reports/eda/` (class balance, approval rate by group, income distribution, missing values). → [03-dataset.md](03-dataset.md), [../src/loanwise/ml/eda.py](../src/loanwise/ml/eda.py)

## Preprocessing & features

### Q11. Walk me through the pipeline.
Five steps, all inside one scikit-learn `Pipeline` ([../src/loanwise/ml/pipelines.py](../src/loanwise/ml/pipelines.py)). `clean` forces the 11 contract columns and correct types; `impute` fills gaps; `features` adds total income, EMI, the EMI-to-income ratio and its capped log; `encode` keeps only Credit_History, Loan_Amount_Term and the log ratio as numerics (standardised for Logistic Regression) and one-hot encodes the six categoricals; `model` is the classifier. The output is 18 columns for the model. → [04 · Data preparation and features](04-data-preparation-and-features.md)

### Q12. Why put the preprocessing inside the saved pipeline?
So that training and serving cannot disagree. The saved `loan_model.pkl` accepts the raw 11-column frame and does every transformation itself, so the API does not reimplement imputation or encoding and cannot forget a step. It also prevents data leakage during cross-validation, because each fold fits its own imputer and scaler. The cost is that the pickle references `loanwise.ml.features` by import path, so that module cannot be moved or renamed without retraining; a unit test guards this.

### Q13. What was the income bug, and how did you fix it?
The first version gave the model raw ApplicantIncome, CoapplicantIncome and LoanAmount. On 614 rows those features picked up counter-intuitive negative signs, so raising someone's income could *lower* their approval chance, and the effect grew for very large incomes. (A quick reproduction: a plain Logistic Regression on standardised raw columns gives co-applicant income a negative coefficient of about −0.13.) The fix has three parts: income and loan size now reach the model **only** through `log1p(clip(EMI / total income, 0, 10))`, so more income always lowers the ratio and a bigger loan always raises it; the tree models get `monotonic_cst`; and `check_monotonicity()` sweeps incomes and loan sizes on three profiles and aborts training, saving nothing, if approval ever moves the wrong way. All 12 sweeps pass for the saved model. → [04 · Data preparation and features](04-data-preparation-and-features.md), [../src/loanwise/ml/features.py](../src/loanwise/ml/features.py)

### Q14. Why clip and log the ratio?
The raw ratio can be enormous for tiny incomes (a ₹1 crore loan on ₹1,000 a month), and a linear model would let that one value swamp everything. Clipping to [0, 10] caps it; `log1p` compresses the remaining range and is safe at zero. Both are monotonic transforms, so the direction "higher ratio means less affordable" is preserved. Extreme cases are then handled explicitly by the guardrails rather than by extrapolation.

### Q15. The model's EMI ignores interest but the guardrails use 9 %. Isn't that inconsistent?
It is deliberate. Inside the model, the EMI only needs to be monotonic (bigger loan → bigger EMI, longer term → smaller EMI), and `loan / term` achieves that with no assumed interest rate baked into a learned feature. The guardrails and the number shown to the user need a *realistic* payment, so they use a standard amortised EMI at 9 % a year. For example, ₹25,00,000 over 240 months gives an `emi_estimate` of ₹22,493. The trade-off is documented in [../src/loanwise/ml/features.py](../src/loanwise/ml/features.py) and [../src/loanwise/domain/guardrails.py](../src/loanwise/domain/guardrails.py).

### Q16. Why one-hot encoding rather than label encoding?
Label encoding (Rural = 0, Semiurban = 1, Urban = 2) invents an order and equal spacing that do not exist, which a linear model would take literally. One-hot gives each category its own 0/1 column and its own coefficient. `handle_unknown="ignore"` means an unexpected value becomes all zeros instead of an exception, although validation already prevents unknown values reaching the model.

### Q17. Why scale only for Logistic Regression?
Logistic Regression with L2 regularisation is sensitive to feature scale: an unscaled feature with large values gets an artificially small coefficient and is penalised differently. Standardising the three numeric columns puts them on a comparable footing and makes coefficient sizes roughly comparable. Trees split on thresholds, so scaling changes nothing for them, and the tree pipelines use `"passthrough"`.

### Q18. How do you prevent train/serve skew?
Five things. All preprocessing lives in the saved pipeline. Every field name, allowed value, limit and unit is defined once in [../src/loanwise/domain/schemas.py](../src/loanwise/domain/schemas.py) and used by validation, the sanitizer and training. The sanitizer is the single place units are converted. A unit test checks that schema columns match the pipeline's columns. And after saving, training loads the pickle in a fresh Python process and scores probe rows, exactly as the API would; scikit-learn is pinned to 1.9.1 so the pickle loads identically in production.

## Algorithms

### Q19. Why these three algorithms?
They cover the main families for small tabular data: a linear model (Logistic Regression), a single interpretable non-linear model (Decision Tree) and an ensemble (Random Forest). All three output probabilities, which the product needs, and all three support the monotonicity requirement (Logistic Regression through the feature design; the trees through `monotonic_cst`). With 614 rows, heavier models such as gradient boosting or neural networks would mostly add variance. → [05 · Algorithms](05-algorithms.md)

### Q20. Explain Logistic Regression simply.
It gives each feature a weight, adds up `intercept + Σ weight × feature` to get a score called the log-odds, and passes that score through the sigmoid `1 / (1 + e^(−z))` to get a probability between 0 and 1. Training finds the weights that best explain the observed approvals, with an L2 penalty that keeps weights small. In the saved model the largest weight is +1.157 on standardised Credit_History; the EMI-to-income ratio has −0.218, so less affordable loans score lower.

### Q21. How does a Decision Tree decide its splits?
At each node it tries candidate thresholds on each feature and picks the one that most reduces Gini impurity, which measures how mixed approvals and rejections are in each branch. It repeats until it hits limits such as `max_depth` or `min_samples_leaf`. The tuned tree here is only depth 2 with at least 10 rows per leaf, which says the data supports very few reliable rules.

### Q22. How is a Random Forest different?
It trains many trees (300 here), each on a bootstrap sample of rows and considering a random subset of features at each split, then averages their probabilities. That averaging reduces the variance of single trees. The tuned forest used `max_depth = 4` and `min_samples_leaf = 5`. It came a close second on CV (0.7962 vs 0.7983).

### Q23. What are monotonic constraints, and why only on the trees?
A monotonic constraint forces the prediction to move in only one direction as a feature rises. The trees get `monotonic_cst` with +1 on Credit_History, −1 on the log EMI-to-income ratio and 0 on everything else. Logistic Regression has no such parameter, but it does not need one: it is linear in each feature, so whatever sign it learns for the ratio applies everywhere, and the training-time sweep verifies that sign is the safe one. → [../src/loanwise/ml/pipelines.py](../src/loanwise/ml/pipelines.py)

## Training & evaluation

### Q24. How did you split and validate?
A stratified 80/20 split with `random_state=42` gives 491 training and 123 hold-out rows. Each candidate is tuned with `GridSearchCV` using stratified 5-fold CV on the 491 rows, scoring accuracy, and the tuned pipeline's 5-fold CV mean and standard deviation are recorded. The hold-out set is scored once per model for reporting only. The winner is then refitted on all 614 rows before saving. → [06 · Training and evaluation](06-training-and-evaluation.md), [../src/loanwise/ml/evaluation.py](../src/loanwise/ml/evaluation.py)

### Q25. Which hyperparameters did you tune, and what won?
Logistic Regression: `C` in {0.01, 0.1, 1, 10}, best 0.1. Decision Tree: `max_depth` in {2, 3, 4, 6} × `min_samples_leaf` in {5, 10, 20}, best depth 2 and leaf 10. Random Forest (300 trees): `max_depth` in {4, 6, 8} × `min_samples_leaf` in {3, 5, 10}, best depth 4 and leaf 5. The grids are deliberately small because 491 rows cannot support a large search without overfitting the CV score itself.

### Q26. Why did Logistic Regression win if the Decision Tree scored higher on the test set?
The premise is wrong for the current model: all three score exactly 0.8537 on the hold-out set, and the Decision Tree actually has the *lowest* CV accuracy (0.7840). More importantly, the rule never looks at the test set. The model is chosen by the highest mean 5-fold CV accuracy on the training split, ties within 0.001 going to the lower CV standard deviation; Logistic Regression won with 0.7983. If a tree ever did score higher on the hold-out, I would still not switch, because choosing by the test set turns it into a second validation set and its score stops being an honest estimate. With 123 rows, one row is worth 0.81 percentage points, so small hold-out differences are noise anyway.

### Q27. Why are all three models' hold-out predictions identical?
Because on these 123 rows all three effectively reduce to one rule: approve if credit history is good. I checked this directly: "approve when Credit_History is 1 (missing counts as 1)" produces exactly the same 123 predictions and the same confusion matrix (84 TP, 17 FP, 21 TN, 1 FN). Credit history is so dominant (79.6 % vs 7.9 % approval) that the other features rarely push a probability across 0.5. The models do differ in their probabilities and in CV, which is why CV is the better comparison. → [06 · Training and evaluation](06-training-and-evaluation.md)

### Q28. Why is accuracy alone misleading here?
First, the classes are imbalanced: always saying "approved" already gets 0.6911, so 0.8537 is a 16-point gain, not 85 % skill. Second, accuracy hides which mistakes are made: recall is 0.9882 but precision only 0.8317, and the model catches only 21 of the 38 real rejections. For a loan tool, approving someone who would be rejected (17 cases) is the more harmful error, and accuracy does not show that. That is why the report includes precision, recall, F1 and the baseline, and why the guardrails lean conservative.

### Q29. Why select by CV accuracy rather than F1 or ROC AUC?
Accuracy was the simplest metric to explain and defend for this brief, and with the classes stratified it is still informative relative to the stated baseline. F1 on the positive (approved) class would barely separate the models, since they all approve good-credit applicants. If I changed the metric, I would pick ROC AUC or log loss to judge the quality of the probabilities, or recall on rejections if catching risky applications mattered most. → [Q57](#q57-what-would-you-do-with-more-time)

### Q30. What exactly is the monotonicity check?
`check_monotonicity()` takes three hand-written base profiles (a strong salaried applicant, a weak self-employed applicant with bad credit, and a high-income urban one) and, for each, sweeps 60 log-spaced values of applicant income, co-applicant income and both together (₹1,000 to ₹1 crore a month), and of loan size (₹10,000 to ₹1 crore). Approval must never fall as income rises nor rise as the loan grows (tolerance 1e-9). That is 12 sweeps; any failure raises `MonotonicityError` before the model is saved. For profile 1, for example, P(approve) rises from 0.832 to 0.894 across the applicant-income sweep and falls from 0.892 to 0.012 across the loan sweep. → [../src/loanwise/ml/evaluation.py](../src/loanwise/ml/evaluation.py)

### Q31. Is Logistic Regression really better than Random Forest?
Not in any statistically meaningful sense. The CV gap is 0.0021, while the CV standard deviations are about 0.044 to 0.046. Logistic Regression wins by the stated rule, and it has practical advantages that would justify it even at a tie: it is simpler, faster, easier to explain to a non-technical user and an examiner, and its monotonic behaviour follows directly from its coefficients. The honest answer is "they are equivalent on this data; we chose the simplest one by a pre-declared rule."

## Results & interpretation

### Q32. Explain the hold-out confusion matrix.
With "approved" as the positive class: 84 true positives, 1 false negative, 21 true negatives and 17 false positives, out of 123 rows. Precision is 84 / 101 = 0.8317, recall 84 / 85 = 0.9882 and accuracy 105 / 123 = 0.8537. In words: the model almost never rejects someone who was approved, but it wrongly approves 17 of the 38 people who were rejected, all of whom had good (or missing, so imputed as good) credit history.

### Q33. Which features matter most, and how did you measure that?
I used the absolute Logistic Regression coefficients, summed the one-hot columns back into readable features and normalised the top 8 to sum to 1. Credit History 0.3292, Property Area 0.2234, Number of Dependents 0.1302, Marital Status 0.1143, Education 0.0701, EMI-to-Income Ratio 0.0621, Loan Term 0.0550, Gender 0.0158. One caveat: only the three numeric columns are standardised, while one-hot columns are raw 0/1, so comparing magnitudes across those two groups is approximate. Permutation importance would be a more robust alternative. → [../src/loanwise/ml/evaluation.py](../src/loanwise/ml/evaluation.py)

### Q34. What does "confidence" mean? Is it a real probability?
It is the model's probability for the side it chose: `p` if approved, `1 − p` if rejected, then adjusted by guardrails (at least 0.90 on a forced rejection, at most 0.65 for an approval with bad credit). Labels are High ≥ 0.75, Medium ≥ 0.60, otherwise Low. The probabilities are not calibrated, so "0.69" should not be read as "69 of 100 such people get approved". For example, a graduate earning ₹45,000 a month asking for ₹25 lakh over 20 years with good credit gets "Likely Approved" at 0.6934, Medium, with a warning that the EMI is 50 % of income.

### Q35. Why is "Self Employed" missing from the feature-importance list?
The report keeps the top 8 of 9 readable features, and Self Employed is ninth. That matches the data, where approval rates for self-employed and salaried applicants are almost identical (68.3 % vs 68.6 %). It is still an input to the model; it simply has very little influence.

## Validation, guardrails & edge cases

### Q36. Why have guardrails if you already have an ML model?
Because a model trained on 614 rows, almost all with modest incomes and loans, can be confidently wrong on inputs it has never seen. Without rules, a ₹1 crore loan on a ₹5,000 salary with good credit could come back "approved", since credit history dominates. Guardrails use the applicant's real numbers and well-understood lending logic to catch those cases, and they make the explanations concrete ("the monthly payment would be about ₹89,973, more than your whole income"). The model handles the patterns in the data; the rules handle facts the data cannot teach. → [07 · Validation and guardrails](07-validation-and-guardrails.md)

### Q37. What exactly are the guardrails?
Four rules in [../src/loanwise/domain/guardrails.py](../src/loanwise/domain/guardrails.py), using an amortised EMI at 9 % a year. **R1:** EMI above 65 % of total monthly income forces "Likely Rejected". **R2:** a loan above 60 times total monthly income (more than five years of income) forces "Likely Rejected". **R3:** bad credit is always given as a negative reason and, if the model still approves, confidence is capped at 0.65. **R4:** an EMI between 45 % and 65 % of income adds a "big stretch" reason without overriding. When R1 or R2 fires, `guardrail_applied` is true and confidence is `max(1 − p, 0.90)`.

### Q38. Can a guardrail turn a rejection into an approval?
No, by design. Guardrails can only force a rejection or lower confidence. For an advice tool, telling someone a loan is unlikely when it might be possible is a much safer failure than encouraging them to take on an unaffordable loan. This is asserted in the guardrail tests ([../tests/unit/test_guardrails.py](../tests/unit/test_guardrails.py)).

### Q39. What happens if I type "2.5 lakh", "30 years" or "abc"?
Validation is forgiving on format and strict on meaning. "2.5 lakh" becomes ₹2,50,000 and "30 years" becomes 360 months, each with a note in `warnings` saying how it was read; "₹ 25,000", "Rs. 25000", "25k" and " YES " also work. "abc" in an income field, a negative number, NaN, a boolean, an unknown choice or a term such as 7 months produce a specific plain-English message for that field. All errors are collected and returned together as a 422 so the form can highlight every red box at once. → [../src/loanwise/domain/validation.py](../src/loanwise/domain/validation.py)

### Q40. What happens if the model file is missing?
The app still starts. `ModelRegistry.get()` returns `None`, `/api/health` reports `"model_loaded": false`, and `POST /api/predict` returns 503 with "Our loan checker isn't ready yet...". Validation runs *before* the model check, so a user with a broken form still gets 422 field errors. If a model was loaded and the file later disappears or a reload fails, the registry keeps serving the previous model. `run.sh` also trains a model automatically on first run if the file is missing. → [../src/loanwise/services/model_registry.py](../src/loanwise/services/model_registry.py)

### Q41. What if someone enters a huge income, such as ₹90 lakh a month?
Monthly income up to ₹1,00,00,000 is accepted; above that is a validation error that suggests they may have typed a yearly figure. Above ₹5,00,000 a month the sanitizer adds a warning to double-check. The model is safe here because income only enters through the capped ratio, and the monotonicity sweep goes up to ₹1 crore a month; a "₹90 lakh income" row is also one of the probes in the post-training sanity check. Real values are never clamped, because that would distort the ratio.

### Q42. Why validate on the server if the browser already validates?
Browser checks are for instant feedback only; anyone can bypass them with a script or `curl`. Layer 2 on the server is the real gate and the only one the model trusts. Layer 3, the sanitizer, then guarantees the exact columns, types and units. Keeping layer 2 in pure Python with no Flask also means it is covered by 22 fast unit tests.

## Backend & API

### Q43. Why Flask, an app factory and blueprints?
Flask is small and enough for six JSON endpoints plus static files. The app factory `create_app(settings, model=...)` builds a fresh app per call, so tests can inject a fake, broken or missing model and a temporary database without touching globals. Blueprints group routes (`predict`, `history`, `meta`) under `/api`, and the SPA blueprint is registered last so its catch-all route cannot shadow the API. Layering is strict: `domain` has no Flask and no I/O, `services` knows nothing about HTTP, and `api` only maps exceptions to status codes. → [02 · How it works end to end](02-how-it-works-end-to-end.md), [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)

### Q44. Which status codes do you return, and why 422 rather than 400 for bad answers?
200 success; 400 when the body is not readable JSON or not an object; 404/405 for unknown API paths or wrong methods; 413 above 32 KB; 422 when the JSON is fine but the answers are invalid; 503 when the model, model report or demo data is unavailable; 500 for anything unexpected. 400 means "I could not read your request", 422 means "I read it, but these fields are wrong", and the 422 body carries an `errors` map the form uses to mark each field. Every error body is `{"ok": false, "message": ...}` in plain English; exception text is logged, never returned. → [../docs/API.md](../docs/API.md), [../src/loanwise/api/errors.py](../src/loanwise/api/errors.py)

### Q45. How is history stored, and what if saving fails?
In SQLite at `instance/loanwise.db`, in a `predictions` table holding the cleaned inputs and full result as JSON, plus the raw model probability for debugging. Each call opens a short-lived connection and writes are serialised with a lock. History is a nice-to-have, so if saving fails the error is logged and the user still gets their result with `"id": null`. `GET /api/history` returns the newest first (default 50, maximum 500), and `DELETE /api/history` clears it.

### Q46. How does hot model reload work, and is it thread-safe?
On each request `ModelRegistry` compares the model file's modification time with the one it loaded. If it changed, it reloads under a `threading.Lock`, double-checking inside the lock so only one thread loads. The new object must have `predict_proba`, otherwise the old model is kept. So re-running `make train` updates a running dev server without a restart. Under gunicorn each worker process has its own registry and reloads independently.

### Q47. How did you test the system?
90 tests run by `python3 -m unittest discover -s tests -t .` (pytest also works). 62 unit tests cover validation (22), services (11), guardrails (8), features and schema consistency including the saved model's monotonicity (8), config (6), the sanitizer (4) and CORS (3). 28 integration tests drive the real Flask app with fake, broken, missing and real models, plus SPA fallback and history round-trips. Code quality is checked with ruff and `mypy --strict`. → [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)

## Frontend & UX

### Q48. Why React, and why esbuild instead of Vite or create-react-app?
React 19 with React Router gives a small single-page app with five pages (Home, Check, Result, How it works, History) plus a not-found page. esbuild is a single, fast build tool with no plugin ecosystem to configure; the custom scripts in `frontend/scripts/` handle production builds and a dev server on port 5173 that proxies `/api` to Flask on 5000. A pre-built `frontend/dist` ships with the repository, so Node is only needed to change the UI. → [09 · Frontend](09-frontend.md)

### Q49. How is the form designed for a first-time user?
It is a three-step wizard (About you, Your money, Your loan), with tap-to-choose answers for categoricals, plain questions ("Are you married?") and the loan term chosen in years. Credit history is asked as "Have you paid back past loans or credit cards on time?" with an extra option, "I never had a loan or card", which is sent as `"good"` because the person has missed no payments. Answers are kept in `sessionStorage`, so a refresh or a server error never loses them. The result page shows the verdict, confidence label, reasons and estimated EMI. → [../frontend/src/lib/fields.js](../frontend/src/lib/fields.js)

### Q50. How does the UI handle errors and accessibility?
`api.js` turns every failure into an `ApiError` with a kind (network, timeout, validation, server, bad-response) and a plain-English message, with a 15-second timeout (20 seconds for predictions). A 422 maps each server error back onto its field and jumps to the right step. For accessibility there is a skip link, `aria-live` regions for field errors and toasts, the Atkinson Hyperlegible font (designed by the Braille Institute for readability), and `MotionConfig reducedMotion="user"` plus a `prefers-reduced-motion` stylesheet rule so animations respect the user's system setting. → [../frontend/src/api.js](../frontend/src/api.js)

## Ethics, fairness & limitations

### Q51. Isn't using Gender discriminatory?
Yes, it is a real concern, and the project says so openly. The original specification required all dataset inputs, so Gender and Married are used; Gender's importance is small (0.0158), but Marital Status is the fourth-largest factor (0.1143), and together they account for about 13 %. In the data, approval is 69.3 % for men versus 67.0 % for women and 71.6 % for married versus 62.9 % for unmarried applicants, and the model reproduces those patterns. In most jurisdictions using sex or marital status in credit decisions is prohibited or tightly restricted. Before any real use I would remove both, review proxies such as Dependents, retrain, measure outcome and error-rate parity across groups, and get legal review. → [../docs/MODEL_CARD.md](../docs/MODEL_CARD.md), [03 · Dataset: limitations and biases](03-dataset.md#8-limitations-and-biases)

### Q52. Are there less obvious fairness problems?
Three. Property Area is the second-largest factor and can act as a proxy for income or community. Missing credit history is imputed as "good", and the UI's "never had a loan" also maps to "good"; that is generous to people with thin files but is an assumption, not a fact. And the dataset's provenance and time period are unknown, so historical lending bias may be baked into the labels. None of these is measured yet, which is the honest status.

### Q53. What are the main limitations?
A small, old, single-source dataset of 614 rows. High variance, with CV standard deviation around 0.045, larger than the gaps between models. Few rows with very high incomes or loans, so those predictions are extrapolations (mitigated by the ratio design and guardrails). No calibration. No information about existing debts, employment length, collateral or actual interest rates. A fixed 9 % rate for the EMI estimate. Single-instance SQLite storage. → [../docs/MODEL_CARD.md](../docs/MODEL_CARD.md)

## Deployment & scaling

### Q54. How do you run and deploy it?
Locally, `./run.sh` (or `run.bat`) creates `.venv`, installs dependencies, trains the model if missing, builds the frontend if missing and starts the server, falling back to port 8000 if 5000 is busy, which is common on macOS because of AirPlay. In production, `gunicorn wsgi:app`. The [../Dockerfile](../Dockerfile) is multi-stage: `node:20-slim` builds the UI, then `python:3.12-slim` installs the package, copies the model and demo CSV, runs as non-root user `loanwise`, logs JSON and has a `HEALTHCHECK` on `/api/health`. → [08 · Backend](08-backend.md)

### Q55. How would this scale to many users?
Prediction is cheap (one pipeline call on one row), and the API is stateless apart from history, so it scales horizontally by adding gunicorn workers (`GUNICORN_WORKERS`, default 2) and containers behind a load balancer. Two things must change first. SQLite is per-instance, so history needs a shared database behind the same `HistoryRepository` interface. And the model should be versioned and deployed with the image or from a model store, rather than relying on file-modification hot reload in each worker.

### Q56. What security measures are in place?
Request bodies are capped at 32 KB (413 above). Text answers are limited to 60 characters, and NaN, Infinity and booleans are rejected. CORS allows only exact allowed hostnames, so look-alike domains are refused. Every response gets `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` and `Referrer-Policy: same-origin`. The SPA file server refuses paths that escape `frontend/dist`. Errors never expose stack traces, and the container runs as a non-root user. Not yet present: authentication, rate limiting, and protection for `DELETE /api/history`, which anyone who can reach the server can call. The model pickle must also only ever come from a trusted build, since loading a pickle can execute code.

## What would you do with more time?

### Q57. What would you do with more time?
1. **Fairness first:** retrain without Gender and Married, measure the accuracy cost, and report approval-rate and error-rate parity by group.
2. **Better evaluation:** repeated or nested CV and confidence intervals, plus ROC AUC, log loss and recall on rejections, since accuracy cannot separate the models.
3. **Calibrate** probabilities (`CalibratedClassifierCV`) so "confidence" means something measurable.
4. **Use the 50 missing credit histories honestly**, for example with a "missing" indicator instead of imputing "good".
5. **More and better data:** existing debts, employment length, actual interest rates; then the guardrails' 9 % assumption can go.
6. **Per-applicant explanations** from the model's own contributions (for example coefficient × feature), alongside the rule-based reasons.
7. **Production hardening:** a shared database, authentication on history, rate limiting, model versioning and drift monitoring.

---

## Two-minute elevator pitch

> LoanWise AI answers one question for people who have never applied for a loan: "Am I likely to be approved, and why?"
>
> You answer eleven simple questions in a three-step form. You can type your income as "45,000", "45k" or "₹ 45,000", and your loan as "25 lakh". The server checks every answer, collects every mistake at once and explains each one in plain English.
>
> Behind it is a scikit-learn pipeline trained on 614 real loan applications. I compared Logistic Regression, a Decision Tree and a Random Forest using five-fold cross-validation, and I chose the winner by cross-validation, never by the test set. Logistic Regression won with 79.8 % CV accuracy, and it scores 85.4 % on a held-out test set, against 69 % for simply approving everyone. Credit history is by far the strongest factor.
>
> Along the way I found a real problem: the first model had learned that a higher income *lowered* your chances. I fixed it by feeding income and loan size to the model only as an affordability ratio, the monthly instalment divided by income, and I added an automatic check that refuses to save any model where more income lowers approval or a bigger loan raises it.
>
> On top of the model sit common-sense lending rules. If the monthly payment would take more than 65 % of your income, or the loan is more than five years of your income, the answer is "Likely Rejected", whatever the model says. The rules can only make the answer more cautious, never less.
>
> You get a verdict, a confidence level, three to five reasons and an estimated monthly payment. Engineering-wise it is a layered Flask API with 90 automated tests, strict type checking, Docker deployment and a React front end built for accessibility.
>
> I'm also clear about its limits: it is a small dataset, it uses gender and marital status, which a real lender shouldn't, and it is an educational estimate, not a lending decision.

---

## Ten-slide presentation outline

| # | Slide | What to put on it | Speaker note |
|---|---|---|---|
| 1 | **LoanWise AI** | Title, one-line purpose, home-page screenshot (`docs/screenshots/home-desktop.png`) | "A plain-English loan-approval estimate for first-time borrowers." |
| 2 | **The problem** | Users don't know if a loan is realistic; forms are intimidating; banks don't explain rejections | Motivation and audience; it is not a lending decision. |
| 3 | **The data** | 614 rows, 11 inputs, 68.7 % approved; missing-value counts; credit-history approval 79.6 % vs 7.9 % | Why `test.csv` (no labels) is only for demos. |
| 4 | **Pipeline and features** | clean → impute → engineer → encode → model; the EMI-to-income ratio | All preprocessing inside the saved pipeline (no skew, no leakage). |
| 5 | **The income bug** | Before: income had a negative effect. After: income only via the ratio, monotonic constraints, 12-sweep check that blocks saving | The strongest "I debugged a real ML problem" story. |
| 6 | **Model comparison** | Table: CV 0.7983 / 0.7962 / 0.7840; hold-out 0.8537 for all; baseline 0.6911 | Chosen by CV, never by test; identical test predictions = credit-history rule. |
| 7 | **Interpreting results** | Confusion matrix 84 / 17 / 21 / 1; feature-importance bar chart | Why accuracy alone misleads; precision vs recall. |
| 8 | **Guardrails and validation** | Three validation layers; R1–R4; screenshots of 422 errors and a guardrail rejection | The model handles patterns, the rules handle facts; rules only ever make it more cautious. |
| 9 | **Architecture and engineering** | Layer diagram (api → services → domain/storage), endpoints, status codes, 90 tests, Docker | App factory, hot reload, plain-English errors. |
| 10 | **Ethics, limits, next steps** | Gender/Married use, small data, no calibration; the more-time list | End with the honest framing and one clear next step (remove protected attributes and audit). |

---

[← Back to index](README.md)
