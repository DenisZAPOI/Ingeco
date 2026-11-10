// Job offers: the filters run on the phone (one call for the whole list), and
// "Comment y aller ?" starts a booking of 3 steps instead of 4.

import { afterEach, describe, expect, it, vi } from 'vitest';

import type { JobOffer } from '../api/jobs';
import { bookingSteps, draftForJobOffer, skipsDropoff } from './bookingDraft';
import { setLanguage } from '../i18n';
import { NO_FILTER, filterJobOffers, filtersFromParams, filtersToParams, offerCommunes, readStoredJobOffers, storeJobOffers } from './jobs';
import { returnPathFromState } from './paths';

function offer(changes: Partial<JobOffer>): JobOffer {
  return {
    id: 1,
    title: 'Employé(e) de rayon',
    employer: 'Supermarché (fictif)',
    description: '',
    contractType: 'fixed_term',
    schedule: 'day',
    partTime: false,
    beginnerWelcome: false,
    noDiplomaRequired: false,
    place: { address: 'Mairie de Matoury', lat: 4.847, lng: -52.331, communeId: 3, token: 'signed' },
    communeName: 'Matoury',
    publishedAt: '2026-11-09T12:00:00Z',
    language: 'fr',
    ...changes,
  };
}

const MATOURY_DAY = offer({ id: 1 });
const CAYENNE_NIGHT_BEGINNER = offer({
  id: 2,
  schedule: 'night',
  beginnerWelcome: true,
  place: { address: 'Gare routière, Cayenne', lat: 4.935, lng: -52.328, communeId: 1, token: 'signed' },
  communeName: 'Cayenne',
});
const CAYENNE_DAY_NO_DIPLOMA = offer({
  id: 3,
  noDiplomaRequired: true,
  beginnerWelcome: true,
  place: { address: 'Marché de Cayenne', lat: 4.936, lng: -52.33, communeId: 1, token: 'signed' },
  communeName: 'Cayenne',
});
const OFFERS = [MATOURY_DAY, CAYENNE_NIGHT_BEGINNER, CAYENNE_DAY_NO_DIPLOMA];

function ids(offers: JobOffer[]): number[] {
  return offers.map((found) => found.id);
}

describe('filterJobOffers', () => {
  it('keeps every offer without a filter', () => {
    expect(ids(filterJobOffers(OFFERS, NO_FILTER))).toEqual([1, 2, 3]);
  });

  it('combines the filters: each one narrows the list', () => {
    expect(ids(filterJobOffers(OFFERS, { ...NO_FILTER, communeId: 1 }))).toEqual([2, 3]);
    expect(ids(filterJobOffers(OFFERS, { ...NO_FILTER, communeId: 1, schedule: 'day' }))).toEqual([3]);
    expect(ids(filterJobOffers(OFFERS, { ...NO_FILTER, beginnerWelcome: true }))).toEqual([2, 3]);
    expect(ids(filterJobOffers(OFFERS, { ...NO_FILTER, beginnerWelcome: true, noDiplomaRequired: true }))).toEqual([3]);
  });
});

describe('offerCommunes', () => {
  it('lists each commune once, by name', () => {
    expect(offerCommunes(OFFERS)).toEqual([
      { id: 1, name: 'Cayenne' },
      { id: 3, name: 'Matoury' },
    ]);
  });
});

describe('filters in the address', () => {
  it('reads back what it wrote', () => {
    const filters = { communeId: 3, schedule: 'night' as const, beginnerWelcome: true, noDiplomaRequired: false };
    expect(filtersFromParams(new URLSearchParams(filtersToParams(filters)))).toEqual(filters);
  });

  it('writes nothing without a filter', () => {
    expect(filtersToParams(NO_FILTER)).toEqual({});
  });

  it('ignores a value typed by hand that means nothing', () => {
    expect(filtersFromParams(new URLSearchParams('commune=abc&horaires=matin&debutant=oui'))).toEqual(NO_FILTER);
  });
});

describe('Comment y aller ?', () => {
  it('starts a trip to the job, for work, in 3 steps', () => {
    const draft = draftForJobOffer(MATOURY_DAY.id, MATOURY_DAY.place);

    expect(draft.dropoff).toEqual(MATOURY_DAY.place);
    expect(draft.purpose).toBe('employment');
    expect(skipsDropoff(draft)).toBe(true);
    expect(bookingSteps(draft)).toMatchObject({ pickup: 1, time: 2, confirm: 3, total: 3 });
  });

  it('goes back to the usual 4 steps once the destination is changed', () => {
    const draft = { ...draftForJobOffer(MATOURY_DAY.id, MATOURY_DAY.place), jobOfferId: null };

    expect(bookingSteps(draft)).toMatchObject({ pickup: 1, dropoff: 2, time: 3, confirm: 4, total: 4 });
  });
});

describe('returnPathFromState', () => {
  it('returns to a page of the app after the login', () => {
    expect(returnPathFromState({ returnTo: '/reserver/depart' })).toBe('/reserver/depart');
  });

  it('never leads out of the app', () => {
    expect(returnPathFromState({ returnTo: '//site.example' })).toBeNull();
    expect(returnPathFromState({ returnTo: '/\\site.example' })).toBeNull();
    expect(returnPathFromState({ returnTo: 'https://site.example' })).toBeNull();
    expect(returnPathFromState(null)).toBeNull();
  });
});

describe('offers kept on the phone', () => {
  afterEach(async () => {
    await setLanguage('fr');
    vi.unstubAllGlobals();
  });

  it('are shown again only in the language they were received in', async () => {
    const stored = new Map<string, string>();
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => stored.get(key) ?? null,
      setItem: (key: string, value: string) => stored.set(key, value),
    });

    storeJobOffers(OFFERS);
    expect(ids(readStoredJobOffers() ?? [])).toEqual([1, 2, 3]);

    // In French on the phone: after switching to English, the API is waited for.
    await setLanguage('en');
    expect(readStoredJobOffers()).toBeNull();
  });
});
