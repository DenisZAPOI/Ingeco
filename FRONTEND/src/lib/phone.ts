const GUYANA_PREFIX = '+594';
const NATIONAL_PAIRS = /(\d{2})(?=\d)/g;

/** '+594694123456' → '0694 12 34 56', as people know their number. Other countries stay as stored. */
export function formatPhone(phone: string): string {
  if (!phone.startsWith(GUYANA_PREFIX)) {
    return phone;
  }
  const national = `0${phone.slice(GUYANA_PREFIX.length)}`;
  return `${national.slice(0, 4)} ${national.slice(4).replace(NATIONAL_PAIRS, '$1 ')}`;
}
