import { useEffect, useRef, useState } from 'react';

import type { Ride } from '../../api/rides';
import { useCancelRide } from '../../hooks/useRides';
import { useSlowNetwork } from '../../hooks/useSlowNetwork';
import { formatPrice } from '../../lib/format';

type CancelRideProps = {
  ride: Ride;
  onCancelled: (ride: Ride) => void;
};

/** "Annuler ce trajet", confirmed on the spot: no pop-up window to find or close. */
export function CancelRide({ ride, onCancelled }: CancelRideProps) {
  const [confirming, setConfirming] = useState(false);
  const cancellation = useCancelRide();
  const slow = useSlowNetwork(cancellation.submitting);
  const questionRef = useRef<HTMLParagraphElement>(null);

  // A screen reader reads the question as soon as it appears.
  useEffect(() => {
    if (confirming) questionRef.current?.focus();
  }, [confirming]);

  async function cancel() {
    const cancelled = await cancellation.submit(ride.id);
    if (cancelled) onCancelled(cancelled);
  }

  if (!confirming) {
    return (
      <button type="button" className="button button-block button-secondary" onClick={() => setConfirming(true)}>
        Annuler ce trajet
      </button>
    );
  }

  return (
    <div className="panel confirm">
      <p ref={questionRef} tabIndex={-1} className="confirm-question">
        Voulez-vous vraiment annuler ce trajet ?
      </p>
      {ride.paymentStatus === 'paid' && <p>Vous serez remboursé de {formatPrice(ride.riderAmountCents)}.</p>}
      {cancellation.error && (
        <p role="alert" className="alert alert-error">
          {cancellation.error}
        </p>
      )}
      {slow && (
        <p role="status" className="note">
          Le réseau est lent. Ne fermez pas l'application, l'envoi continue.
        </p>
      )}
      <div className="stack">
        <button type="button" className="button button-block" onClick={cancel} disabled={cancellation.submitting}>
          {cancellation.submitting ? 'Envoi en cours…' : 'Oui, annuler'}
        </button>
        <button
          type="button"
          className="button button-block button-secondary"
          onClick={() => setConfirming(false)}
          disabled={cancellation.submitting}
        >
          Non, garder le trajet
        </button>
      </div>
    </div>
  );
}
