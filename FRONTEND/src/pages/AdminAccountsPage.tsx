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
import { ROLE_LABELS } from '../lib/accounts';
import { NEW_ACCOUNT_PATH } from '../lib/paths';

// In the address: the Back button, from an account, returns to the same search.
const SEARCH_PARAM = 'recherche';
const ROLE_PARAM = 'role';
const STATUS_PARAM = 'statut';
const ALL = 'all';

const ROLE_CHOICES: Choice<AccountRole | typeof ALL>[] = [
  { value: ALL, label: 'Tous les rôles' },
  ...(Object.entries(ROLE_LABELS) as [AccountRole, string][]).map(([value, label]) => ({ value, label })),
];
const STATUS_CHOICES: Choice<AccountStatus | typeof ALL>[] = [
  { value: ALL, label: 'Actifs et suspendus' },
  { value: 'active', label: 'Actifs' },
  { value: 'suspended', label: 'Suspendus' },
];

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
      <PageHero title="Comptes" />
      <PageSheet>
        <Link to={NEW_ACCOUNT_PATH} className="button button-block">
          Créer un compte
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
            label="Nom ou numéro de téléphone"
            value={search}
            onChange={setSearch}
            type="search"
            hint="Exemple : Chloé, ou 0694 12"
          />
          <button type="submit" className="button button-block button-secondary">
            Rechercher
          </button>
          <SelectField
            label="Rôle"
            choices={ROLE_CHOICES}
            value={filters.role ?? ALL}
            onChange={(role) => apply({ role: role === ALL ? null : role })}
          />
          <SelectField
            label="Statut"
            choices={STATUS_CHOICES}
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
      {list.accounts.length === 0 ? <p>Aucun compte ne correspond.</p> : <AccountList accounts={list.accounts} />}
      {list.moreError && <ErrorAlert message={list.moreError} onRetry={list.loadMore} />}
      {list.hasMore && !list.moreError && (
        <button
          type="button"
          className="button button-block button-secondary"
          onClick={list.loadMore}
          disabled={list.loadingMore}
        >
          {list.loadingMore ? 'Chargement…' : 'Voir plus de comptes'}
        </button>
      )}
    </RequestState>
  );
}
