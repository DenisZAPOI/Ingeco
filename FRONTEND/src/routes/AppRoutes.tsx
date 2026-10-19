import { Route, Routes } from 'react-router-dom';

import { Layout } from '../components/layout/Layout';
import { ActivatePage } from '../pages/ActivatePage';
import { DiagnosticPage } from '../pages/DiagnosticPage';
import { HomePage } from '../pages/HomePage';
import { LoginPage } from '../pages/LoginPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { ProfilePage } from '../pages/ProfilePage';
import { RegisterPage } from '../pages/RegisterPage';
import { LoggedInRoutes, VisitorRoutes } from './AccessRoutes';

// Paths in French: users see them in the address bar.
export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="diagnostic" element={<DiagnosticPage />} />
        <Route element={<VisitorRoutes />}>
          <Route path="connexion" element={<LoginPage />} />
          <Route path="inscription" element={<RegisterPage />} />
          <Route path="activation" element={<ActivatePage />} />
        </Route>
        <Route element={<LoggedInRoutes />}>
          <Route path="profil" element={<ProfilePage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
