import { Route, Routes } from 'react-router-dom';

import { Layout } from '../components/layout/Layout';
import { DiagnosticPage } from '../pages/DiagnosticPage';
import { HomePage } from '../pages/HomePage';
import { NotFoundPage } from '../pages/NotFoundPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="diagnostic" element={<DiagnosticPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
