import { useSlowNetwork } from '../../hooks/useSlowNetwork';
import { t } from '../../i18n';

/** "Chargement…", then reassurance when the network is slow. */
export function LoadingMessage() {
  const slow = useSlowNetwork(true);
  return <p role="status">{slow ? t('common.loadingSlow') : t('common.loading')}</p>;
}
