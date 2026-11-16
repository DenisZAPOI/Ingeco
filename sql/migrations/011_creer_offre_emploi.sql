-- 011 : tables offre_emploi et offre_emploi_traduction (module M2)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #48 (cahier des charges §7.2, P1 ; ADR 018)
-- Retour arrière : DROP TABLE offre_emploi_traduction; DROP TABLE offre_emploi;
--
-- Un jeu d'offres d'emploi FICTIVES (cahier des charges §5 : aucune donnée
-- réelle), filtrables par commune, horaires, débutant accepté et sans
-- diplôme. « Comment y aller ? » préremplit l'arrivée d'un trajet avec le
-- lieu de l'offre : adresse, lat, lng et commune ont les formats de course.
-- Une offre peut être dans une commune non desservie (migration 010) :
-- l'API le dit à l'usager au lieu de proposer un trajet impossible.
--
-- Textes en français dans offre_emploi (langue de référence, jamais vide).
-- Les autres langues sont dans offre_emploi_traduction, une ligne par
-- langue ; l'API lit avec un LEFT JOIN sur la langue demandée et retombe
-- sur le français s'il n'y a pas de ligne. Les trois textes viennent
-- toujours de la même langue : ils sont tous NOT NULL dans une traduction.
--
-- Une offre retirée passe à active = FALSE : jamais supprimée.

CREATE TABLE offre_emploi (
    id_offre           INT AUTO_INCREMENT PRIMARY KEY,
    intitule           VARCHAR(150) NOT NULL,
    employeur          VARCHAR(150) NOT NULL,  -- nom fictif
    description        TEXT         NOT NULL,  -- en langage simple
    type_contrat       ENUM('cdi','cdd','interim','alternance','saisonnier') NOT NULL,
    -- Filtre « horaires »
    plage_horaire      ENUM('journee','horaires_decales','nuit') NOT NULL,
    temps_partiel      BOOLEAN NOT NULL,
    debutant_accepte   BOOLEAN NOT NULL,
    sans_diplome       BOOLEAN NOT NULL,
    -- Lieu de travail, mêmes formats que l'arrivée d'une course
    adresse            VARCHAR(255) NOT NULL,
    lat                DECIMAL(9,6) NOT NULL,
    lng                DECIMAL(9,6) NOT NULL,
    id_commune         INT NOT NULL,
    publiee_le         DATETIME NOT NULL,
    active             BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_commune) REFERENCES commune(id_commune),
    CONSTRAINT chk_offre_emploi_position CHECK (lat BETWEEN -90 AND 90 AND lng BETWEEN -180 AND 180),
    CONSTRAINT chk_offre_emploi_textes   CHECK (intitule <> '' AND employeur <> '' AND description <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Liste filtrée des offres actives, les plus récentes d'abord
CREATE INDEX idx_offre_emploi_liste ON offre_emploi(active, id_commune, publiee_le);

CREATE TABLE offre_emploi_traduction (
    id_offre     INT NOT NULL,
    code_langue  VARCHAR(10) NOT NULL,
    intitule     VARCHAR(150) NOT NULL,
    employeur    VARCHAR(150) NOT NULL,
    description  TEXT         NOT NULL,
    PRIMARY KEY (id_offre, code_langue),
    FOREIGN KEY (id_offre)    REFERENCES offre_emploi(id_offre),
    FOREIGN KEY (code_langue) REFERENCES langue(code),
    -- Le français est dans offre_emploi
    CONSTRAINT chk_offre_emploi_traduction_langue CHECK (code_langue <> 'fr'),
    CONSTRAINT chk_offre_emploi_traduction_textes CHECK (intitule <> '' AND employeur <> '' AND description <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
