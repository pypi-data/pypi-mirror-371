import os
import bcrypt
import re
import string

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 64
_bcrypt_rounds_env = os.getenv("BCRYPT_ROUNDS")
BCRYPT_ROUNDS = int(_bcrypt_rounds_env) if _bcrypt_rounds_env else 12


def validate_password_complexity(password: str) -> None:
    """Проверяет наличие цифр, верхнего/нижнего регистра и спецсимволов."""
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain a digit")
    if not any(ch in string.punctuation for ch in password):
        raise ValueError("Password must contain a special character")


def validate_password_length(password: str) -> None:
    """Проверяет, что длина пароля находится в допустимых пределах."""
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError("Password too short")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password exceeds maximum length")


def hash_password(password: str) -> str:
    """Хэширует пароль, используя bcrypt."""
    validate_password_length(password)
    validate_password_complexity(password)
    rounds = BCRYPT_ROUNDS
    return bcrypt.hashpw(
        password.encode(), bcrypt.gensalt(rounds=rounds)
    ).decode()


def verify_password(password: str, stored_hash: str) -> bool:
    """Проверяет пароль по сохранённому bcrypt-хэшу."""

    try:
        validate_password_length(password)
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    except ValueError:
        # ``bcrypt.checkpw`` raises ``ValueError`` when ``stored_hash`` is not a
        # valid bcrypt hash. Historically this bubbled up to callers, but for a
        # verification helper it's more convenient to treat such cases as a
        # failed password check.  We also treat length violations the same way
        # by reusing the existing ``ValueError`` from ``validate_password_length``.
        return False

