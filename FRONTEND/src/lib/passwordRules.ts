import { t } from '../i18n';

// Same rules as the back-end (services/account_rules.py), checked while the
// user types so they see at once what is missing. The back-end checks again:
// this list only helps, it protects nothing.

export const PASSWORD_MIN_LENGTH = 8;

export type PasswordRule = { label: string; isMet: (password: string) => boolean };

/** A function, not a constant: the labels follow the language. */
export function passwordRules(): PasswordRule[] {
  return [
    {
      label: t('password.ruleLength', { min: PASSWORD_MIN_LENGTH }),
      isMet: (password) => password.length >= PASSWORD_MIN_LENGTH,
    },
    { label: t('password.ruleCapital'), isMet: (password) => password !== password.toLowerCase() },
    { label: t('password.ruleDigit'), isMet: (password) => /[0-9]/.test(password) },
    { label: t('password.ruleSymbol'), isMet: (password) => /[^\p{L}\p{N}\s]|_/u.test(password) },
  ];
}

export function isStrongPassword(password: string): boolean {
  return passwordRules().every((rule) => rule.isMet(password));
}
