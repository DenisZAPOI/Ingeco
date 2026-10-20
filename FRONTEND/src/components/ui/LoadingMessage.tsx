import { useSlowNetwork } from '../../hooks/useSlowNetwork';

/** "Chargement…", then reassurance when the network is slow. */
export function LoadingMessage() {
  const slow = useSlowNetwork(true);
  return <p role="status">{slow ? 'Le réseau est lent. Merci de patienter, le chargement continue…' : 'Chargement…'}</p>;
}
