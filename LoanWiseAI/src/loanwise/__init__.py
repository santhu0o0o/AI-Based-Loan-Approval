"""LoanWise AI: plain-English loan-approval estimates backed by a scikit-learn model.

Package layout (each layer only depends on the layers below it)::

    loanwise.api        Flask application factory, blueprints, HTTP error handling
    loanwise.services   orchestration: model registry, prediction and sample services
    loanwise.storage    persistence (SQLite prediction history)
    loanwise.domain     pure business rules: schema, validation, sanitising, guardrails
    loanwise.ml         training pipeline and the custom transforms pickled inside it
    loanwise.config     environment-driven settings shared by every layer

This module is intentionally import-light: the trained pipeline is unpickled via
``loanwise.ml.features``, so importing ``loanwise`` must never pull in Flask.
"""

__version__ = "1.0.0"

__all__ = ["__version__"]
