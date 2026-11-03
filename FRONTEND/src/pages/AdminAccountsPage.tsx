import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import type { AccountFilters, AccountRole, AccountStatus } from '../api/admin';
import { AccountList } from '../components/admin/AccountCard';
import type { Choice } from '../components/form/ChoiceGroup';
import { SelectField } from '../components/form/SelectField';
import { TextField } from '../components/form/TextField';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { ErrorAlert } from '../components/ui/ErrorAlert';
import { RequestState } from '../components/ui/RequestState';
import { useAccounts } from '../hooks/useAdmin';
import { t } from '../i18n';
import { ROLES, roleLabel } from '../lib/accounts';
import { NEW_ACCOUNT_PATH } from '../lib/paths';

// In the address: the Back button, from an account, returns to the same search.
const SEARCH_PARAM = 'recherche';
const ROLE_PARAM = 'role';
const STATUS_PARAM = 'statut';
const ALL = 'all';

function roleChoices(): Choice<AccountRole | typeof ALL>[] {
  return [{ value: ALL, label: t('admin.allRoles') }, ...ROLES.map((role) => ({ value: role, label: roleLabel(role) }))];
}

function statusChoices(): Choice<AccountStatus | typeof ALL>[] {
  return [
    { value: ALL, label: t('admin.allStatuses') },
    { value: 'active', label: t('admin.activeAccounts') },
    { value: 'suspended', label: t('admin.suspendedAccounts') },
  ];
}

/** UC51: find an account by name or phone, filter by role and status. */
export function AdminAccountsPage() {
  const [params, setParams] = useSearchParams();
  const filters: AccountFilters = {
    search: params.get(SEARCH_PARAM),
    role: (params.get(ROLE_PARAM) as AccountRole | null) ?? null,
    status: (params.get(STATUS_PARAM) as AccountStatus | null) ?? null,
  };
  const [search, setSearch] = useState(filters.search ?? '');

  function apply(changes: Partial<AccountFilters>) {
    const next = { ...filters, ...changes };
    const query: Record<string, string> = {};
    if (next.search) query[SEARCH_PARAM] = next.search;
    if (next.role) query[ROLE_PARAM] = next.role;
    if (next.status) query[STATUS_PARAM] = next.status;
    setParams(query, { replace: true });
  }

  return (
    <section>
      <PageHero title={t('admin.accountsTitle')} />
      <PageSheet>
        <Link to={NEW_ACCOUNT_PATH} className="button button-block">
          {t('admin.createAccount')}
        </Link>
        {/* Searched on "Rechercher", not at every letter: on 2G, one call per word typed. */}
        <form
          className="form"
          role="search"
          onSubmit={(event) => {
            event.preventDefault();
            apply({ search: search.trim() || null });
          }}
        >
          <TextField
            label={t('admin.search')}
            value={search}
            onChange={setSearch}
            type="search"
            hint={t('admin.searchHint')}
          />
          <button type="submit" className="button button-block button-secondary">
            {t('admin.searchSubmit')}
          </button>
          <SelectField
            label={t('admin.role')}
            choices={roleChoices()}
            value={filters.role ?? ALL}
            onChange={(role) => apply({ role: role === ALL ? null : role })}
          />
          <SelectField
            label={t('admin.status')}
            choices={statusChoices()}
            value={filters.status ?? ALL}
            onChange={(status) => apply({ status: status === ALL ? null : status })}
          />
        </form>
        {/* New filters, new list: it starts again from the first page. */}
        <Results key={params.toString()} filters={filters} />
      </PageSheet>
    </section>
  );
}

function Results({ filters }: { filters: AccountFilters }) {
  const list = useAccounts(filters);

  return (
    <RequestState loading={list.loading} error={list.error} onRetry={list.retry}>
      {list.accounts.length === 0 ? <p>{t('admin.noAccount')}</p> : <AccountList accounts={list.accounts} />}
      {list.moreError && <ErrorAlert message={list.moreError} onRetry={list.loadMore} />}
      {list.hasMore && !list.moreError && (
        <button
          type="button"
          className="button button-block button-secondary"
          onClick={list.loadMore}
          disabled={list.loadingMore}
        >
          {list.loadingMore ? t('common.loading') : t('admin.moreAccounts')}
        </button>
      )}
    </RequestState>
  );
}
