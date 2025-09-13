from __future__ import annotations

import logging
import re


REDACT_RE = re.compile(r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,})")


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = REDACT_RE.sub("***", record.msg)
        return True


def get_logger(name: str = "genticode") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.addFilter(RedactingFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

