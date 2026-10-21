"""Pure business logic for loan applications: no Flask, no I/O, no model loading.

Three-layer input defence (layer 1 is the browser form):

* :mod:`~loanwise.domain.validation` (layer 2) parses and validates raw answers.
* :mod:`~loanwise.domain.sanitizer` (layer 3) maps them onto the model's columns.
* :mod:`~loanwise.domain.guardrails` applies lending rules on top of the model.
"""
