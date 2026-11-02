import { Navigate, Outlet, Route, Routes } from 'react-router-dom';

import { Layout } from '../components/layout/Layout';
import { BookingDraftProvider } from '../context/BookingDraftProvider';
import { BOOKING_PATHS } from '../lib/paths';
import { ActivatePage } from '../pages/ActivatePage';
import { BookingConfirmPage } from '../pages/BookingConfirmPage';
import { BookingPlacePage } from '../pages/BookingPlacePage';
import { BookingTimePage } from '../pages/BookingTimePage';
import { DiagnosticPage } from '../pages/DiagnosticPage';
import { HomePage } from '../pages/HomePage';
import { LoginPage } from '../pages/LoginPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { ProfilePage } from '../pages/ProfilePage';
import { RegisterPage } from '../pages/RegisterPage';
import { RidePage } from '../pages/RidePage';
import { RidePaymentPage } from '../pages/RidePaymentPage';
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
          {/* The steps of a booking share its draft. */}
          <Route
            path="reserver"
            element={
              <BookingDraftProvider>
                <Outlet />
              </BookingDraftProvider>
            }
          >
            <Route index element={<Navigate to={BOOKING_PATHS.pickup} replace />} />
            <Route path="depart" element={<BookingPlacePage key="pickup" stop="pickup" />} />
            <Route path="arrivee" element={<BookingPlacePage key="dropoff" stop="dropoff" />} />
            <Route path="horaire" element={<BookingTimePage />} />
            <Route path="confirmation" element={<BookingConfirmPage />} />
          </Route>
          <Route path="trajets/:id" element={<RidePage />} />
          <Route path="trajets/:id/paiement" element={<RidePaymentPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
