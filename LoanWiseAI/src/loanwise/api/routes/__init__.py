"""JSON API blueprints, all mounted under ``/api``."""

from __future__ import annotations

from flask import Blueprint

from loanwise.api.routes import history, meta, predict

API_BLUEPRINTS: tuple[Blueprint, ...] = (predict.bp, history.bp, meta.bp)

__all__ = ["API_BLUEPRINTS"]
