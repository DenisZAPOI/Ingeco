import { Navigate, Outlet, Route, Routes } from 'react-router-dom';

import { Layout } from '../components/layout/Layout';
import { BookingDraftProvider } from '../context/BookingDraftProvider';
import { BOOKING_PATHS } from '../lib/paths';
import { AboutPage } from '../pages/AboutPage';
import { ActivatePage } from '../pages/ActivatePage';
import { AdminAccountPage } from '../pages/AdminAccountPage';
import { AdminAccountsPage } from '../pages/AdminAccountsPage';
import { AdminNewAccountPage } from '../pages/AdminNewAccountPage';
import { BookingConfirmPage } from '../pages/BookingConfirmPage';
import { BookingPlacePage } from '../pages/BookingPlacePage';
import { BookingTimePage } from '../pages/BookingTimePage';
import { DiagnosticPage } from '../pages/DiagnosticPage';
import { DriverEarningsPage } from '../pages/DriverEarningsPage';
import { DriverRidePage } from '../pages/DriverRidePage';
import { DriverRidesPage } from '../pages/DriverRidesPage';
import { FaqPage } from '../pages/FaqPage';
import { HelpPage } from '../pages/HelpPage';
import { HomePage } from '../pages/HomePage';
import { JobPage } from '../pages/JobPage';
import { JobsPage } from '../pages/JobsPage';
import { TrainingsPage } from '../pages/TrainingsPage';
import { LoginPage } from '../pages/LoginPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { PasswordResetPage } from '../pages/PasswordResetPage';
import { ProfilePage } from '../pages/ProfilePage';
import { RegisterPage } from '../pages/RegisterPage';
import { RidePage } from '../pages/RidePage';
import { RidePaymentPage } from '../pages/RidePaymentPage';
import { RidesPage } from '../pages/RidesPage';
import { LoggedInRoutes, VisitorRoutes } from './AccessRoutes';

// Paths in French: users see them in the address bar.
export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="diagnostic" element={<DiagnosticPage />} />
        <Route path="a-propos" element={<AboutPage />} />
        <Route path="aide" element={<HelpPage />} />
        <Route path="aide/questions" element={<FaqPage />} />
        <Route path="emplois" element={<JobsPage />} />
        <Route path="emplois/:id" element={<JobPage />} />
        <Route path="formations" element={<TrainingsPage />} />
        <Route element={<VisitorRoutes />}>
          <Route path="connexion" element={<LoginPage />} />
          <Route path="inscription" element={<RegisterPage />} />
          <Route path="activation" element={<ActivatePage />} />
          <Route path="mot-de-passe-oublie" element={<PasswordResetPage />} />
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
          <Route path="trajets" element={<RidesPage />} />
          <Route path="trajets/:id" element={<RidePage />} />
          <Route path="trajets/:id/paiement" element={<RidePaymentPage />} />
          <Route path="courses" element={<DriverRidesPage />} />
          <Route path="courses/:id" element={<DriverRidePage />} />
          <Route path="revenus" element={<DriverEarningsPage />} />
          <Route path="admin/comptes" element={<AdminAccountsPage />} />
          <Route path="admin/comptes/nouveau" element={<AdminNewAccountPage />} />
          <Route path="admin/comptes/:id" element={<AdminAccountPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
