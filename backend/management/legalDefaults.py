from pathlib import Path

LEGAL_DEFAULTS_DIR = Path(__file__).resolve().parent / "legal_defaults"


def _read_default(filename):
    return (LEGAL_DEFAULTS_DIR / filename).read_text(encoding="utf-8")


def termsService():
    return _read_default("terms_service.md")


def privacyPolicy():
    return _read_default("privacy_policy.md")
