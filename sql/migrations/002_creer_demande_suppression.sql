-- 002 : table demande_suppression (demandes de suppression de compte)
-- 03/11/2026, Kurtys TSHIBOLA (équipe BD), issue #32 (cahier des charges §6, P1)
-- Retour arrière : DROP TABLE demande_suppression;
--
-- Une personne demande la suppression de son compte ; un administrateur la
-- traite. Une table plutôt qu'une colonne sur utilisateur : on garde
-- l'historique (qui a demandé, quand, qui a traité, quand), utile au
-- registre des traitements. Aucune ligne n'est jamais supprimée.
--
-- Ce que devient le compte une fois la demande traitée (anonymisation du
-- nom, du téléphone et du courriel, courses gardées sans identité) reste à
-- décider ensemble (issue #32) : ce sera une autre migration si le schéma
-- doit changer.

CREATE TABLE demande_suppression (
    id_demande      INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur  INT NOT NULL,
    demandee_le     DATETIME NOT NULL,
    -- NULL tant que la demande n'est pas traitée
    traitee_le      DATETIME,
    id_traitee_par  INT,
    -- Une seule demande en cours par compte : vaut id_utilisateur tant que
    -- la demande n'est pas traitée, NULL ensuite (UNIQUE accepte plusieurs
    -- NULL). Même principe que tarif_actif dans schema-mvp.sql. Colonne
    -- calculée par MySQL : l'API ne l'écrit jamais.
    demande_en_cours INT GENERATED ALWAYS AS (IF(traitee_le IS NULL, id_utilisateur, NULL)) STORED UNIQUE,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY (id_traitee_par) REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT chk_demande_suppression_traitee CHECK ((traitee_le IS NULL) = (id_traitee_par IS NULL)),
    CONSTRAINT chk_demande_suppression_dates   CHECK (traitee_le IS NULL OR traitee_le >= demandee_le)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Liste des demandes à traiter, les plus anciennes d'abord (administrateur)
CREATE INDEX idx_demande_suppression_a_traiter ON demande_suppression(traitee_le, demandee_le);
