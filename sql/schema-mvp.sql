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


-- ============================================================
-- DONNÉES DE TEST (fictives, RGPD)
-- ============================================================
-- Mêmes comptes que les données factices de l'API
-- (BACKEND/app/repository/user_repository.py) et le README, partie
-- « Comptes de test » :
--   - mot de passe de tous les comptes activés : Trajet-2026!
--   - code d'activation de Gaëlle : 12345678
-- Hachages scrypt générés par BACKEND/app/utils/passwords.py.
-- Le compte David (référent partenaire) est dans schema-hors-scope.sql.
--
-- En production, seul le premier administrateur est créé, SANS mot de
-- passe ni code : il s'active avec un code généré à la main (contrat 2).

SET @mdp  = 'scrypt:32768:8:1$LlorBBmyFb00mWld$bd33a7acc5b00332e868ccd803b9d76652d3f3676d9f4138812f6c889738e4998842f78a18a3c64c39dd7b7d7524cfc4ed8bf6d40f3007d2e6cae0283cee685f';
SET @code = 'scrypt:32768:8:1$AAFT8bnFcgzpQN95$7e5dce4e3b7069dd0e89fc40434e04f0d8c7869ea30e89ad83e24281e27bf751f2f5e1b016ac1c643864da7baafcd51eab32596832eb52185d7e1c10335f7ed6';

INSERT INTO utilisateur (id_utilisateur, code_role, statut, prenom, nom, telephone, mot_de_passe_hash, code_activation_hash, code_activation_expire_le, cree_le) VALUES
(1, 'rider',    'actif',    'Alice',  'Démo', '+594694000001', @mdp, NULL,  NULL,                  '2026-10-01 12:00:00'),
(2, 'rider',    'actif',    'Bruno',  'Démo', '+594694000002', @mdp, NULL,  NULL,                  '2026-10-01 12:00:00'),
(3, 'driver',   'actif',    'Chloé',  'Démo', '+594694000003', @mdp, NULL,  NULL,                  '2026-10-01 12:00:00'),
(5, 'operator', 'actif',    'Emma',   'Démo', '+594694000005', @mdp, NULL,  NULL,                  '2026-10-01 12:00:00'),
(6, 'admin',    'actif',    'Farid',  'Démo', '+594694000006', @mdp, NULL,  NULL,                  '2026-10-01 12:00:00'),
-- Créée par le centre d'appel : pas encore de mot de passe
(7, 'rider',    'actif',    'Gaëlle', 'Démo', '+594694000007', NULL, @code, '2027-12-31 12:00:00', '2026-10-01 12:00:00'),
(8, 'rider',    'suspendu', 'Hugo',   'Démo', '+594694000008', @mdp, NULL,  NULL,                  '2026-10-01 12:00:00'),
-- Second chauffeur, sans véhicule accessible
(9, 'driver',   'actif',    'Inès',   'Démo', '+594694000009', @mdp, NULL,  NULL,                  '2026-10-01 12:00:00');

INSERT INTO usager (id_utilisateur, est_prioritaire, besoin_vehicule_accessible) VALUES
(1, FALSE, FALSE),
(2, TRUE,  TRUE),
(7, FALSE, FALSE),
(8, FALSE, FALSE);

INSERT INTO chauffeur (id_utilisateur, est_disponible, derniere_lat, derniere_lng, derniere_position_le) VALUES
(3, TRUE,  4.937200, -52.326000, '2026-10-20 12:00:00'),
(9, FALSE, NULL,     NULL,       NULL);

INSERT INTO vehicule (id_chauffeur, immatriculation, modele, nombre_places, est_accessible) VALUES
(3, 'AA-001-AA', 'Véhicule fictif', 4, TRUE),
(9, 'AA-002-AA', 'Véhicule fictif', 4, FALSE);

-- Une course par statut utile aux écrans. Adresses fictives.
INSERT INTO course (
    id_course, id_requete_client, id_usager, id_chauffeur, id_saisie_par, canal, statut, motif,
    adresse_depart, lat_depart, lng_depart, id_commune_depart,
    adresse_arrivee, lat_arrivee, lng_arrivee, id_commune_arrivee,
    prevue_le, besoin_vehicule_accessible, distance_km, id_tarif, prix_centimes,
    statut_paiement, expire_le, cree_le, payee_le, acceptee_le, demarree_le, terminee_le,
    annulee_le, expiree_le, id_annulee_par
) VALUES
-- Terminée et évaluée
(1, '00000000-0000-4000-8000-000000000001', 1, 3, 1, 'application', 'terminee', 'emploi',
 '1 rue Fictive, Cayenne', 4.937200, -52.326000, 1,
 'Agence fictive, Cayenne', 4.931000, -52.318000, 1,
 NULL, FALSE, 3.20, 1, 1056,
 'paye', '2026-10-15 12:15:30', '2026-10-15 12:00:00', '2026-10-15 12:00:30', '2026-10-15 12:02:00', '2026-10-15 12:10:00', '2026-10-15 12:22:00',
 NULL, NULL, NULL),
-- Programmée, réservée par téléphone, payée, en attente d'un chauffeur
(2, '00000000-0000-4000-8000-000000000002', 2, NULL, 5, 'telephone', 'en_attente', 'sante',
 '2 rue Fictive, Matoury', 4.847000, -52.331000, 3,
 'Centre de santé fictif, Cayenne', 4.935000, -52.330000, 1,
 '2026-11-05 13:00:00', TRUE, 11.40, 1, 1712,
 'paye', '2026-11-05 13:00:00', '2026-10-20 11:00:00', '2026-10-20 11:05:00', NULL, NULL, NULL,
 NULL, NULL, NULL),
-- Réservée, pas encore payée
(3, '00000000-0000-4000-8000-000000000003', 1, NULL, 1, 'application', 'attente_paiement', 'formation',
 '1 rue Fictive, Cayenne', 4.937200, -52.326000, 1,
 'Organisme de formation fictif, Rémire-Montjoly', 4.917000, -52.276000, 2,
 '2026-11-06 11:30:00', FALSE, 7.80, 1, 1424,
 'en_attente', '2026-10-20 12:15:00', '2026-10-20 12:00:00', NULL, NULL, NULL, NULL,
 NULL, NULL, NULL),
-- Expirée sans chauffeur, remboursée
(4, '00000000-0000-4000-8000-000000000004', 1, NULL, 1, 'application', 'expiree', 'demarche_administrative',
 '1 rue Fictive, Cayenne', 4.937200, -52.326000, 1,
 'Administration fictive, Cayenne', 4.939000, -52.333000, 1,
 NULL, FALSE, 1.50, 1, 920,
 'rembourse', '2026-10-18 12:16:00', '2026-10-18 12:00:00', '2026-10-18 12:01:00', NULL, NULL, NULL,
 NULL, '2026-10-18 12:16:00', NULL),
-- Annulée par l'usager après paiement, remboursée
(5, '00000000-0000-4000-8000-000000000005', 2, NULL, 2, 'application', 'annulee', 'autre',
 '2 rue Fictive, Matoury', 4.847000, -52.331000, 3,
 '3 rue Fictive, Matoury', 4.851000, -52.336000, 3,
 NULL, TRUE, 1.10, 1, 888,
 'rembourse', '2026-10-19 12:15:30', '2026-10-19 12:00:00', '2026-10-19 12:00:30', NULL, NULL, NULL,
 '2026-10-19 12:05:00', NULL, 2);

INSERT INTO evaluation (id_course, note, commentaire, cree_le) VALUES
(1, 5, 'Trajet ponctuel.', '2026-10-15 12:30:00');
