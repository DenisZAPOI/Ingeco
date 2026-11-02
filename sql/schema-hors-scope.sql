-- ============================================================
-- En route pour l'emploi : schéma de la base, HORS MVP
-- ============================================================
-- Version 2 (20/10/2026). À lancer APRÈS schema-mvp.sql.
--
-- Ce fichier garde ce qui n'est pas encore dans le périmètre, pour ne pas
-- perdre le travail de la première version. Rien ici n'est validé par la
-- cliente : l'API ne s'en sert pas tant qu'un élément n'est pas passé dans
-- schema-mvp.sql.
--
--   1. Bons solidaires et structures partenaires : le fonctionnement des
--      bons n'est pas encore spécifié par la cliente. Le modèle ci-dessous
--      est l'hypothèse H7 du contrat d'API (un pourcentage de prise en
--      charge sur un nombre de courses), à revoir selon sa réponse.
--   2. Documents des chauffeurs (UC72), dont l'agrément pour le transport
--      de personnes handicapées (UC80, « en deuxième partie »).
--   3. Module de formation des chauffeurs (UC76).
--   4. Indicateur d'impact social : chauffeur en parcours d'insertion (UC74).
--
-- Pas encore modélisés, faute de besoin précis : abonnement mensuel (UC79),
-- notifications dans l'application (UC73), tarifs par profil ou par
-- financement (UC70, UC71), facturation consolidée des partenaires (UC75).
-- ============================================================

SET NAMES utf8mb4;

-- ------------------------------------------------------------
-- 1. Bons solidaires et structures partenaires
-- ------------------------------------------------------------

INSERT INTO role (code, libelle) VALUES
('partner', 'Référent partenaire');

