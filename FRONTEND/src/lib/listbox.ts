// Keyboard rules of a drop-down list (ARIA "listbox" pattern), without React:
// tested on their own (listbox.test.ts).

/** How long the letters typed one after the other make a single search. */
export const TYPEAHEAD_RESET_MS = 700;

/** The option highlighted after a navigation key, or null for any other key.
 *  Stops at both ends: no jump from the last option back to the first. */
export function movedIndex(key: string, index: number, count: number): number | null {
  if (count === 0) return null;
  switch (key) {
    case 'ArrowDown':
      return Math.min(count - 1, index + 1);
    case 'ArrowUp':
      return Math.max(0, index - 1);
    case 'Home':
      return 0;
    case 'End':
      return count - 1;
    default:
      return null;
  }
}

/** Without accents or capitals: "re" finds "Rémire-Montjoly". */
function simplified(text: string): string {
  return text.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLocaleLowerCase();
}

/** The option whose label starts with the letters typed, or null. One letter
 *  goes to the next option with that letter (pressing "c" again goes on);
 *  several letters stay on the current option while it still matches. */
export function typeaheadIndex(labels: readonly string[], query: string, index: number): number | null {
  const wanted = simplified(query);
  if (wanted === '' || labels.length === 0) return null;
  const start = wanted.length === 1 ? index + 1 : index;
  for (let step = 0; step < labels.length; step++) {
    const candidate = (start + step + labels.length) % labels.length;
    if (simplified(labels[candidate]).startsWith(wanted)) return candidate;
  }
  return null;
}
