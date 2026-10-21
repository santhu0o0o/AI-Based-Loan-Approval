# 01 · What and Why

> **In short.** LoanWise AI is a website. You answer 11 simple questions about yourself, your income and the home loan you want. The website then tells you whether a bank is likely to approve that loan, how sure it is, the reasons, and roughly how much you would pay each month. The answer comes from a computer program that studied 614 real past loan applications and the decisions made on them. On top of that program sit simple common-sense money rules that stop it from giving silly answers. The whole thing was built so that a person who has never applied for a loan, and has never used a computer for anything serious, can use it without help. It is a student project, not a bank, and it says so on every page.

---

## Contents

1. [The problem, in plain words](#1-the-problem-in-plain-words)
2. [Why predicting loan approval matters](#2-why-predicting-loan-approval-matters)
3. [What LoanWise AI does: one real example](#3-what-loanwise-ai-does-one-real-example)
4. [Who it is for](#4-who-it-is-for)
5. [Goals of the project](#5-goals-of-the-project)
6. [The design principle: "built for the dumbest person alive"](#6-the-design-principle-built-for-the-dumbest-person-alive)
7. [Disclaimer and ethics](#7-disclaimer-and-ethics)
8. [Scope: what it does and does not do](#8-scope-what-it-does-and-does-not-do)
9. [For the technically curious: the technology and why each piece was chosen](#9-for-the-technically-curious-the-technology-and-why-each-piece-was-chosen)

If the words "AI", "model", "data" or "training" are new to you, read [00 · AI from zero](00-ai-from-zero.md) first. This chapter uses them in the same sense.

---

## 1. The problem, in plain words

A **home loan** is money a bank lends you to buy a house. You pay it back in equal monthly amounts over many years, plus extra money called **interest**, which is the bank's charge for lending.

Before lending, the bank decides whether to say yes or no. It looks at things like:

* how much you earn each month,
* whether someone else (for example your husband, wife or parent) will help repay,
* how much you want to borrow and over how many years,
* whether you repaid past loans and credit-card bills on time.

The person applying usually cannot see how this decision is made. They fill in long forms, wait days or weeks, and may simply be told "no".

The problem LoanWise AI addresses: **can a person get a quick, honest, understandable estimate of their chances before they apply, and see what would improve them?**

---

## 2. Why predicting loan approval matters

For the applicant:

* **Less wasted effort.** If a ₹25 lakh loan is clearly too large for a ₹30,000 salary, it is better to learn that in one minute at home than after weeks of paperwork.
* **Knowing what to change.** The answer comes with reasons. For example: "The monthly payment would be about ₹43,726, which is more than your whole monthly income. … Try a smaller loan or a longer repayment time."
* **Less fear.** People who have never dealt with a bank are often nervous about it. A private, free, no-sign-up check takes away some of that.

For a lender (in a real product, which this is not):

* Applications are sorted faster.
* Simple cases are decided consistently.
* Staff time goes to the difficult cases.

For a student project, it is also a complete, realistic example of the full path from raw data to a working website: collecting data, studying it, teaching a computer program from it, checking how good that program is, and putting it in front of real people safely.

---

## 3. What LoanWise AI does: one real example

This is a real check, run on the finished project.

**The person.** A married woman with one child. She has a college degree and works for a salary. She earns ₹48,000 a month and her husband earns ₹22,000 a month. She has always paid past bills on time. She wants to borrow ₹25,00,000 (25 lakh rupees) for a house near a city, and pay it back over 20 years.

**What she does.** She opens the website. She taps answers on three short screens: "About you", "Your money" and "Your loan". She types three numbers: her income, her husband's income, and the loan amount. She presses **See my result**.

**What she sees, about one second later:**

* A green stamp: **LIKELY APPROVED**.
* The headline: "Great news! Your loan is likely to be approved."
* "How sure are we?": **85%, High confidence.** "We are quite sure about this answer."
* "Why we said this":
  * Your credit history is good — this helps a lot.
  * The monthly payment (about ₹22,493) is 32% of your income — manageable, but not small.
  * The loan is about 3.0 years of your income — a sensible size.
  * Having a co-applicant with income makes the loan safer for the bank.
  * Being a graduate helps a little.
* "Your monthly payment would be about ₹22,493 a month."

**What happened behind the screen, in one paragraph.** Her phone sent her 11 answers to the LoanWise computer. That computer checked every answer was sensible. It converted the answers into the exact form the prediction program expects. The prediction program, which learned from 614 past applications, calculated an 85% chance of approval. Then a set of fixed money rules checked whether the monthly payment was affordable. It was, so the answer stayed "approved". The result was saved in a list of past checks and sent back to her phone.

[02 · How it works end to end](02-how-it-works-end-to-end.md) follows this exact example step by step, showing the real text sent at each step.

---

## 4. Who it is for

| Person | What they need from LoanWise AI |
|---|---|
| **An applicant** with no financial or technical background | A quick yes/no estimate, in simple words, with reasons and the likely monthly payment |
| **A student presenting the project** (for example in a viva, which is an oral exam where you defend your work) | A complete, explainable system they can demonstrate and justify |
| **Engineers receiving the code** | Clean, tested, documented code they can run, change and deploy |

The first group decided almost every design choice.

---

## 5. Goals of the project

The original project specification listed eight objectives. Each one, and where it was done:

| # | Objective (from the specification) | What was done | Read more |
|---|---|---|---|
| 1 | Collect and prepare loan data | A public dataset of 614 labelled home-loan applications (`data/raw/loan.csv`); blanks filled in, text turned into numbers, new useful measures calculated | [03](03-dataset.md), [04](04-data-preparation-and-features.md) |
| 2 | Analyse which factors affect approval | Charts and summaries of the data; the finding that past repayment record ("credit history") matters far more than anything else | [03](03-dataset.md) |
| 3 | Train and compare several classification methods | Three methods were taught from the same data and compared fairly: Logistic Regression, Decision Tree and Random Forest | [05](05-algorithms.md), [06](06-training-and-evaluation.md) |
| 4 | Save the best one | The winner (Logistic Regression) is saved to `artifacts/models/loan_model.pkl`, with a report in `model_info.json` | [06](06-training-and-evaluation.md) |
| 5 | Build a web interface | A website with a three-step question form, a result page, a "how it works" page and a history page | [09](09-frontend.md) |
| 6 | Connect it to the model through Flask | A Python program (built with a tool called Flask) receives the answers, runs the model and replies | [08](08-backend.md) |
| 7 | Show the result clearly | Stamp, headline, confidence, reasons and monthly payment, in plain English | [09](09-frontend.md) |
| 8 | Test and deploy | 90 automatic tests; one-command start scripts; a Docker package for servers | [08](08-backend.md) |

A **classification method** (objective 3) is a way of teaching a computer to put things into categories, here "approved" or "rejected". [00](00-ai-from-zero.md) and [05](05-algorithms.md) explain this from the beginning.

Two goals were added during the project, because of the design principle in section 6:

* **Never give a confident wrong answer to nonsense input.** This led to the three-layer checking of answers and the money rules ("guardrails") in [07](07-validation-and-guardrails.md).
* **Never show a technical error to the user.** Every failure becomes a short sentence that says what to do next.

---

## 6. The design principle: "built for the dumbest person alive"

The client's instruction was blunt: the app must work for "the dumbest person alive". In practice this means: **assume the user knows nothing about loans, banks or computers, and may make every possible mistake.** It is not about the user's intelligence. It is about removing everything that requires prior knowledge.

This principle changed concrete things:

| Without the principle | What LoanWise AI does instead |
|---|---|
| A field labelled "Dependents" | The question "How many people depend on your money?", with tap answers "None, 1 person, 2 people, 3 or more", and a "?" button explaining who counts |
| A field labelled "Credit_History: 1 / 0" | "Have you paid back past loans or credit cards on time?" with "Yes, always on time", "No, I was late or missed some" and "I never had a loan or card" |
| A field labelled "Loan_Amount_Term (months)" | "How many years do you want to pay it back over?" with ten buttons from "1 year" to "40 years" |
| A box where you type `2500000` and must count the zeros | The box adds commas as you type (`25,00,000`) and shows "That's ₹25 lakh" underneath |
| Typing letters into a number box | The box does not accept letters at all |
| An error after pressing submit, at the top of the page | A red message under the exact question, the moment it is wrong, saying what to do: "Please tap 'Yes' or 'No'." |
| One error at a time | All problems shown together, with a count: "4 answers need fixing." |
| The computer receives "25 lakh" from another program and crashes | It reads "25 lakh" as ₹25,00,000 and says so: "We read your loan amount "25 lakh" as ₹25,00,000." |
| A ₹1 crore loan on a ₹5,000 salary gets "approved" because the prediction program has never seen such a case | A fixed rule rejects it and explains why, with the actual monthly payment |
| "Probability 0.8521" | "85%, High confidence. We are quite sure about this answer." |
| "Error 500: Internal Server Error" | "Something went wrong on our side. Please try again in a minute." |
| Losing everything you typed when the internet drops | Your answers stay on the page, with a message titled "Your answers are safe" |
| A "rejected" screen in red | A calm indigo stamp "NOT LIKELY YET", a small growing plant and "A 'no' today is not a 'no' forever." |

---

## 7. Disclaimer and ethics

**LoanWise AI is not a bank and does not make lending decisions.** Every page shows: "This is a school project, not a bank. Our answer is a guess made by a computer that learned from 614 old loan applications. A real bank will look at many more things before saying yes or no."

Things a responsible reader should know:

* **Small data.** 614 past applications is a small amount. The measured accuracy (about 80% on fair repeated testing, 85% on one held-back test set) is only a rough indication. Read [06](06-training-and-evaluation.md) for how this was measured.
* **A simple baseline is close.** About 69% of the past applications were approved. So a "program" that always says "approved" would already be right 69% of the time. The model does better, but not by a huge margin.
* **Gender and marital status are used.** The original specification required these questions because the dataset has them. In a real lending product, using them would raise serious fairness and legal concerns: two people with identical finances could get different answers because of their gender. Before any real use, these questions should be removed and the model checked for unfair treatment of groups. In the current model, gender has the smallest influence of all the factors (see the "feature importance" list in [06](06-training-and-evaluation.md)), but "small" is not "none".
* **Old, foreign-origin data.** The dataset is a widely used public practice dataset. Its incomes are small and its exact origin and time period are unclear. It does not represent today's Indian lending market. See [03](03-dataset.md).
* **The monthly payment is an estimate** at a fixed 9% yearly interest rate. Real rates differ.
* **Privacy.** No name, phone number, address or ID number is asked for. Each check's answers and result are saved on the server in a history list so the user can compare checks. Anyone using the same server can see and delete that list. That is acceptable for a demonstration, not for real customers.
* **Explanations are rules, not mind-reading.** The "Why we said this" reasons are written by fixed rules that describe the applicant's situation. They are not a breakdown of how the prediction program reached its number. [07](07-validation-and-guardrails.md#b7-how-the-reasons-list-is-built) explains exactly how they are produced.

---

## 8. Scope: what it does and does not do

**In scope:**

* Home-loan approval estimate for one applicant plus an optional co-applicant.
* The 11 questions that exist in the dataset.
* Plain-English result, reasons, confidence and estimated monthly payment.
* A history of past checks on the same server.
* A page explaining how the program decides, using the real training report.
* Running on a laptop with one command, or on a server.

**Not in scope (non-goals):**

* Real lending decisions, credit-bureau look-ups or connections to any bank.
* User accounts, logins or private per-user history.
* Other loan types (car, personal, business).
* Interest-rate quotes or eligibility amounts.
* Languages other than English.
* Automatic retraining from new applications. The program only learns when someone runs the training step by hand.

---

## 9. For the technically curious: the technology and why each piece was chosen

You can skip this section without losing the story. Each term is defined in the table.

| Part | Technology | What it is | Why it was chosen |
|---|---|---|---|
| Programming language (server and learning) | **Python 3.10+** | A widely used programming language | The standard language for data analysis and machine learning; the required libraries below exist only or best in Python |
| Data handling | **pandas**, **NumPy** | Python libraries for working with tables of data and numbers | Industry standard; reading the CSV file, filling blanks and computing new columns are one-liners |
| Machine learning | **scikit-learn** 1.9.1 | A Python library containing ready-made, well-tested learning methods | Has all three required methods, plus tools for fair comparison (cross-validation) and for packaging the data preparation together with the model (a "pipeline"). Pinned to one exact version because the saved model file only loads in that version |
| Saving the model | **joblib** | Saves a Python object to a file and loads it back | The recommended way to save scikit-learn models |
| Charts during training | **matplotlib** | Python charting library | Produces the data-analysis charts |
| Web server | **Flask 3** | A small Python library for writing programs that answer requests from browsers | The specification named it; it is small enough to understand completely, which matters in a viva |
| Production server | **gunicorn** | A program that runs a Flask app robustly, several copies at once | The standard way to run Flask for real traffic |
| History storage | **SQLite** | A database stored in a single file, built into Python | No separate database software to install; enough for one server |
| Website | **React 19** | A JavaScript library for building interactive pages from reusable pieces | Handles a multi-step form with live checking cleanly; very widely known |
| Page navigation | **React Router** | Lets one web page show different screens for different addresses | Gives real addresses (`/check`, `/result`) that survive a refresh |
| Animation | **framer-motion** | Animation library for React | Makes cause and effect visible (the stamp landing); has built-in support for users who turn animations off |
| Icons | **lucide-react** | A set of simple line icons | Clear, consistent, light |
| Bundling the website | **esbuild** | A tool that packs all the website's source files into a few small files | One small dependency, very fast; see [09](09-frontend.md#b10-build-tooling-esbuild-instead-of-vite) |
| Fonts | **Baloo 2**, **Atkinson Hyperlegible** | Typefaces | Indian-designed display font; body font designed for low-vision readers; see [09](09-frontend.md#a23-typefaces) |
| Code quality | **ruff**, **mypy (strict)** | Tools that read the code and flag mistakes and missing type information | Catch bugs before running; enforce one style |
| Tests | **unittest** (Python's built-in testing tool) | Code that runs the real code and checks the results | No extra dependency; 90 tests |
| Packaging | **Docker** | Packs the app and everything it needs into one image that runs the same on any server | Repeatable deployment |

---

[Next → 02 · How it works end to end](02-how-it-works-end-to-end.md)  
[← Back to index](README.md)
