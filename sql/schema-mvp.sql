-- ============================================================
-- En route pour l'emploi : schéma de la base, périmètre MVP
-- ============================================================
-- Version 2 (20/10/2026). Remplace la première version, écrite avant le
-- contrat d'API v2 (docs/contrat-api.md), dont elle suit les parties 3 et 6.
--
-- SGBD : MySQL 8.0.16 ou plus récent (les CHECK ne sont appliqués qu'à
-- partir de cette version), moteur InnoDB (transactions, voir contrat 6.2).
-- Choix de l'équipe BD, à confirmer.
--
-- Conventions :
--   - dates-heures en UTC (DATETIME sans fuseau) : l'API fournit toujours
--     la valeur, d'où l'absence de DEFAULT CURRENT_TIMESTAMP, qui suivrait
--     le fuseau de la session MySQL ;
--   - montants en centimes d'euro, entiers ;
--   - positions en degrés décimaux (WGS 84), 6 décimales (~10 cm) ;
--   - aucune suppression physique : on change un statut.
--
-- Hors de ce fichier : bons solidaires, structures partenaires et autres
-- éléments hors MVP, dans schema-hors-scope.sql (à lancer APRÈS celui-ci).
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Réinitialisation pour relancer le script en développement. Les tables de
-- schema-hors-scope.sql sont aussi supprimées : elles dépendent des tables
-- ci-dessous, et devront être recréées après.
DROP TABLE IF EXISTS progression_formation;
DROP TABLE IF EXISTS module_formation;
DROP TABLE IF EXISTS document_chauffeur;
DROP TABLE IF EXISTS bon_solidaire;
DROP TABLE IF EXISTS referent;
DROP TABLE IF EXISTS structure_partenaire;
DROP TABLE IF EXISTS evaluation;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS tarif;
DROP TABLE IF EXISTS vehicule;
DROP TABLE IF EXISTS chauffeur;
DROP TABLE IF EXISTS usager;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS commune;
DROP TABLE IF EXISTS role;

SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- 1. role : données de référence (contrat 2)
-- ------------------------------------------------------------
-- Une table plutôt qu'un ENUM : ajouter un rôle (partner, dans
-- schema-hors-scope.sql) est un simple INSERT.
CREATE TABLE role (
    code     VARCHAR(20)  PRIMARY KEY,  -- rider | driver | operator | admin
    libelle  VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 2. commune : communes desservies (contrat 3.6, H18)
-- ------------------------------------------------------------
-- Seules les communes de cette table sont desservies : départ et arrivée
-- d'une course doivent en faire partie. Ajouter Kourou = un INSERT.
CREATE TABLE commune (
    id_commune  INT AUTO_INCREMENT PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 3. utilisateur : compte commun à tous les rôles (contrat 3.1)
-- ------------------------------------------------------------
CREATE TABLE utilisateur (
    id_utilisateur             INT AUTO_INCREMENT PRIMARY KEY,
    code_role                  VARCHAR(20)  NOT NULL,
    statut                     ENUM('actif','suspendu') NOT NULL DEFAULT 'actif',
    prenom                     VARCHAR(100) NOT NULL,
    nom                        VARCHAR(100) NOT NULL,
    -- Identifiant de connexion, au format international (+594...)
    telephone                  VARCHAR(16)  NOT NULL UNIQUE,
    -- Facultatif ; UNIQUE accepte plusieurs NULL
    email                      VARCHAR(255) UNIQUE,
    -- NULL tant que le compte créé par un tiers n'est pas activé
    mot_de_passe_hash          VARCHAR(255),
    -- Code d'activation à usage unique (activation, mot de passe oublié)
    code_activation_hash       VARCHAR(255),
    code_activation_expire_le  DATETIME,
    cree_le                    DATETIME NOT NULL,
    FOREIGN KEY (code_role) REFERENCES role(code),
    CONSTRAINT chk_utilisateur_telephone CHECK (telephone REGEXP '^[+][0-9]{8,15}$'),
    CONSTRAINT chk_utilisateur_email     CHECK (email IS NULL OR email <> ''),
    CONSTRAINT chk_utilisateur_code      CHECK ((code_activation_hash IS NULL) = (code_activation_expire_le IS NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Recherche de l'opérateur et de l'administrateur par nom (contrat 4.5, 4.6)
CREATE INDEX idx_utilisateur_nom ON utilisateur(nom, prenom);
CREATE INDEX idx_utilisateur_role ON utilisateur(code_role, statut);

-- ------------------------------------------------------------
-- 4. usager : informations propres au rôle rider
-- ------------------------------------------------------------
CREATE TABLE usager (
    id_utilisateur              INT PRIMARY KEY,
    -- Usager prioritaire : un attribut, pas un rôle (H2). Aucun effet
    -- automatique dans le MVP (H15)
    est_prioritaire             BOOLEAN NOT NULL DEFAULT FALSE,
    besoin_vehicule_accessible  BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 5. chauffeur : informations propres au rôle driver
-- ------------------------------------------------------------
-- Compte créé par un administrateur après vérification des documents en
-- personne : aucun numéro de permis ni document stocké (minimisation RGPD).
CREATE TABLE chauffeur (
    id_utilisateur        INT PRIMARY KEY,
    est_disponible        BOOLEAN NOT NULL DEFAULT FALSE,
    -- Dernière position connue seulement, pas d'historique (H6). Remise à
    -- NULL quand le chauffeur passe hors ligne
    derniere_lat          DECIMAL(9,6),
    derniere_lng          DECIMAL(9,6),
    derniere_position_le  DATETIME,
    -- Photo du visage, réduite par l'API (~15 Ko) avant écriture (H19).
    -- Stockée en base : sauvegardée avec le reste, pas de serveur de fichiers
    photo                 BLOB,
    -- Sert à invalider le cache de la photo sur les téléphones
    photo_modifiee_le     DATETIME,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT chk_chauffeur_position CHECK (
        (derniere_lat IS NULL AND derniere_lng IS NULL AND derniere_position_le IS NULL)
        OR (derniere_lat IS NOT NULL AND derniere_lng IS NOT NULL AND derniere_position_le IS NOT NULL)
    ),
    CONSTRAINT chk_chauffeur_lat   CHECK (derniere_lat BETWEEN -90 AND 90),
    CONSTRAINT chk_chauffeur_lng   CHECK (derniere_lng BETWEEN -180 AND 180),
    CONSTRAINT chk_chauffeur_photo CHECK ((photo IS NULL) = (photo_modifiee_le IS NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chauffeurs disponibles autour d'un point (contrat 6.1) : filtre sur un
-- rectangle lat/lng, distance exacte calculée par l'API
CREATE INDEX idx_chauffeur_position ON chauffeur(est_disponible, derniere_lat, derniere_lng);

-- ------------------------------------------------------------
-- 6. vehicule : un seul par chauffeur dans le MVP (H5)
-- ------------------------------------------------------------
-- Table à part (plutôt que des colonnes du chauffeur) pour pouvoir passer
-- à plusieurs véhicules en retirant l'unicité sur id_chauffeur.
CREATE TABLE vehicule (
    id_vehicule      INT AUTO_INCREMENT PRIMARY KEY,
    id_chauffeur     INT NOT NULL UNIQUE,
    immatriculation  VARCHAR(20)  NOT NULL UNIQUE,
    modele           VARCHAR(100) NOT NULL, -- marque et modèle, tels qu'affichés au passager
    nombre_places    TINYINT NOT NULL,
    est_accessible   BOOLEAN NOT NULL DEFAULT FALSE, -- fauteuil roulant
    FOREIGN KEY (id_chauffeur) REFERENCES chauffeur(id_utilisateur),
    CONSTRAINT chk_vehicule_places CHECK (nombre_places BETWEEN 1 AND 8)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 7. tarif : un seul tarif actif dans le MVP (H8)
-- ------------------------------------------------------------
-- Les anciens tarifs restent (une course garde la référence du tarif qui a
-- servi à calculer son prix). Plusieurs tarifs actifs (par profil, par
-- financement) : hors MVP, il suffira de retirer la colonne tarif_actif.
CREATE TABLE tarif (
    id_tarif                  INT AUTO_INCREMENT PRIMARY KEY,
    prise_en_charge_centimes  INT NOT NULL,
    prix_km_centimes          INT NOT NULL,
    actif                     BOOLEAN NOT NULL,
    cree_le                   DATETIME NOT NULL,
    -- 1 si actif, NULL sinon : l'unicité n'autorise qu'un tarif actif
    tarif_actif               TINYINT GENERATED ALWAYS AS (IF(actif, 1, NULL)) STORED UNIQUE,
    CONSTRAINT chk_tarif_montants CHECK (prise_en_charge_centimes >= 0 AND prix_km_centimes >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 8. course (contrat 3.3)
-- ------------------------------------------------------------
-- Cycle de vie de statut :
--   attente_paiement --paiement--> en_attente --> acceptee --> en_cours --> terminee
--                                       ^------ désistement ----'
--   attente_paiement, en_attente           --> expiree   (délai dépassé, tâche de l'API)
--   attente_paiement, en_attente, acceptee --> annulee
-- Une course n'est proposée aux chauffeurs qu'en en_attente, donc payée.
--
-- Montants : sans bon solidaire, la part de l'usager est le prix entier.
-- schema-hors-scope.sql ajoute la part du bon (part usager = prix - part bon).
CREATE TABLE course (
    id_course                   INT AUTO_INCREMENT PRIMARY KEY,
    -- UUID généré par l'appareil : une requête rejouée ne crée pas de
    -- doublon (contrat 6.7)
    id_requete_client           CHAR(36) NOT NULL UNIQUE,
    id_usager                   INT NOT NULL,
    -- NULL tant qu'aucun chauffeur n'a accepté, et de nouveau après un désistement
    id_chauffeur                INT,
    -- L'usager lui-même, ou l'opérateur qui a réservé à sa place
    id_saisie_par               INT NOT NULL,
    canal                       ENUM('application','telephone') NOT NULL,
    statut                      ENUM('attente_paiement','en_attente','acceptee','en_cours','terminee','annulee','expiree') NOT NULL,
    motif                       ENUM('emploi','formation','sante','demarche_administrative','autre') NOT NULL,

    adresse_depart              VARCHAR(255) NOT NULL,
    lat_depart                  DECIMAL(9,6) NOT NULL,
    lng_depart                  DECIMAL(9,6) NOT NULL,
    id_commune_depart           INT NOT NULL,
    adresse_arrivee             VARCHAR(255) NOT NULL,
    lat_arrivee                 DECIMAL(9,6) NOT NULL,
    lng_arrivee                 DECIMAL(9,6) NOT NULL,
    id_commune_arrivee          INT NOT NULL,

    -- NULL = course immédiate
    prevue_le                   DATETIME,
    -- Copié du profil de l'usager à la réservation
    besoin_vehicule_accessible  BOOLEAN NOT NULL,
    -- Distance par la route, calculée par l'API à la réservation (H13)
    distance_km                 DECIMAL(6,2) NOT NULL,
    -- Tarif qui a servi au calcul ; le prix est figé à la réservation
    id_tarif                    INT NOT NULL,
    prix_centimes               INT NOT NULL,

    -- Paiement simulé (H10) : un statut, pas de table de paiements
    statut_paiement             ENUM('non_requis','en_attente','paye','rembourse') NOT NULL,
    -- Au-delà, une course attente_paiement ou en_attente expire (contrat 6.8)
    expire_le                   DATETIME NOT NULL,

    -- Une date par changement d'état
    cree_le                     DATETIME NOT NULL,
    payee_le                    DATETIME,
    acceptee_le                 DATETIME, -- remise à NULL après un désistement
    demarree_le                 DATETIME,
    terminee_le                 DATETIME,
    annulee_le                  DATETIME,
    expiree_le                  DATETIME,
    id_annulee_par              INT,

    FOREIGN KEY (id_usager)          REFERENCES usager(id_utilisateur),
    FOREIGN KEY (id_chauffeur)       REFERENCES chauffeur(id_utilisateur),
    FOREIGN KEY (id_saisie_par)      REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY (id_commune_depart)  REFERENCES commune(id_commune),
    FOREIGN KEY (id_commune_arrivee) REFERENCES commune(id_commune),
    FOREIGN KEY (id_tarif)           REFERENCES tarif(id_tarif),
    FOREIGN KEY (id_annulee_par)     REFERENCES utilisateur(id_utilisateur),

    CONSTRAINT chk_course_positions CHECK (
        lat_depart  BETWEEN -90 AND 90 AND lng_depart  BETWEEN -180 AND 180
        AND lat_arrivee BETWEEN -90 AND 90 AND lng_arrivee BETWEEN -180 AND 180
    ),
    CONSTRAINT chk_course_montants CHECK (prix_centimes >= 0 AND distance_km >= 0),
    -- Un chauffeur si et seulement si la course est prise (contrat 6.5) ;
    -- une course annulée peut l'avoir été avant ou après l'acceptation
    CONSTRAINT chk_course_chauffeur CHECK (
        statut = 'annulee'
        OR (id_chauffeur IS NOT NULL) = (statut IN ('acceptee','en_cours','terminee'))
    ),
    CONSTRAINT chk_course_acceptee CHECK ((id_chauffeur IS NULL) = (acceptee_le IS NULL)),
    -- Pas d'impayé : une course proposée ou prise est payée ou sans part usager
    CONSTRAINT chk_course_paiement CHECK (
        statut NOT IN ('en_attente','acceptee','en_cours','terminee')
        OR statut_paiement IN ('paye','non_requis')
    ),
    CONSTRAINT chk_course_attente_paiement CHECK (
        statut <> 'attente_paiement' OR statut_paiement = 'en_attente'
    ),
    CONSTRAINT chk_course_payee_le CHECK (
        (payee_le IS NOT NULL) = (statut_paiement IN ('paye','rembourse'))
    ),
    CONSTRAINT chk_course_demarree CHECK (
        (demarree_le IS NOT NULL) = (statut IN ('en_cours','terminee'))
    ),
    CONSTRAINT chk_course_terminee CHECK ((terminee_le IS NOT NULL) = (statut = 'terminee')),
    CONSTRAINT chk_course_annulee  CHECK (
        (statut = 'annulee') = (annulee_le IS NOT NULL)
        AND (annulee_le IS NULL) = (id_annulee_par IS NULL)
    ),
    CONSTRAINT chk_course_expiree  CHECK ((expiree_le IS NOT NULL) = (statut = 'expiree'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Accès fréquents (contrat 6.6)
-- Tâche d'expiration, chaque minute : statut + échéance
CREATE INDEX idx_course_expiration ON course(statut, expire_le);
-- Courses proposées : immédiates, puis programmées triées par date
CREATE INDEX idx_course_statut_prevue ON course(statut, prevue_le);
-- Courses d'un usager, d'un chauffeur, les plus récentes d'abord
CREATE INDEX idx_course_usager ON course(id_usager, cree_le);
CREATE INDEX idx_course_chauffeur ON course(id_chauffeur, cree_le);
-- Statistiques sur une période (contrat 6.4)
CREATE INDEX idx_course_cree_le ON course(cree_le);

-- ------------------------------------------------------------
-- 9. evaluation : l'usager note le chauffeur (contrat 3.4)
-- ------------------------------------------------------------
-- Une seule évaluation par course : la course est la clé. L'auteur est
-- l'usager de la course, le chauffeur évalué celui de la course.
CREATE TABLE evaluation (
    id_course    INT PRIMARY KEY,
    note         TINYINT NOT NULL,
    commentaire  VARCHAR(500),
    cree_le      DATETIME NOT NULL,
    FOREIGN KEY (id_course) REFERENCES course(id_course),
    CONSTRAINT chk_evaluation_note CHECK (note BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_evaluation_cree_le ON evaluation(cree_le);


-- ============================================================
-- DONNÉES DE RÉFÉRENCE
-- ============================================================

INSERT INTO role (code, libelle) VALUES
('rider',    'Usager'),
('driver',   'Chauffeur'),
('operator', 'Opérateur du centre d''appel'),
('admin',    'Administrateur');

-- Zone du pilote (première visio). Kourou viendra ensuite.
INSERT INTO commune (id_commune, nom) VALUES
(1, 'Cayenne'),
(2, 'Rémire-Montjoly'),
(3, 'Matoury');

-- Montants PROVISOIRES, à faire fixer par la cliente
INSERT INTO tarif (id_tarif, prise_en_charge_centimes, prix_km_centimes, actif, cree_le) VALUES
(1, 800, 80, TRUE, '2026-10-01 12:00:00');

-- Les comptes et courses de test sont dans demo-data.sql, chargé en local
-- seulement (compose.yaml). En production, seul le premier administrateur
-- est créé, SANS mot de passe ni code : il s'active avec un code généré à
-- la main (contrat 2).
