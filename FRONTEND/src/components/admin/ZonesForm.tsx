import { useState } from 'react';

import type { Zone } from '../../api/settings';
import { useSaveZones, useZones } from '../../hooks/useSettings';
import { t } from '../../i18n';
import { CheckboxField } from '../form/CheckboxField';
import { Form } from '../form/Form';
import { RequestState } from '../ui/RequestState';

/** The communes that receive rides (zones, §5 M9). */
export function ZonesForm() {
  const zones = useZones();

  return (
    <section>
      <h2>{t('settings.zonesTitle')}</h2>
      <p className="note">{t('settings.zonesNote')}</p>
      <RequestState loading={zones.loading} error={zones.error} onRetry={zones.retry}>
        {zones.data && <ZoneFields zones={zones.data.items} />}
      </RequestState>
    </section>
  );
}

/** Served communes first, then the others, each group by name. Sorted once,
 *  when loaded: a commune does not jump away when its box is ticked. */
function servedFirst(zones: Zone[]): Zone[] {
  const served = zones.filter((zone) => zone.isServed);
  const others = zones.filter((zone) => !zone.isServed);
  return [...served, ...others];
}

function ZoneFields({ zones }: { zones: Zone[] }) {
  const [order] = useState(() => servedFirst(zones));
  const [servedIds, setServedIds] = useState(() => new Set(zones.filter((zone) => zone.isServed).map((zone) => zone.id)));
  const [saved, setSaved] = useState(false);
  const save = useSaveZones();

  function toggle(id: number, isServed: boolean) {
    setSaved(false);
    setServedIds((previous) => {
      const next = new Set(previous);
      if (isServed) {
        next.add(id);
      } else {
        next.delete(id);
      }
      return next;
    });
  }

  async function submit() {
    const result = await save.submit([...servedIds]);
    if (!result) return;
    setServedIds(new Set(result.items.filter((zone) => zone.isServed).map((zone) => zone.id)));
    setSaved(true);
  }

  return (
    <Form
      onSubmit={submit}
      submitLabel={t('settings.zonesSubmit')}
      submitting={save.submitting}
      error={save.error}
      success={saved ? t('settings.zonesSaved') : null}
    >
      <fieldset className="field">
        <legend className="field-label">{t('settings.servedLegend')}</legend>
        {order.map((zone) => (
          <CheckboxField
            key={zone.id}
            label={zone.name}
            checked={servedIds.has(zone.id)}
            onChange={(isServed) => toggle(zone.id, isServed)}
          />
        ))}
      </fieldset>
    </Form>
  );
}
