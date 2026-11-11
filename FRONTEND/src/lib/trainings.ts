// Training (module M3, palier P1): links to existing catalogues, nothing
// stored by us. The list is fixed and lives in the front: no call to the API,
// the page shows at once even on 2G. Names and descriptions are in the
// translation files (trainings.catalogues.<id>). Addresses checked on
// 10/11/2026; to move to the database only if the administrator must edit them.

export type TrainingCatalogue = {
  id: 'franceTravail' | 'cpf';
  url: string;
};

export const TRAINING_CATALOGUES: readonly TrainingCatalogue[] = [
  // Every training in France, searchable by place: Cayenne, Kourou…
  { id: 'franceTravail', url: 'https://candidat.francetravail.fr/formations/recherche' },
  // Trainings paid with the personal training account (CPF).
  { id: 'cpf', url: 'https://www.moncompteformation.gouv.fr' },
];
