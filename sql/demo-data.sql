-- ============================================================
-- En route pour l'emploi : données de TEST, développement local seulement
-- ============================================================
-- À lancer APRÈS schema-mvp.sql. Chargé par compose.yaml (base locale) ;
-- JAMAIS en production : ces comptes ont un mot de passe public (README),
-- dont un administrateur. L'API, elle, ne charge ses comptes de test que
-- si LOAD_DEMO_DATA=true.
-- ============================================================

SET NAMES utf8mb4;

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
