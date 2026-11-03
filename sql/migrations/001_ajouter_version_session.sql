-- 001 : colonne version_session sur utilisateur
-- 03/11/2026, Kurtys TSHIBOLA (équipe BD), issue #21 (audit de sécurité, F3)
-- Retour arrière : ALTER TABLE utilisateur DROP COLUMN version_session;
--
-- Compteur de sessions du compte. L'API l'augmente à chaque nouveau mot de
-- passe (profil, activation, mot de passe oublié) et à chaque suspension,
-- et le relit à chaque requête : une session ouverte avant ce changement
-- reçoit 401. Les comptes existants partent de 0. Jamais envoyé au front.

ALTER TABLE utilisateur
    ADD COLUMN version_session INT NOT NULL DEFAULT 0,
    ADD CONSTRAINT chk_utilisateur_version_session CHECK (version_session >= 0);
