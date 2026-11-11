// Directory of help services: the need and the commune filter on the phone,
// "Comment y aller ?" starts a trip there, and the phone numbers are fictitious.

import { afterEach, describe, expect, it, vi } from 'vitest';

import type { HelpService } from '../api/helpServices';
import { setLanguage } from '../i18n';
import { bookingSteps, draftForHelpService, NO_GIVEN_DROPOFF, readBookingDraft, saveBookingDraft, skipsDropoff } from './bookingDraft';
import {
  filterHelpServices,
  filtersFromParams,
  filtersToParams,
  formatUpdatedOn,
  purposeFor,
  readStoredHelpServices,
  serviceCommunes,
  serviceFromState,
  speaksAppLanguage,
  storeHelpServices,
} from './helpServices';
import { formatPhone } from './phone';

function service(changes: Partial<HelpService>): HelpService {
  return {
    id: 1,
    name: 'Point info logement (fictif)',
    category: 'housing',
    description: '',
    hours: 'Du lundi au vendredi, 8 h – 12 h',
    place: { address: 'Mairie de Matoury', lat: 4.847, lng: -52.329, communeId: 3, token: 'signed' },
    communeName: 'Matoury',
    phone: '+33536490001',
    wheelchairAccessible: true,
    spokenLanguages: ['fr', 'gcr'],
    updatedOn: '2026-11-02',
    language: 'fr',
    ...changes,
  };
}

const MATOURY_HOUSING = service({ id: 1 });
const CAYENNE_HOUSING = service({
  id: 2,
  place: { address: 'Place Léopold Héder, Cayenne', lat: 4.9395, lng: -52.3355, communeId: 1, token: 'signed' },
  communeName: 'Cayenne',
  spokenLanguages: ['fr', 'pt-BR'],
});
const CAYENNE_HEALTH = service({ id: 3, category: 'health', communeName: 'Cayenne', place: CAYENNE_HOUSING.place });
const SERVICES = [MATOURY_HOUSING, CAYENNE_HOUSING, CAYENNE_HEALTH];

const ids = (services: HelpService[]) => services.map((found) => found.id);

describe('filters', () => {
  it('keep the services of the chosen need, then of the chosen commune', () => {
    expect(ids(filterHelpServices(SERVICES, { category: 'housing', communeId: null }))).toEqual([1, 2]);
    expect(ids(filterHelpServices(SERVICES, { category: 'housing', communeId: 1 }))).toEqual([2]);
    expect(ids(filterHelpServices(SERVICES, { category: 'food', communeId: null }))).toEqual([]);
  });

  it('offer only the communes that have a service, by name', () => {
    expect(serviceCommunes(SERVICES)).toEqual([
      { id: 1, name: 'Cayenne' },
      { id: 3, name: 'Matoury' },
    ]);
  });

  it('live in the address, in French words, and come back from it', () => {
    const params = filtersToParams({ category: 'health', communeId: 1 });

    expect(params).toEqual({ besoin: 'sante', commune: '1' });
    expect(filtersFromParams(new URLSearchParams(params))).toEqual({ category: 'health', communeId: 1 });
  });

  it('ignore an address that was typed wrong', () => {
    expect(filtersFromParams(new URLSearchParams('besoin=piscine&commune=abc'))).toEqual({ category: null, communeId: null });
  });
});

describe('Comment y aller ?', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('goes to a health service for care, to the others for a procedure', () => {
    expect(purposeFor('health')).toBe('health');
    expect(purposeFor('housing')).toBe('administrative');
    expect(purposeFor('food')).toBe('administrative');
  });

  it('starts a trip to the service in 3 steps', () => {
    const draft = draftForHelpService(CAYENNE_HEALTH.id, CAYENNE_HEALTH.place, purposeFor(CAYENNE_HEALTH.category));

    expect(draft.dropoff).toEqual(CAYENNE_HEALTH.place);
    expect(draft.purpose).toBe('health');
    expect(skipsDropoff(draft)).toBe(true);
    expect(bookingSteps(draft)).toMatchObject({ pickup: 1, time: 2, confirm: 3, total: 3 });
  });

  it('goes back to the usual 4 steps once the destination is changed', () => {
    const draft = { ...draftForHelpService(1, MATOURY_HOUSING.place, 'administrative'), ...NO_GIVEN_DROPOFF };

    expect(bookingSteps(draft)).toMatchObject({ dropoff: 2, total: 4 });
  });

  it('keeps the service through a reload of the page', () => {
    const stored = new Map<string, string>();
    vi.stubGlobal('sessionStorage', {
      getItem: (key: string) => stored.get(key) ?? null,
      setItem: (key: string, value: string) => stored.set(key, value),
      removeItem: (key: string) => stored.delete(key),
    });

    saveBookingDraft(draftForHelpService(2, CAYENNE_HOUSING.place, 'administrative'));

    expect(readBookingDraft().helpServiceId).toBe(2);
    expect(skipsDropoff(readBookingDraft())).toBe(true);
  });
});

describe('a service', () => {
  afterEach(async () => {
    await setLanguage('fr');
    vi.unstubAllGlobals();
  });

  it('shows its fictitious number as people write it', () => {
    expect(formatPhone('+33536490001')).toBe('05 36 49 00 01');
    expect(formatPhone('+594694123456')).toBe('0694 12 34 56');
  });

  it('keeps its date of update in Guyana time', () => {
    // Read at midnight UTC, 2 November would be 1 November in Cayenne (UTC−3).
    expect(formatUpdatedOn('2026-11-02')).toContain('2 novembre');
  });

  it('says it speaks the language of the app, never French (every service speaks it)', async () => {
    expect(speaksAppLanguage(MATOURY_HOUSING)).toBeNull();

    await setLanguage('gcr');
    expect(speaksAppLanguage(MATOURY_HOUSING)).toBe('gcr');
    expect(speaksAppLanguage(CAYENNE_HOUSING)).toBeNull();
  });

  it('is handed over by the list only if it is the one asked for', () => {
    expect(serviceFromState({ service: CAYENNE_HOUSING }, 2)).toEqual(CAYENNE_HOUSING);
    expect(serviceFromState({ service: CAYENNE_HOUSING }, 1)).toBeNull();
    expect(serviceFromState({ service: { id: 2 } }, 2)).toBeNull();
    expect(serviceFromState(null, 2)).toBeNull();
  });

  it('kept on the phone is shown again only in the language it was received in', async () => {
    const stored = new Map<string, string>();
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => stored.get(key) ?? null,
      setItem: (key: string, value: string) => stored.set(key, value),
    });

    storeHelpServices(SERVICES);
    expect(ids(readStoredHelpServices() ?? [])).toEqual([1, 2, 3]);

    await setLanguage('en');
    expect(readStoredHelpServices()).toBeNull();
  });
});
