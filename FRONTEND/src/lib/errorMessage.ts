import { ApiError } from '../api/client';
import { t } from '../i18n';

// Short, plain-language messages: the public is not always at ease with
// digital tools, a technical message would not help them.

export function errorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return t('errors.generic');
  }
  if (error.status === 0) {
    return t('errors.offline');
  }
  if (error.status >= 500) {
    return t('errors.server');
  }
  if (error.status === 400) {
    // The detail lists the faulty fields: each form shows them next to the field.
    return t('errors.checkFields');
  }
  // The API writes its business messages in French, for the user (docs/adr/013).
  if (typeof error.detail === 'string') {
    return error.detail;
  }
  if (error.status === 401) return t('errors.unauthorized');
  if (error.status === 403) return t('errors.forbidden');
  return t('errors.generic');
}
