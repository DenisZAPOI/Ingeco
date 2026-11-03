/** Every text of `texts` between brackets, its {placeholders} kept: on screen,
 *  a text without brackets is one still written in the code. Development only. */
export function pseudoLanguage<T>(texts: T): T {
  if (typeof texts === 'string') {
    return `[${texts}]` as T;
  }
  if (typeof texts === 'object' && texts !== null) {
    return Object.fromEntries(Object.entries(texts).map(([key, value]) => [key, pseudoLanguage(value)])) as T;
  }
  return texts;
}
