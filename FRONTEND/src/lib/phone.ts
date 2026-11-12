const GUYANA_PREFIX = '+594';
// Mainland France: the fictitious numbers of the help directory (ARCEP range 05 36 49).
const FRANCE_PREFIX = '+33';
const NATIONAL_PAIRS = /(\d{2})(?=\d)/g;

/** '+594694123456' → '0694 12 34 56', '+33536490001' → '05 36 49 00 01',
 *  as people know their number. Other countries stay as stored. */
export function formatPhone(phone: string): string {
  if (phone.startsWith(GUYANA_PREFIX)) {
    const national = `0${phone.slice(GUYANA_PREFIX.length)}`;
    return `${national.slice(0, 4)} ${national.slice(4).replace(NATIONAL_PAIRS, '$1 ')}`;
  }
  if (phone.startsWith(FRANCE_PREFIX)) {
    return `0${phone.slice(FRANCE_PREFIX.length)}`.replace(NATIONAL_PAIRS, '$1 ');
  }
  return phone;
}
