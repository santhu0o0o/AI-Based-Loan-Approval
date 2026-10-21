"""Model training and the custom transforms that live inside the saved pipeline.

Only :mod:`loanwise.ml.features` is needed at serving time (to unpickle the
model); the other modules are used by the training entry point
:func:`loanwise.ml.train.main`.
"""
