import { useSyncExternalStore } from 'react';

import { language, subscribeToLanguage, type Language } from '../i18n';

/** The current language; the component renders again when it changes. */
export function useLanguage(): Language {
  return useSyncExternalStore(subscribeToLanguage, language);
}
