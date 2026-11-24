// Pages of a list already loaded on the phone (job offers): cutting it in
// pages costs no call, so it stays instant on a slow network. The page lives
// in the address (?page=2), so the Back button from an item comes back to it.

/** Name of the address parameter, in French: users see it. */
const PAGE_PARAM = 'page';
const FIRST_PAGE = 1;

export type Page<T> = {
  items: T[];
  /** The page shown, from 1, brought back within the pages that exist. */
  page: number;
  pageCount: number;
};

/** The items of one page. A page past the end (fewer items after a filter)
 *  shows the last one; an empty list has one empty page. */
export function paginate<T>(items: readonly T[], page: number, pageSize: number): Page<T> {
  const pageCount = Math.max(FIRST_PAGE, Math.ceil(items.length / pageSize));
  const shownPage = Math.min(Math.max(page, FIRST_PAGE), pageCount);
  const start = (shownPage - 1) * pageSize;
  return { items: items.slice(start, start + pageSize), page: shownPage, pageCount };
}

/** The page asked in the address: 1 when it is missing or not a whole number. */
export function pageFromParams(params: URLSearchParams): number {
  const page = Number(params.get(PAGE_PARAM));
  const isValid = Number.isInteger(page) && page >= FIRST_PAGE;
  return isValid ? page : FIRST_PAGE;
}

/** The address parameter of a page: none for the first one. */
export function pageToParams(page: number): Record<string, string> {
  if (page <= FIRST_PAGE) return {};
  return { [PAGE_PARAM]: String(page) };
}
