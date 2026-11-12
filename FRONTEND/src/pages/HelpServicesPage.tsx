import { Link, useSearchParams } from 'react-router-dom';

import type { HelpCategory } from '../api/helpServices';
import { SelectField } from '../components/form/SelectField';
import { CategoryIcon } from '../components/help/CategoryIcon';
import { HelpServiceList } from '../components/help/HelpServiceCard';
import { RightsSimulators } from '../components/help/RightsSimulators';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { useHelpServices } from '../hooks/useHelpServices';
import { t, tn } from '../i18n';
import {
  HELP_CATEGORIES,
  categoryLabel,
  filterHelpServices,
  filtersFromParams,
  filtersToParams,
  serviceCommunes,
  type HelpFilters,
} from '../lib/helpServices';
import { HELP_PATH, HELP_SERVICES_PATH } from '../lib/paths';

const ALL = 'all';

/** Directory of help services (module M5), public. First the needs, as large
 *  tiles (no call needed: shown at once, even on 2G); a need chosen, its
 *  services, to narrow down by commune. One call for the whole list. */
export function HelpServicesPage() {
  const [params, setParams] = useSearchParams();
  const filters = filtersFromParams(params);

  return filters.category === null ? (
    <NeedChoice />
  ) : (
    <ServicesOfNeed
      category={filters.category}
      filters={filters}
      // replace: the Back button goes back to the needs, it does not undo each commune.
      onChange={(next) => setParams(filtersToParams(next), { replace: true })}
    />
  );
}

function NeedChoice() {
  return (
    <section>
      <PageHero title={t('helpServices.title')}>
        <p className="hero-lead">{t('helpServices.lead')}</p>
      </PageHero>
      <PageSheet>
        <nav aria-label={t('helpServices.needsLabel')}>
          <ul className="category-grid">
            {HELP_CATEGORIES.map((category) => (
              <li key={category}>
                {/* A link, not a state: the address says the need, and Back returns here. */}
                <Link to={`${HELP_SERVICES_PATH}?${new URLSearchParams(filtersToParams({ category, communeId: null }))}`} className="category-tile">
                  <span className="icon-chip">
                    <CategoryIcon category={category} />
                  </span>
                  <span className="category-tile-title">{categoryLabel(category)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <p className="note">{t('helpServices.fictional')}</p>
        <Link to={HELP_PATH} className="link-action">
          {t('helpServices.backToHelp')}
        </Link>
      </PageSheet>
    </section>
  );
}

type ServicesOfNeedProps = {
  category: HelpCategory;
  filters: HelpFilters;
  onChange: (filters: HelpFilters) => void;
};

function ServicesOfNeed({ category, filters, onChange }: ServicesOfNeedProps) {
  const services = useHelpServices();
  const ofNeed = filterHelpServices(services.data ?? [], { category, communeId: null });
  const shown = filterHelpServices(ofNeed, filters);
  const communeChoices = [
    { value: ALL, label: t('helpServices.allCommunes') },
    ...serviceCommunes(ofNeed).map((commune) => ({ value: String(commune.id), label: commune.name })),
  ];

  return (
    <section>
      <PageHero title={categoryLabel(category)} eyebrow={t('helpServices.title')}>
        <p className="hero-lead">{t(`helpServices.categories.${category}.hint`)}</p>
      </PageHero>
      <PageSheet>
        <RequestState loading={services.loading && !services.data} error={services.error} onRetry={services.retry}>
          {ofNeed.length > 1 && (
            <SelectField
              label={t('helpServices.commune')}
              choices={communeChoices}
              value={filters.communeId === null ? ALL : String(filters.communeId)}
              onChange={(chosen) => onChange({ category, communeId: chosen === ALL ? null : Number(chosen) })}
            />
          )}
          <p aria-live="polite" className="note">
            {tn('helpServices.count', shown.length)}
          </p>
          {shown.length > 0 ? (
            <HelpServiceList services={shown} />
          ) : (
            <>
              <p>{t('helpServices.noMatch')}</p>
              <button type="button" className="button button-block button-secondary" onClick={() => onChange({ category, communeId: null })}>
                {t('helpServices.allCommunesButton')}
              </button>
            </>
          )}
          <p className="note">{t('helpServices.fictional')}</p>
        </RequestState>
        {/* Outside the loading state: useful even when the services cannot load. */}
        {category === 'rights' && <RightsSimulators />}
        <Link to={HELP_SERVICES_PATH} className="link-action">
          {t('helpServices.otherNeed')}
        </Link>
      </PageSheet>
    </section>
  );
}
