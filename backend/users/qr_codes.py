import base64
import binascii
import os
from urllib.parse import urlencode

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _get_aes_key() -> bytes:
    try:
        key = base64.urlsafe_b64decode(settings.AES_KEY.encode("ascii"))
    except (AttributeError, UnicodeEncodeError, binascii.Error) as exc:
        raise ImproperlyConfigured(
        ) from exc

    if len(key) != 32:
        raise ImproperlyConfigured("AES_KEY must decode to a 32-byte AES-256 key.")

    return key


def encrypt_join_code(join_code: str) -> str:
    nonce = os.urandom(12)
    ciphertext = AESGCM(_get_aes_key()).encrypt(nonce, join_code.encode("utf-8"), None)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")


def build_registration_url(frontend_url: str, join_code: str) -> str:
    encrypted_code = encrypt_join_code(join_code)
    return (
        f"{frontend_url.rstrip('/')}/private/authentication/register?"
        f"{urlencode({'rel': encrypted_code})}"
    )
