-- 013 : fiches pratiques « Comment faire ? » (module M5)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #49 (cahier des charges §7.5, P1 ; ADR 018 et 019)
-- Retour arrière :
--   DROP TABLE fiche_pratique_a_apporter; DROP TABLE fiche_pratique_etape;
--   DROP TABLE fiche_pratique_traduction; DROP TABLE fiche_pratique;
--
-- Une fiche en langage simple : un titre, une introduction, des étapes
-- dans l'ordre (une phrase courte chacune, lue aussi à voix haute par le
-- téléphone, ADR 019), ce qu'il faut apporter, et la page officielle qui
-- tient les règles à jour. Forme reprise de l'écran déjà codé (sprint 1),
-- plus détaillée que le simple « contenu » proposé dans l'issue : les
-- étapes sont des lignes, pas un texte à découper.
--
-- Langues : titre, introduction et nom de la source sont en français dans
-- fiche_pratique, traduits dans fiche_pratique_traduction (même modèle
-- que les offres). Les étapes et les choses à apporter sont des listes :
-- elles portent leur langue, français compris, dans fiche_pratique_etape et
-- fiche_pratique_a_apporter. Pour une langue, l'API prend la traduction ET
-- les listes de cette langue, ou tout en français : une fiche ne mélange
-- jamais deux langues. Une traduction a donc autant d'étapes que le
-- français ; c'est à l'écriture des données d'y veiller.

CREATE TABLE fiche_pratique (
    id_fiche       INT AUTO_INCREMENT PRIMARY KEY,
    -- Mêmes besoins que service_aide (migration 012)
    categorie      ENUM('garde','logement','droits','sante','aide_alimentaire','numerique','demarches','equipement') NOT NULL,
    titre          VARCHAR(150) NOT NULL,
    introduction   VARCHAR(500) NOT NULL,
    -- Page officielle qui tient les règles à jour. Les deux NULL quand il
    -- n'y en a pas de fiable : une étape nomme alors le lieu où demander
    source_nom     VARCHAR(150),
    source_url     VARCHAR(500),
    mis_a_jour_le  DATE    NOT NULL,
    active         BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_fiche_pratique_source CHECK ((source_nom IS NULL) = (source_url IS NULL)),
    CONSTRAINT chk_fiche_pratique_url    CHECK (source_url IS NULL OR source_url LIKE 'https://%'),
    CONSTRAINT chk_fiche_pratique_textes CHECK (titre <> '' AND introduction <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_fiche_pratique_categorie ON fiche_pratique(active, categorie);

CREATE TABLE fiche_pratique_traduction (
    id_fiche      INT NOT NULL,
    code_langue   VARCHAR(10) NOT NULL,
    titre         VARCHAR(150) NOT NULL,
    introduction  VARCHAR(500) NOT NULL,
    -- NULL si la fiche n'a pas de source
    source_nom    VARCHAR(150),
    PRIMARY KEY (id_fiche, code_langue),
    FOREIGN KEY (id_fiche)    REFERENCES fiche_pratique(id_fiche),
    FOREIGN KEY (code_langue) REFERENCES langue(code),
    CONSTRAINT chk_fiche_pratique_traduction_langue CHECK (code_langue <> 'fr'),
    CONSTRAINT chk_fiche_pratique_traduction_textes CHECK (titre <> '' AND introduction <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Les étapes, dans l'ordre, une ligne par étape et par langue
CREATE TABLE fiche_pratique_etape (
    id_fiche     INT NOT NULL,
    code_langue  VARCHAR(10) NOT NULL,
    ordre        TINYINT NOT NULL,
    texte        VARCHAR(300) NOT NULL,
    PRIMARY KEY (id_fiche, code_langue, ordre),
    FOREIGN KEY (id_fiche)    REFERENCES fiche_pratique(id_fiche),
    FOREIGN KEY (code_langue) REFERENCES langue(code),
    CONSTRAINT chk_fiche_pratique_etape_ordre CHECK (ordre BETWEEN 1 AND 20),
    CONSTRAINT chk_fiche_pratique_etape_texte CHECK (texte <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ce qu'il faut apporter ; aucune ligne quand rien de spécial n'est demandé
CREATE TABLE fiche_pratique_a_apporter (
    id_fiche     INT NOT NULL,
    code_langue  VARCHAR(10) NOT NULL,
    ordre        TINYINT NOT NULL,
    texte        VARCHAR(150) NOT NULL,
    PRIMARY KEY (id_fiche, code_langue, ordre),
    FOREIGN KEY (id_fiche)    REFERENCES fiche_pratique(id_fiche),
    FOREIGN KEY (code_langue) REFERENCES langue(code),
    CONSTRAINT chk_fiche_pratique_a_apporter_ordre CHECK (ordre BETWEEN 1 AND 20),
    CONSTRAINT chk_fiche_pratique_a_apporter_texte CHECK (texte <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
