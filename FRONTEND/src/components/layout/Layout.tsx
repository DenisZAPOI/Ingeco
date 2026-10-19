import { Link, Outlet } from 'react-router-dom';

export function Layout() {
  return (
    <>
      <header className="header">
        <Link to="/" className="brand">
          En route pour l'emploi
        </Link>
      </header>
      <main className="main">
        <Outlet />
      </main>
    </>
  );
}
