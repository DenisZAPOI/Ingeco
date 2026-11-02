import { useCallback, useState } from 'react';

import {
  createAccount,
  fetchAccount,
  fetchAccounts,
  newActivationCode,
  savePhoto,
  updateAccount,
  type Account,
  type AccountChanges,
  type AccountFilters,
  type NewAccount,
} from '../api/admin';
import { errorMessage } from '../lib/errorMessage';
import { useRequest } from './useRequest';
import { useSubmit } from './useSubmit';

/** Accounts matching the filters, page after page. Give the list a `key` made
 *  of the filters: new filters start again from the first page. */
export function useAccounts({ search, role, status }: AccountFilters) {
  const firstPage = useRequest(useCallback(() => fetchAccounts({ search, role, status }, null), [search, role, status]));
  const [morePages, setMorePages] = useState<{ items: Account[]; nextCursor: string | null } | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [moreError, setMoreError] = useState<string | null>(null);

  const accounts = [...(firstPage.data?.items ?? []), ...(morePages?.items ?? [])];
  const nextCursor = morePages ? morePages.nextCursor : (firstPage.data?.nextCursor ?? null);

  const loadMore = useCallback(async () => {
    if (!nextCursor) return;
    setLoadingMore(true);
    setMoreError(null);
    try {
      const page = await fetchAccounts({ search, role, status }, nextCursor);
      setMorePages((previous) => ({ items: [...(previous?.items ?? []), ...page.items], nextCursor: page.nextCursor }));
    } catch (caught) {
      setMoreError(errorMessage(caught));
    } finally {
      setLoadingMore(false);
    }
  }, [nextCursor, search, role, status]);

  return {
    accounts,
    loading: firstPage.loading,
    error: firstPage.error,
    retry: firstPage.retry,
    hasMore: nextCursor !== null,
    loadMore,
    loadingMore,
    moreError,
  };
}

/** `known`: the account handed over by the previous screen, shown without a call. */
export function useAccount(id: number, known: Account | null) {
  return useRequest(useCallback(() => fetchAccount(id), [id]), known);
}

export function useCreateAccount() {
  return useSubmit(useCallback((account: NewAccount) => createAccount(account), []));
}

export function useUpdateAccount(id: number) {
  return useSubmit(useCallback((changes: AccountChanges) => updateAccount(id, changes), [id]));
}

export function useSavePhoto(id: number) {
  return useSubmit(useCallback((imageBase64: string) => savePhoto(id, imageBase64), [id]));
}

export function useNewActivationCode(id: number) {
  return useSubmit(useCallback(() => newActivationCode(id), [id]));
}
