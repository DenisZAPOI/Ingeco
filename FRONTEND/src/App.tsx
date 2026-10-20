import { BrowserRouter } from 'react-router-dom';

import { SessionProvider } from './context/SessionProvider';
import { AppRoutes } from './routes/AppRoutes';

export function App() {
  return (
    <BrowserRouter>
      <SessionProvider>
        <AppRoutes />
      </SessionProvider>
    </BrowserRouter>
  );
}
