import { describe, expect, it } from 'vitest';

import { pageFromParams, pageToParams, paginate } from './pagination';

const ITEMS = Array.from({ length: 23 }, (_, index) => index + 1);
const PAGE_SIZE = 10;

describe('paginate', () => {
  it('cuts the list in pages of the given size', () => {
    const second = paginate(ITEMS, 2, PAGE_SIZE);
    expect(second.items).toEqual([11, 12, 13, 14, 15, 16, 17, 18, 19, 20]);
    expect(second.pageCount).toBe(3);
  });

  it('shows the rest on the last page', () => {
    expect(paginate(ITEMS, 3, PAGE_SIZE).items).toEqual([21, 22, 23]);
  });

  it('brings a page past the end back to the last one (after a filter)', () => {
    const page = paginate(ITEMS, 9, PAGE_SIZE);
    expect(page.page).toBe(3);
    expect(page.items).toEqual([21, 22, 23]);
  });

  it('brings a page before the start back to the first one', () => {
    expect(paginate(ITEMS, 0, PAGE_SIZE).page).toBe(1);
  });

  it('gives one empty page for an empty list', () => {
    expect(paginate([], 1, PAGE_SIZE)).toEqual({ items: [], page: 1, pageCount: 1 });
  });
});

describe('pageFromParams', () => {
  it('reads the page of the address', () => {
    expect(pageFromParams(new URLSearchParams('page=2'))).toBe(2);
  });

  it('falls back to the first page when it is missing or wrong', () => {
    expect(pageFromParams(new URLSearchParams(''))).toBe(1);
    expect(pageFromParams(new URLSearchParams('page=abc'))).toBe(1);
    expect(pageFromParams(new URLSearchParams('page=-3'))).toBe(1);
    expect(pageFromParams(new URLSearchParams('page=1.5'))).toBe(1);
  });
});

describe('pageToParams', () => {
  it('leaves the first page out of the address', () => {
    expect(pageToParams(1)).toEqual({});
    expect(pageToParams(3)).toEqual({ page: '3' });
  });
});
