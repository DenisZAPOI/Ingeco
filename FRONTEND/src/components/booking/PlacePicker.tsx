import { useId, useState, type KeyboardEvent } from 'react';

import type { Commune, Place } from '../../api/places';
import type { Stop } from '../../api/rides';
import { usePlaceSearch } from '../../hooks/usePlaceSearch';
import { t } from '../../i18n';
import { ChoiceGroup } from '../form/ChoiceGroup';

type PlacePickerProps = {
  communes: Commune[];
  value: Stop | null;
  onChange: (stop: Stop | null) => void;
  /** Shown under the list: no address chosen yet. */
  error?: string;
};

/** Commune, then a search, then a choice in the results. */
export function PlacePicker({ communes, value, onChange, error }: PlacePickerProps) {
  const [communeId, setCommuneId] = useState<number | null>(value?.communeId ?? null);
  const [text, setText] = useState('');
  const { places, searching, error: searchError, search, clear } = usePlaceSearch();
  const inputId = useId();
  const searchErrorId = `${inputId}-error`;

  function chooseCommune(id: string) {
    setCommuneId(Number(id));
    clear();
    onChange(null);
  }

  function runSearch() {
    if (communeId !== null && !searching) search(text, communeId);
  }

  // Enter in the field searches: it must not send the whole step.
  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter') {
      event.preventDefault();
      runSearch();
    }
  }

  // The address chosen earlier stays listed, so coming back to the step shows it.
  const listed: Place[] =
    places ?? (value ? [{ label: value.address, lat: value.lat, lng: value.lng, communeId: value.communeId, token: value.token }] : []);

  return (
    <>
      <ChoiceGroup
        legend={t('booking.commune')}
        choices={communes.map((commune) => ({ value: String(commune.id), label: commune.name }))}
        value={communeId === null ? null : String(communeId)}
        onChange={chooseCommune}
      />

      {communeId !== null && (
        <div className="field">
          <label htmlFor={inputId} className="field-label">
            {t('booking.searchLabel')}
          </label>
          <div className="input-with-button">
            <input
              id={inputId}
              className="field-input"
              value={text}
              onChange={(event) => setText(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t('booking.searchPlaceholder')}
              autoComplete="street-address"
              enterKeyHint="search"
              aria-invalid={searchError ? true : undefined}
              aria-describedby={searchError ? searchErrorId : undefined}
            />
            <button type="button" className="button button-secondary" onClick={runSearch} disabled={searching}>
              {searching ? t('booking.searching') : t('booking.search')}
            </button>
          </div>
          {searchError && (
            <p id={searchErrorId} role="alert" className="field-error">
              {searchError}
            </p>
          )}
        </div>
      )}

      {places?.length === 0 && (
        <p role="status" className="note">
          {t('booking.noAddress')}
        </p>
      )}

      {listed.length > 0 && (
        <ChoiceGroup
          legend={t('booking.pickAddress')}
          choices={listed.map((place, index) => ({ value: String(index), label: place.label }))}
          value={value ? String(listed.findIndex((place) => place.label === value.address)) : null}
          onChange={(index) => {
            const place = listed[Number(index)];
            // The token goes back with the stop: the API only books the places it proposed.
            onChange({ address: place.label, lat: place.lat, lng: place.lng, communeId: place.communeId, token: place.token });
          }}
          error={error}
        />
      )}
      {listed.length === 0 && error && <p className="field-error">{error}</p>}
    </>
  );
}
