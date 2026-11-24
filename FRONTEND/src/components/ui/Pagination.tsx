import { t } from '../../i18n';

type PaginationProps = {
  page: number;
  pageCount: number;
  onChange: (page: number) => void;
};

/** « Précédente », « Page 2 sur 4 », « Suivante »: two large buttons and
 *  where we are, in words. Nothing when everything fits on one page. */
export function Pagination({ page, pageCount, onChange }: PaginationProps) {
  if (pageCount <= 1) return null;

  const isFirst = page === 1;
  const isLast = page === pageCount;
  return (
    <nav className="pagination" aria-label={t('pagination.label')}>
      <button type="button" className="button button-secondary" disabled={isFirst} onClick={() => onChange(page - 1)}>
        {t('pagination.previous')}
      </button>
      <p className="pagination-status">{t('pagination.status', { page, total: pageCount })}</p>
      <button type="button" className="button button-secondary" disabled={isLast} onClick={() => onChange(page + 1)}>
        {t('pagination.next')}
      </button>
    </nav>
  );
}
