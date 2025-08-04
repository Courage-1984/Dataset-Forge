#!/usr/bin/env python3
"""
Logging utilities for Dataset Forge.
"""

import logging
from dataset_forge.utils.printing import print_error


def log_uncaught_exceptions(ex_cls, ex, tb):
    """Log uncaught exceptions with traceback using the logging module."""
    print_error(f"Uncaught exception: {ex_cls.__name__}: {ex}")
    logging.error("Uncaught exception", exc_info=(ex_cls, ex, tb))
