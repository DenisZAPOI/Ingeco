import { describe, expect, it } from 'vitest';

import { t } from '../i18n';
import { TRAINING_CATALOGUES } from './trainings';

describe('training catalogues', () => {
  it('only lead to secure sites', () => {
    for (const catalogue of TRAINING_CATALOGUES) {
      expect(new URL(catalogue.url).protocol).toBe('https:');
    }
  });

  it('each have a name, a description and a link text', () => {
    for (const { id } of TRAINING_CATALOGUES) {
      expect(t(`trainings.catalogues.${id}.name`)).not.toBe('');
      expect(t(`trainings.catalogues.${id}.description`)).not.toBe('');
      expect(t(`trainings.catalogues.${id}.open`)).not.toBe('');
    }
  });
});
