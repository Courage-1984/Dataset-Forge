import logging


def log_uncaught_exceptions(ex_cls, ex, tb):
    """Log uncaught exceptions with traceback using the logging module."""
    print(f"Uncaught exception: {ex_cls.__name__}: {ex}")
    logging.error("Uncaught exception", exc_info=(ex_cls, ex, tb))
