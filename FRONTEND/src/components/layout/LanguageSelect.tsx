import { useId, useState } from 'react';

import { useLanguage } from '../../hooks/useLanguage';
import { availableLanguages, languageName, setLanguage, t, type Language } from '../../i18n';

/** Choice of the language, on every screen (cahier des charges §6: the language
 *  can change at any time). Each language is written in its own words, so that
 *  someone who does not read the current one still finds theirs. The choice is
 *  kept on this phone (i18n/index.ts). */
export function LanguageSelect() {
  const current = useLanguage();
  const id = useId();
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);
  const languages = availableLanguages();
  if (languages.length < 2) return null;

  // A translation is downloaded the first time it is chosen: on a slow
  // network the list waits, and says so if the download fails.
  async function choose(code: Language) {
    setFailed(false);
    setLoading(true);
    try {
      await setLanguage(code);
    } catch {
      setFailed(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="language-select">
      <div className="language-select-row">
        <label htmlFor={id}>{t('common.language')}</label>
        <select
          id={id}
          value={current}
          disabled={loading}
          aria-busy={loading}
          onChange={(event) => void choose(event.target.value as Language)}
        >
          {languages.map((code) => (
            <option key={code} value={code} lang={code}>
              {languageName(code)}
            </option>
          ))}
        </select>
      </div>
      {failed && (
        <p role="alert" className="field-error">
          {t('common.languageFailed')}
        </p>
      )}
    </div>
  );
}
