// Same rules as the back-end (services/account_rules.py), checked while the
// user types so they see at once what is missing. The back-end checks again:
// this list only helps, it protects nothing.

export const PASSWORD_MIN_LENGTH = 8;

export type PasswordRule = { label: string; isMet: (password: string) => boolean };

export const PASSWORD_RULES: PasswordRule[] = [
  { label: `Au moins ${PASSWORD_MIN_LENGTH} caractères`, isMet: (password) => password.length >= PASSWORD_MIN_LENGTH },
  { label: 'Une majuscule', isMet: (password) => password !== password.toLowerCase() },
  { label: 'Un chiffre', isMet: (password) => /[0-9]/.test(password) },
  { label: 'Un symbole (par exemple ! ? - *)', isMet: (password) => /[^\p{L}\p{N}\s]|_/u.test(password) },
];

export function isStrongPassword(password: string): boolean {
  return PASSWORD_RULES.every((rule) => rule.isMet(password));
}