-- Association, collectivité ou entreprise qui finance des trajets
CREATE TABLE structure_partenaire (
    id_structure  INT AUTO_INCREMENT PRIMARY KEY,
    nom           VARCHAR(150) NOT NULL,
    type          ENUM('association','collectivite','entreprise') NOT NULL,
    -- Les bons d'une structure suspendue ne sont plus acceptés pour de
    -- nouvelles réservations
    statut        ENUM('active','suspendue') NOT NULL DEFAULT 'active',
    cree_le       DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Informations propres au rôle partner. Une structure a un ou plusieurs
-- référents.
CREATE TABLE referent (
    id_utilisateur  INT PRIMARY KEY,
    id_structure    INT NOT NULL,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY (id_structure)   REFERENCES structure_partenaire(id_structure)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- « Expiré » et « épuisé » ne sont pas des statuts : ils se déduisent des
-- dates et du compteur, qui ne peuvent donc pas se contredire.
CREATE TABLE bon_solidaire (
    id_bon                       INT AUTO_INCREMENT PRIMARY KEY,
    -- SOL- + 8 caractères sans lettres ambiguës, généré par l'API
    code                         VARCHAR(12) NOT NULL UNIQUE,
    id_structure                 INT NOT NULL,
    id_emis_par                  INT NOT NULL,
    -- Si renseigné, seul cet usager peut l'utiliser
    id_beneficiaire              INT,
    pourcentage_prise_en_charge  TINYINT NOT NULL, -- 100 = prise en charge totale
    nb_courses_max               INT NOT NULL,
    nb_courses_utilisees         INT NOT NULL DEFAULT 0,
    -- Dates en heure de Guyane, bornes incluses
    valide_du                    DATE NOT NULL,
    valide_au                    DATE NOT NULL,
    statut                       ENUM('actif','revoque') NOT NULL DEFAULT 'actif',
    cree_le                      DATETIME NOT NULL,
    FOREIGN KEY (id_structure)    REFERENCES structure_partenaire(id_structure),
    FOREIGN KEY (id_emis_par)     REFERENCES referent(id_utilisateur),
    FOREIGN KEY (id_beneficiaire) REFERENCES usager(id_utilisateur),
    CONSTRAINT chk_bon_pourcentage CHECK (pourcentage_prise_en_charge BETWEEN 1 AND 100),
    CONSTRAINT chk_bon_courses     CHECK (nb_courses_max >= 1 AND nb_courses_utilisees BETWEEN 0 AND nb_courses_max),
    CONSTRAINT chk_bon_dates       CHECK (valide_au >= valide_du)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_bon_structure ON bon_solidaire(id_structure, statut);

-- Traçabilité exigée par le cahier des charges : le bon et la part prise en
-- charge restent sur la course, même si le bon est révoqué ou la course
-- annulée. Part de l'usager = prix_centimes - part_bon_centimes.
ALTER TABLE course
    ADD COLUMN id_bon INT AFTER prix_centimes,
    ADD COLUMN part_bon_centimes INT NOT NULL DEFAULT 0 AFTER id_bon,
    ADD CONSTRAINT fk_course_bon FOREIGN KEY (id_bon) REFERENCES bon_solidaire(id_bon),
    ADD CONSTRAINT chk_course_part_bon CHECK (
        part_bon_centimes BETWEEN 0 AND prix_centimes
        AND (id_bon IS NOT NULL OR part_bon_centimes = 0)
    ),
    -- Paiement non requis si et seulement si le bon couvre tout
    ADD CONSTRAINT chk_course_non_requis CHECK (
        (statut_paiement = 'non_requis') = (part_bon_centimes = prix_centimes)
    );

CREATE INDEX idx_course_bon ON course(id_bon);

-- ------------------------------------------------------------
-- 2. Documents des chauffeurs (UC72, UC80)
-- ------------------------------------------------------------
-- Dans le MVP, les documents sont vérifiés en personne et rien n'est stocké.
-- Si cette table sert un jour : pièces d'identité = données sensibles,
-- prévoir durée de conservation et accès restreint (RGPD).
CREATE TABLE document_chauffeur (
    id_document             INT AUTO_INCREMENT PRIMARY KEY,
    id_chauffeur            INT NOT NULL,
    type                    ENUM('permis','assurance','carte_vtc','agrement_pmr','autre') NOT NULL,
    chemin_fichier          VARCHAR(255), -- NULL tant que le document n'est pas déposé
    statut                  ENUM('a_deposer','en_attente','valide','refuse') NOT NULL DEFAULT 'a_deposer',
    commentaire_validation  TEXT,
    date_expiration         DATE,
    depose_le               DATETIME,
    valide_le               DATETIME,
    FOREIGN KEY (id_chauffeur) REFERENCES chauffeur(id_utilisateur)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 3. Formation des chauffeurs (UC76)
-- ------------------------------------------------------------
CREATE TABLE module_formation (
    id_module      INT AUTO_INCREMENT PRIMARY KEY,
    titre          VARCHAR(150) NOT NULL,
    description    TEXT,
    ordre          TINYINT NOT NULL UNIQUE,
    duree_minutes  SMALLINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE progression_formation (
    id_chauffeur  INT NOT NULL,
    id_module     INT NOT NULL,
    statut        ENUM('non_commence','en_cours','termine') NOT NULL DEFAULT 'non_commence',
    pourcentage   TINYINT NOT NULL DEFAULT 0,
    commence_le   DATETIME,
    termine_le    DATETIME,
    PRIMARY KEY (id_chauffeur, id_module),
    FOREIGN KEY (id_chauffeur) REFERENCES chauffeur(id_utilisateur),
    FOREIGN KEY (id_module)    REFERENCES module_formation(id_module),
    CONSTRAINT chk_progression_pourcentage CHECK (pourcentage BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 4. Impact social (UC74)
-- ------------------------------------------------------------
ALTER TABLE chauffeur
    ADD COLUMN en_parcours_insertion BOOLEAN NOT NULL DEFAULT FALSE;


-- ============================================================
-- DONNÉES DE TEST (fictives, RGPD)
-- ============================================================
-- David : le référent des données factices de l'API
-- (BACKEND/app/repository/user_repository.py), mot de passe Trajet-2026!

INSERT INTO structure_partenaire (id_structure, nom, type, statut, cree_le) VALUES
(1, 'Association fictive', 'association', 'active', '2026-10-01 12:00:00');

INSERT INTO utilisateur (id_utilisateur, code_role, statut, prenom, nom, telephone, mot_de_passe_hash, cree_le) VALUES
(4, 'partner', 'actif', 'David', 'Démo', '+594694000004',
 'scrypt:32768:8:1$LlorBBmyFb00mWld$bd33a7acc5b00332e868ccd803b9d76652d3f3676d9f4138812f6c889738e4998842f78a18a3c64c39dd7b7d7524cfc4ed8bf6d40f3007d2e6cae0283cee685f',
 '2026-10-01 12:00:00');

INSERT INTO referent (id_utilisateur, id_structure) VALUES
(4, 1);

INSERT INTO bon_solidaire (code, id_structure, id_emis_par, id_beneficiaire, pourcentage_prise_en_charge, nb_courses_max, nb_courses_utilisees, valide_du, valide_au, statut, cree_le) VALUES
('SOL-4F7K2Q9M', 1, 4, NULL, 50,  10, 0, '2026-10-01', '2026-12-31', 'actif', '2026-10-01 12:00:00'),
('SOL-8H3N6R2T', 1, 4, 2,    100, 5,  0, '2026-10-01', '2026-12-31', 'actif', '2026-10-01 12:00:00');

INSERT INTO module_formation (titre, description, ordre, duree_minutes) VALUES
('Sécurité routière',             'Règles de sécurité et bonnes pratiques de conduite.',                1, 30),
('Relation usager',               'Accueil, communication et accompagnement des publics prioritaires.', 2, 25),
('Utilisation de l''application', 'Prise en main de l''outil chauffeur : courses, statuts.',            3, 20);
