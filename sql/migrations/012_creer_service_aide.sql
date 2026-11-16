-- 012 : tables service_aide, service_aide_langue et service_aide_traduction (module M5)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #49 (cahier des charges §7.5, P1 ; ADR 018)
-- Retour arrière :
--   DROP TABLE service_aide_traduction; DROP TABLE service_aide_langue; DROP TABLE service_aide;
--
-- Annuaire de services d'aide FICTIFS, recherchables par commune et par
-- besoin, avec les langues parlées, les horaires, l'accessibilité et la
-- date de mise à jour. Le lieu sert à « Comment y aller ? », comme pour
-- les offres. Un service « santé » décrit un lieu d'accueil, jamais une
-- pathologie (§12 : pas de diagnostic médical).
--
-- Les huit besoins sont ceux du cahier des charges (§7.5) ; la même liste
-- sert aux fiches pratiques (migration 013).
--
-- Traductions : même modèle que les offres (migration 011). Français dans
-- service_aide ; autres langues dans service_aide_traduction ; repli sur
-- le français. Un service fermé passe à actif = FALSE.

CREATE TABLE service_aide (
    id_service      INT AUTO_INCREMENT PRIMARY KEY,
    nom             VARCHAR(150) NOT NULL,
    categorie       ENUM('garde','logement','droits','sante','aide_alimentaire','numerique','demarches','equipement') NOT NULL,
    description     TEXT         NOT NULL,
    -- Texte libre, en heure de Guyane (« Du lundi au vendredi, 8 h – 12 h »)
    horaires        VARCHAR(255) NOT NULL,
    adresse         VARCHAR(255) NOT NULL,
    lat             DECIMAL(9,6) NOT NULL,
    lng             DECIMAL(9,6) NOT NULL,
    id_commune      INT NOT NULL,
    -- Numéro fictif, au format international comme utilisateur.telephone
    telephone       VARCHAR(16),
    accessible_pmr  BOOLEAN NOT NULL,
    mis_a_jour_le   DATE    NOT NULL,
    actif           BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_commune) REFERENCES commune(id_commune),
    CONSTRAINT chk_service_aide_position  CHECK (lat BETWEEN -90 AND 90 AND lng BETWEEN -180 AND 180),
    CONSTRAINT chk_service_aide_telephone CHECK (telephone IS NULL OR telephone REGEXP '^[+][0-9]{8,15}$'),
    CONSTRAINT chk_service_aide_textes    CHECK (nom <> '' AND description <> '' AND horaires <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Recherche par besoin et par commune
CREATE INDEX idx_service_aide_recherche ON service_aide(actif, categorie, id_commune);

-- Langues parlées sur place (plusieurs par service)
CREATE TABLE service_aide_langue (
    id_service   INT NOT NULL,
    code_langue  VARCHAR(10) NOT NULL,
    PRIMARY KEY (id_service, code_langue),
    FOREIGN KEY (id_service)  REFERENCES service_aide(id_service),
    FOREIGN KEY (code_langue) REFERENCES langue(code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE service_aide_traduction (
    id_service   INT NOT NULL,
    code_langue  VARCHAR(10) NOT NULL,
    nom          VARCHAR(150) NOT NULL,
    description  TEXT         NOT NULL,
    horaires     VARCHAR(255) NOT NULL,
    PRIMARY KEY (id_service, code_langue),
    FOREIGN KEY (id_service)  REFERENCES service_aide(id_service),
    FOREIGN KEY (code_langue) REFERENCES langue(code),
    CONSTRAINT chk_service_aide_traduction_langue CHECK (code_langue <> 'fr'),
    CONSTRAINT chk_service_aide_traduction_textes CHECK (nom <> '' AND description <> '' AND horaires <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
