-- ============================================================
-- En route pour l'emploi : données de TEST, développement local seulement
-- ============================================================
-- À lancer APRÈS schema-mvp.sql et les migrations. Chargé par compose.yaml
-- (base locale) et par les tests de l'API (BACKEND/tests/mysql_setup.py).
-- JAMAIS en production : ces comptes ont un mot de passe public (README),
-- dont un administrateur.
--
-- Écrit par les développeurs depuis le 12/11/2026 (le schéma et les
-- migrations restent à l'équipe BD). C'est la seule source des comptes et
-- des courses de test : l'API n'en crée plus elle-même.
--
-- REJOUABLE : il commence par effacer toutes les lignes écrites par l'API,
-- puis remet la démo dans son état de départ, dates comprises. Sert au
-- premier démarrage de la base, à la remise à zéro (README, « Remettre la
-- démo à zéro ») et avant chaque test. Les données de référence (rôles,
-- communes, tarif) ne sont pas touchées.
-- ============================================================

SET NAMES utf8mb4;

-- ============================================================
-- EFFACER LA DÉMO PRÉCÉDENTE
-- ============================================================
-- Les tables filles d'abord (clés étrangères). Une nouvelle table où l'API
-- écrit s'ajoute ici, à sa place dans cet ordre.
DELETE FROM evaluation;
DELETE FROM course;
DELETE FROM demande_suppression;
DELETE FROM vehicule;
DELETE FROM chauffeur;
DELETE FROM usager;
DELETE FROM utilisateur;

-- ============================================================
-- DONNÉES DE TEST (fictives, RGPD)
-- ============================================================
-- Les comptes du README, partie « Comptes de test » :
--   - mot de passe de tous les comptes activés : Trajet-2026!
--   - code d'activation de Gaëlle : 12345678
-- Hachages scrypt générés par BACKEND/app/utils/passwords.py.
--
-- Les dates sont calculées au chargement (issue #45) : la démo reste à jour
-- quel que soit le jour où la base est créée.

SET @mdp  = 'scrypt:32768:8:1$LlorBBmyFb00mWld$bd33a7acc5b00332e868ccd803b9d76652d3f3676d9f4138812f6c889738e4998842f78a18a3c64c39dd7b7d7524cfc4ed8bf6d40f3007d2e6cae0283cee685f';
SET @code = 'scrypt:32768:8:1$AAFT8bnFcgzpQN95$7e5dce4e3b7069dd0e89fc40434e04f0d8c7869ea30e89ad83e24281e27bf751f2f5e1b016ac1c643864da7baafcd51eab32596832eb52185d7e1c10335f7ed6';
SET @maintenant = UTC_TIMESTAMP();
SET @inscrit_le = @maintenant - INTERVAL 30 DAY;

INSERT INTO utilisateur (id_utilisateur, code_role, statut, prenom, nom, telephone, mot_de_passe_hash, code_activation_hash, code_activation_expire_le, cree_le) VALUES
(1, 'rider',    'actif',    'Alice',  'Démo', '+594694000001', @mdp, NULL,  NULL,                           @inscrit_le),
(2, 'rider',    'actif',    'Bruno',  'Démo', '+594694000002', @mdp, NULL,  NULL,                           @inscrit_le),
(3, 'driver',   'actif',    'Chloé',  'Démo', '+594694000003', @mdp, NULL,  NULL,                           @inscrit_le),
-- Référent partenaire (rôle de la migration 008). Sa structure viendra
-- avec les bons solidaires (schema-hors-scope.sql, après la soutenance).
(4, 'partner',  'actif',    'David',  'Démo', '+594694000004', @mdp, NULL,  NULL,                           @inscrit_le),
(5, 'operator', 'actif',    'Emma',   'Démo', '+594694000005', @mdp, NULL,  NULL,                           @inscrit_le),
(6, 'admin',    'actif',    'Farid',  'Démo', '+594694000006', @mdp, NULL,  NULL,                           @inscrit_le),
-- Créée par le centre d'appel : pas encore de mot de passe
(7, 'rider',    'actif',    'Gaëlle', 'Démo', '+594694000007', NULL, @code, @maintenant + INTERVAL 1 YEAR, @inscrit_le),
(8, 'rider',    'suspendu', 'Hugo',   'Démo', '+594694000008', @mdp, NULL,  NULL,                           @inscrit_le),
-- Second chauffeur, sans véhicule accessible
(9, 'driver',   'actif',    'Inès',   'Démo', '+594694000009', @mdp, NULL,  NULL,                           @inscrit_le);

INSERT INTO usager (id_utilisateur, est_prioritaire, besoin_vehicule_accessible) VALUES
(1, FALSE, FALSE),
(2, TRUE,  TRUE),
(7, FALSE, FALSE),
(8, FALSE, FALSE);

-- Chloé est hors ligne : elle se met en ligne depuis l'application, qui
-- envoie alors sa position.
INSERT INTO chauffeur (id_utilisateur, est_disponible, derniere_lat, derniere_lng, derniere_position_le) VALUES
(3, FALSE, NULL, NULL, NULL),
(9, FALSE, NULL, NULL, NULL);

INSERT INTO vehicule (id_chauffeur, immatriculation, modele, nombre_places, est_accessible) VALUES
(3, 'AA-001-AA', 'Véhicule fictif', 4, TRUE),
(9, 'AA-002-AA', 'Véhicule fictif', 4, FALSE);

-- ============================================================
-- Courses : une par statut utile aux écrans
-- ============================================================
-- Lieux publics (mairies) ou adresses fictives. Prix du tarif provisoire :
-- 800 + 80 × distance, en centimes.

-- Dates de création, du plus ancien au plus récent
SET @course_1 = @maintenant - INTERVAL 10 DAY;
SET @course_4 = @maintenant - INTERVAL 8 DAY;
SET @course_5 = @maintenant - INTERVAL 6 DAY;
SET @course_6 = @maintenant - INTERVAL 2 DAY;
SET @course_7 = @maintenant - INTERVAL 1 DAY;
SET @course_2 = @maintenant - INTERVAL 1 DAY;
-- Récente : elle expire 15 minutes après sa création si personne ne paie
SET @course_3 = @maintenant - INTERVAL 2 MINUTE;
-- Rendez-vous programmés
SET @prevue_2 = @maintenant + INTERVAL 2 DAY;
SET @prevue_3 = @maintenant + INTERVAL 3 DAY;

INSERT INTO course (
    id_course, id_requete_client, id_usager, id_chauffeur, id_saisie_par, canal, statut, motif,
    adresse_depart, lat_depart, lng_depart, id_commune_depart,
    adresse_arrivee, lat_arrivee, lng_arrivee, id_commune_arrivee,
    prevue_le, besoin_vehicule_accessible, distance_km, id_tarif, prix_centimes,
    statut_paiement, expire_le, cree_le, payee_le, acceptee_le, demarree_le, terminee_le,
    annulee_le, expiree_le, id_annulee_par
) VALUES
-- 1. Terminée et évaluée
(1, '00000000-0000-4000-8000-000000000001', 1, 3, 1, 'application', 'terminee', 'emploi',
 'Mairie de Cayenne', 4.937200, -52.326000, 1,
 'Mairie de Matoury', 4.847000, -52.331000, 3,
 NULL, FALSE, 13.10, 1, 1848,
 'paye', @course_1 + INTERVAL 15 MINUTE, @course_1, @course_1,
 @course_1 + INTERVAL 2 MINUTE, @course_1 + INTERVAL 10 MINUTE, @course_1 + INTERVAL 35 MINUTE,
 NULL, NULL, NULL),
-- 2. Programmée, réservée par téléphone (Emma), payée, en attente d'un chauffeur
(2, '00000000-0000-4000-8000-000000000002', 2, NULL, 5, 'telephone', 'en_attente', 'sante',
 '2 rue Fictive, Matoury', 4.847000, -52.331000, 3,
 'Centre de santé fictif, Cayenne', 4.935000, -52.330000, 1,
 @prevue_2, TRUE, 11.40, 1, 1712,
 'paye', @prevue_2, @course_2, @course_2 + INTERVAL 5 MINUTE, NULL, NULL, NULL,
 NULL, NULL, NULL),
-- 3. Programmée, pas encore payée
(3, '00000000-0000-4000-8000-000000000003', 1, NULL, 1, 'application', 'attente_paiement', 'formation',
 '1 rue Fictive, Cayenne', 4.937200, -52.326000, 1,
 'Organisme de formation fictif, Rémire-Montjoly', 4.917000, -52.276000, 2,
 @prevue_3, FALSE, 7.80, 1, 1424,
 'en_attente', @course_3 + INTERVAL 15 MINUTE, @course_3, NULL, NULL, NULL, NULL,
 NULL, NULL, NULL),
-- 4. Expirée sans chauffeur, remboursée
(4, '00000000-0000-4000-8000-000000000004', 1, NULL, 1, 'application', 'expiree', 'demarche_administrative',
 '1 rue Fictive, Cayenne', 4.937200, -52.326000, 1,
 'Administration fictive, Cayenne', 4.939000, -52.333000, 1,
 NULL, FALSE, 1.50, 1, 920,
 'rembourse', @course_4 + INTERVAL 16 MINUTE, @course_4, @course_4 + INTERVAL 1 MINUTE, NULL, NULL, NULL,
 NULL, @course_4 + INTERVAL 16 MINUTE, NULL),
-- 5. Annulée par l'usagère après paiement, remboursée
(5, '00000000-0000-4000-8000-000000000005', 1, NULL, 1, 'application', 'annulee', 'demarche_administrative',
 'Mairie de Cayenne', 4.937200, -52.326000, 1,
 'Mairie de Matoury', 4.847000, -52.331000, 3,
 NULL, FALSE, 13.10, 1, 1848,
 'rembourse', @course_5 + INTERVAL 15 MINUTE, @course_5, @course_5, NULL, NULL, NULL,
 @course_5 + INTERVAL 5 MINUTE, NULL, 1),
-- 6. Terminée, pas encore évaluée
(6, '00000000-0000-4000-8000-000000000006', 1, 3, 1, 'application', 'terminee', 'sante',
 'Mairie de Cayenne', 4.937200, -52.326000, 1,
 'Mairie de Matoury', 4.847000, -52.331000, 3,
 NULL, FALSE, 13.10, 1, 1848,
 'paye', @course_6 + INTERVAL 15 MINUTE, @course_6, @course_6,
 @course_6 + INTERVAL 2 MINUTE, @course_6 + INTERVAL 10 MINUTE, @course_6 + INTERVAL 35 MINUTE,
 NULL, NULL, NULL),
-- 7. Terminée, pas encore évaluée
(7, '00000000-0000-4000-8000-000000000007', 1, 3, 1, 'application', 'terminee', 'formation',
 'Mairie de Cayenne', 4.937200, -52.326000, 1,
 'Mairie de Matoury', 4.847000, -52.331000, 3,
 NULL, FALSE, 13.10, 1, 1848,
 'paye', @course_7 + INTERVAL 15 MINUTE, @course_7, @course_7,
 @course_7 + INTERVAL 2 MINUTE, @course_7 + INTERVAL 10 MINUTE, @course_7 + INTERVAL 35 MINUTE,
 NULL, NULL, NULL);

INSERT INTO evaluation (id_course, note, commentaire, cree_le) VALUES
(1, 5, 'Trajet ponctuel.', @course_1 + INTERVAL 35 MINUTE);
