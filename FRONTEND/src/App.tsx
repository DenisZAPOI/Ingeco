import { BrowserRouter } from 'react-router-dom';

import { SessionProvider } from './context/SessionProvider';
import { useLanguage } from './hooks/useLanguage';
import { AppRoutes } from './routes/AppRoutes';

export function App() {
  // A change of language draws every screen again, with its texts and formats.
  // Rare (a choice of the user): redrawing the whole tree is simpler than
  // making each text listen to it.
  const language = useLanguage();
  return (
    <BrowserRouter>
      <SessionProvider>
        <AppRoutes key={language} />
      </SessionProvider>
    </BrowserRouter>
  );
}
