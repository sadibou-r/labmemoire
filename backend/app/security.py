"""Hachage de mot de passe (PBKDF2, stdlib uniquement) + génération de jetons."""
import hashlib
import hmac
import secrets

_ALGO = "sha256"
_ITERATIONS = 120_000


def hash_password(password: str) -> str:
    """Retourne 'salt$hash' encodés en hexadécimal."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(_ALGO, password.encode(), bytes.fromhex(salt), _ITERATIONS)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac(_ALGO, password.encode(), bytes.fromhex(salt), _ITERATIONS)
    return hmac.compare_digest(dk.hex(), expected)


def generate_token() -> str:
    return secrets.token_hex(32)
