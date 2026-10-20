"""
Rules on account fields: phone number, password, name, e-mail, activation code.

Shared by registration, activation and profile update. Pure functions: they
return the cleaned value, or raise ValueError with a French message that the
user sees next to the field (the DTOs turn it into a 400).
"""

import re

ROLES = ("rider", "driver", "partner", "operator", "admin")
RIDER = "rider"
ACTIVE = "active"
SUSPENDED = "suspended"

# --- Phone number ------------------------------------------------------------
# Users type the number as they know it: "0694 12 34 56". Stored in the
# international format, unique, used as login.
GUYANA_COUNTRY_CODE = "+594"
NATIONAL_NUMBER_LENGTH = 10
INTERNATIONAL_MIN_DIGITS = 8
INTERNATIONAL_MAX_DIGITS = 15  # E.164 limit
_PHONE_SEPARATORS = re.compile(r"[\s.\-()]")
_NATIONAL_NUMBER = re.compile(rf"0[1-9][0-9]{{{NATIONAL_NUMBER_LENGTH - 2}}}")
_INTERNATIONAL_NUMBER = re.compile(rf"\+[1-9][0-9]{{{INTERNATIONAL_MIN_DIGITS - 1},{INTERNATIONAL_MAX_DIGITS - 1}}}")
INVALID_PHONE = "Numéro de téléphone invalide. Exemple : 0694 12 34 56."


def normalize_phone(raw: str) -> str:
    """'0694 12 34 56' → '+594694123456'. A number in +XX… (or 00XX…) is kept."""
    compact = _PHONE_SEPARATORS.sub("", raw)
    if compact.startswith("00"):
        compact = "+" + compact[2:]
    if _INTERNATIONAL_NUMBER.fullmatch(compact):
        return compact
    if _NATIONAL_NUMBER.fullmatch(compact):
        return GUYANA_COUNTRY_CODE + compact[1:]
    raise ValueError(INVALID_PHONE)


# --- Password ----------------------------------------------------------------
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128  # beyond, hashing a huge input would only cost CPU
_DIGIT = re.compile(r"[0-9]")
_SYMBOL = re.compile(r"[^\w\s]|_")


def check_password_strength(password: str) -> str:
    """At least 8 characters, one capital letter, one digit, one symbol."""
    missing = []
    if len(password) < PASSWORD_MIN_LENGTH:
        missing.append(f"au moins {PASSWORD_MIN_LENGTH} caractères")
    if not any(character.isupper() for character in password):
        missing.append("une majuscule")
    if not _DIGIT.search(password):
        missing.append("un chiffre")
    if not _SYMBOL.search(password):
        missing.append("un symbole (par exemple ! ? - *)")
    if missing:
        raise ValueError("Le mot de passe doit contenir " + ", ".join(missing) + ".")
    return password


# --- Name and e-mail ---------------------------------------------------------
NAME_MAX_LENGTH = 100
EMAIL_MAX_LENGTH = 254
_SPACES = re.compile(r"\s+")
# Deliberately loose: the only real check of an address is a message received.
_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def clean_name(raw: str) -> str:
    name = _SPACES.sub(" ", raw).strip()
    if not name:
        raise ValueError("Ce champ est obligatoire.")
    return name


def clean_email(raw: str | None) -> str | None:
    """An empty field means "no e-mail": stored as null, never as ''."""
    if raw is None or not raw.strip():
        return None
    email = raw.strip().lower()
    if not _EMAIL.fullmatch(email):
        raise ValueError("Adresse e-mail invalide. Exemple : prenom.nom@exemple.fr.")
    return email


# --- Activation code ---------------------------------------------------------
# Dictated on the phone or handed over in person: digits only.
ACTIVATION_CODE_LENGTH = 8
_ACTIVATION_CODE = re.compile(rf"[0-9]{{{ACTIVATION_CODE_LENGTH}}}")


def clean_activation_code(raw: str) -> str:
    code = _PHONE_SEPARATORS.sub("", raw)
    if not _ACTIVATION_CODE.fullmatch(code):
        raise ValueError(f"Le code contient {ACTIVATION_CODE_LENGTH} chiffres.")
    return code
