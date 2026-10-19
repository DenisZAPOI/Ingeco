"""Rules on account fields: pure functions, no server."""

import pytest

from app.services.account_rules import (
    check_password_strength,
    clean_activation_code,
    clean_email,
    clean_name,
    normalize_phone,
)
from app.utils.rate_limit import AttemptLimiter


@pytest.mark.parametrize(
    ("typed", "stored"),
    [
        ("0694 12 34 56", "+594694123456"),
        ("0694.12.34.56", "+594694123456"),
        ("0594-30-00-00", "+594594300000"),
        ("+594 694 12 34 56", "+594694123456"),
        ("0033 6 12 34 56 78", "+33612345678"),
    ],
)
def test_a_phone_number_is_stored_in_international_format(typed, stored):
    assert normalize_phone(typed) == stored


@pytest.mark.parametrize("typed", ["", "0694", "694123456", "06941234567", "+594", "0694 12 34 5a", "+0694123456"])
def test_a_malformed_phone_number_is_refused(typed):
    with pytest.raises(ValueError):
        normalize_phone(typed)


def test_a_strong_password_is_accepted():
    assert check_password_strength("Trajet-2026!") == "Trajet-2026!"


@pytest.mark.parametrize(
    ("password", "missing"),
    [
        ("Ab1!", "au moins 8 caractères"),
        ("trajet-2026", "une majuscule"),
        ("Trajet-deux", "un chiffre"),
        ("Trajet2026", "un symbole"),
    ],
)
def test_a_weak_password_is_refused_saying_what_is_missing(password, missing):
    with pytest.raises(ValueError, match=missing):
        check_password_strength(password)


def test_names_are_trimmed_and_cannot_be_blank():
    assert clean_name("  Jean   Pierre ") == "Jean Pierre"
    with pytest.raises(ValueError):
        clean_name("   ")


def test_an_empty_email_means_no_email():
    assert clean_email("") is None
    assert clean_email(None) is None
    assert clean_email(" Prenom.Nom@Exemple.fr ") == "prenom.nom@exemple.fr"
    with pytest.raises(ValueError):
        clean_email("prenom.nom")


def test_an_activation_code_is_eight_digits_spaces_allowed():
    assert clean_activation_code("1234 5678") == "12345678"
    with pytest.raises(ValueError):
        clean_activation_code("1234567")


def test_the_limiter_blocks_after_the_maximum_then_forgets_old_failures():
    now = [0.0]
    limiter = AttemptLimiter(max_failures=2, window_seconds=60, clock=lambda: now[0])

    limiter.record_failure("key")
    assert not limiter.is_blocked("key")
    limiter.record_failure("key")
    assert limiter.is_blocked("key")
    assert not limiter.is_blocked("other key")

    now[0] = 61
    assert not limiter.is_blocked("key")
