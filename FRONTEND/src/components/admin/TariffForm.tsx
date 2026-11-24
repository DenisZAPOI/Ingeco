import { useState } from 'react';

import type { Tariff } from '../../api/settings';
import { useCreateTariff, useTariff } from '../../hooks/useSettings';
import { t } from '../../i18n';
import { formatDateTime, formatPrice } from '../../lib/format';
import { TARIFF_EXAMPLE_KM, eurosField, examplePriceCents, parseEuros } from '../../lib/settings';
import { Form } from '../form/Form';
import { TextField } from '../form/TextField';
import { RequestState } from '../ui/RequestState';

/** The tariff of the next bookings. A change is a new version: booked rides keep their price (§7.4). */
export function TariffForm() {
  const tariff = useTariff();

  return (
    <section>
      <h2>{t('settings.tariffTitle')}</h2>
      <RequestState loading={tariff.loading} error={tariff.error} onRetry={tariff.retry}>
        {tariff.data && <TariffFields current={tariff.data} />}
      </RequestState>
    </section>
  );
}

function TariffFields({ current }: { current: Tariff }) {
  const [active, setActive] = useState(current);
  const [baseFare, setBaseFare] = useState(() => eurosField(current.baseFareCents));
  const [perKm, setPerKm] = useState(() => eurosField(current.perKmCents));
  const [saved, setSaved] = useState(false);
  const save = useCreateTariff();

  const baseFareCents = parseEuros(baseFare);
  const perKmCents = parseEuros(perKm);
  const bothAmountsValid = baseFareCents !== null && perKmCents !== null;
  // Checked here first: a typing slip is shown under its field, without a call.
  const [showFieldErrors, setShowFieldErrors] = useState(false);

  async function submit() {
    setShowFieldErrors(true);
    if (baseFareCents === null || perKmCents === null) return;
    const result = await save.submit({ baseFareCents, perKmCents });
    if (!result) return;
    setActive(result);
    setSaved(true);
    setShowFieldErrors(false);
  }

  function fieldError(cents: number | null, apiField: string): string | undefined {
    if (showFieldErrors && cents === null) return t('settings.notAnAmount');
    return save.errors[apiField];
  }

  return (
    <>
      <p className="panel">
        {t('settings.tariffCurrent', {
          date: formatDateTime(active.createdAt),
          base: formatPrice(active.baseFareCents),
          perKm: formatPrice(active.perKmCents),
        })}
      </p>
      <Form
        onSubmit={submit}
        submitLabel={t('settings.tariffSubmit')}
        submitting={save.submitting}
        error={save.error}
        success={saved ? t('settings.tariffSaved') : null}
      >
        <TextField
          label={t('settings.baseFare')}
          hint={t('settings.amountHint')}
          inputMode="decimal"
          value={baseFare}
          onChange={(value) => {
            setSaved(false);
            setBaseFare(value);
          }}
          error={fieldError(baseFareCents, 'baseFareCents')}
        />
        <TextField
          label={t('settings.perKm')}
          hint={t('settings.amountHint')}
          inputMode="decimal"
          value={perKm}
          onChange={(value) => {
            setSaved(false);
            setPerKm(value);
          }}
          error={fieldError(perKmCents, 'perKmCents')}
        />
        {bothAmountsValid && (
          <p className="note">
            {t('settings.tariffExample', {
              km: TARIFF_EXAMPLE_KM,
              price: formatPrice(examplePriceCents(baseFareCents, perKmCents, TARIFF_EXAMPLE_KM)),
            })}
          </p>
        )}
      </Form>
    </>
  );
}
