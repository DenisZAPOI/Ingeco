import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { App } from './App';
import { loadStoredLanguage } from './i18n';

// The texts of a language chosen on an earlier visit come first: the first
// screen is drawn in that language rather than in French, then redrawn.
void loadStoredLanguage().then(() => {
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
});
