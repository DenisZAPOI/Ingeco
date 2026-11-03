import type { Ride } from '../../api/rides';
import { useCancelRide } from '../../hooks/useRides';
import { t } from '../../i18n';
import { formatPrice } from '../../lib/format';
import { ConfirmButton } from '../ui/ConfirmButton';

type CancelRideProps = {
  ride: Ride;
  onCancelled: (ride: Ride) => void;
};

/** "Annuler ce trajet", confirmed on the spot. */
export function CancelRide({ ride, onCancelled }: CancelRideProps) {
  const cancellation = useCancelRide();

  async function cancel() {
    const cancelled = await cancellation.submit(ride.id);
    if (cancelled) onCancelled(cancelled);
  }

  return (
    <ConfirmButton
      label={t('ride.cancel')}
      question={t('ride.cancelQuestion')}
      details={
        ride.paymentStatus === 'paid' && <p>{t('ride.cancelRefund', { amount: formatPrice(ride.riderAmountCents) })}</p>
      }
      confirmLabel={t('ride.cancelConfirm')}
      keepLabel={t('ride.cancelKeep')}
      submitting={cancellation.submitting}
      error={cancellation.error}
      onConfirm={cancel}
    />
  );
}
