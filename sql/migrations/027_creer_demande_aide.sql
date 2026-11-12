-- 027 : table demande_aide (« Être rappelé » et « Signaler un problème »)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #57 (cahier des charges §6, P1, module M0)
-- Retour arrière : DROP TABLE demande_aide;
--
-- Les deux demandes ont la même forme : une personne laisse un message ou
-- un numéro, un administrateur ou un opérateur la traite. Même modèle que
-- demande_suppression (migration 002) : traitee_le et id_traitee_par, et
-- aucune ligne n'est jamais supprimée.
--
-- Une personne non connectée peut demander à être rappelée : id_utilisateur
-- est NULL, et il faut alors un téléphone (même format que
-- utilisateur.telephone). Un signalement peut porter sur un trajet
-- (id_course) ; une demande de rappel, non.
--
-- Le message est libre : jamais de donnée de santé ni de diagnostic (§12),
-- l'écran doit le rappeler. Aucun service d'urgence n'est promis (§6).

CREATE TABLE demande_aide (
    id_demande      INT AUTO_INCREMENT PRIMARY KEY,
    type            ENUM('rappel','signalement') NOT NULL,
    -- NULL si la personne n'est pas connectée
    id_utilisateur  INT,
    -- Numéro où rappeler, pour une personne sans compte (ou un autre numéro)
    telephone       VARCHAR(16),
    id_course       INT,
    message         VARCHAR(1000),
    creee_le        DATETIME NOT NULL,
    -- NULL tant que la demande n'est pas traitée
    traitee_le      DATETIME,
    id_traitee_par  INT,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY (id_course)      REFERENCES course(id_course),
    FOREIGN KEY (id_traitee_par) REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT chk_demande_aide_contact   CHECK (id_utilisateur IS NOT NULL OR telephone IS NOT NULL),
    CONSTRAINT chk_demande_aide_telephone CHECK (telephone IS NULL OR telephone REGEXP '^[+][0-9]{8,15}$'),
    CONSTRAINT chk_demande_aide_course    CHECK (id_course IS NULL OR type = 'signalement'),
    CONSTRAINT chk_demande_aide_message   CHECK (message IS NULL OR message <> ''),
    CONSTRAINT chk_demande_aide_traitee   CHECK ((traitee_le IS NULL) = (id_traitee_par IS NULL)),
    CONSTRAINT chk_demande_aide_dates     CHECK (traitee_le IS NULL OR traitee_le >= creee_le)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Demandes à traiter, les plus anciennes d'abord, par type
CREATE INDEX idx_demande_aide_a_traiter ON demande_aide(traitee_le, type, creee_le);
-- Demandes d'une personne
CREATE INDEX idx_demande_aide_utilisateur ON demande_aide(id_utilisateur, creee_le);
