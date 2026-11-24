import { useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { PAGE_PARAM, pageFromParams, paginate, type Page } from '../lib/pagination';

/** Ten items a page: about two screens of a phone. */
export const ITEMS_PER_PAGE = 10;

export type ListPage<T> = Page<T> & {
  goTo: (page: number) => void;
  /** Ref of the element just above the list (its count, its title), which
   *  needs tabIndex={-1}: a new page brings the screen and the focus back to it. */
  listStart: (element: HTMLElement | null) => void;
};

function backToListStart(start: HTMLElement | null) {
  if (!start) return;
  // The focus too: a screen reader starts reading the new page from the top.
  start.focus({ preventScroll: true });
  start.scrollIntoView({ block: 'start' });
}

/** Pages of a public list (offers, services, guides): the page lives in the
 *  address (?page=2), so the Back button from an item comes back to it. The
 *  other parameters of the address (filters) are kept. */
export function useAddressPage<T>(items: readonly T[], perPage = ITEMS_PER_PAGE): ListPage<T> {
  const [params, setParams] = useSearchParams();
  const start = useRef<HTMLElement | null>(null);
  const current = paginate(items, pageFromParams(params), perPage);

  function goTo(page: number) {
    const next = new URLSearchParams(params);
    if (page > 1) {
      next.set(PAGE_PARAM, String(page));
    } else {
      next.delete(PAGE_PARAM);
    }
    // replace: the Back button leaves the list, it does not go back page by page.
    setParams(next, { replace: true });
    backToListStart(start.current);
  }

  function listStart(element: HTMLElement | null) {
    start.current = element;
  }

  return { ...current, goTo, listStart };
}

/** Pages of a list of work (requests to handle): kept on the screen only,
 *  several lists can share a page. */
export function useLocalPage<T>(items: readonly T[], perPage = ITEMS_PER_PAGE): ListPage<T> {
  const [page, setPage] = useState(1);
  const start = useRef<HTMLElement | null>(null);
  const current = paginate(items, page, perPage);

  function goTo(nextPage: number) {
    setPage(nextPage);
    backToListStart(start.current);
  }

  function listStart(element: HTMLElement | null) {
    start.current = element;
  }

  return { ...current, goTo, listStart };
}
