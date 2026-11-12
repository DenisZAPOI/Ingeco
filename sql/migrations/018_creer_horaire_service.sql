-- 018 : table horaire_service (horaires autorisés pour les demandes de trajet)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #51 (cahier des charges §5 M9 et §18, P1)
-- Retour arrière : DROP TABLE horaire_service;
--
-- Les plages pendant lesquelles on peut demander un trajet, réglables par
-- l'administrateur. Une demande hors plage est refusée AVEC une
-- explication en langage simple (§18) : c'est l'API qui la donne.
--
-- HEURE LOCALE DE CAYENNE (America/Cayenne, UTC-3 toute l'année),
-- contrairement aux DATETIME du reste du schéma, qui sont en UTC : un
-- horaire d'ouverture se pense en heure locale. L'API convertit l'heure de
-- la demande avant de comparer.
--
-- Une ou plusieurs plages par jour (pause de midi possible) ; aucune ligne
-- pour un jour = fermé ce jour-là. Bornes incluses : une demande est
-- acceptée si ouvre_a <= heure locale <= ferme_a, d'où 23:59:59 pour
-- « jusqu'à minuit ». Deux plages d'un même jour ne doivent pas se
-- chevaucher : l'unicité empêche seulement deux plages qui commencent à la
-- même heure ; le reste est vérifié par l'API à l'enregistrement.
--
-- Valeur PROVISOIRE (docs/decisions.md, point A, en attente de la
-- cliente) : ouvert tous les jours, toute la journée. Le mécanisme existe,
-- la valeur ne bloque rien.

CREATE TABLE horaire_service (
    id_horaire    INT AUTO_INCREMENT PRIMARY KEY,
    jour_semaine  TINYINT NOT NULL,  -- 1 = lundi … 7 = dimanche (ISO 8601)
    ouvre_a       TIME NOT NULL,
    ferme_a       TIME NOT NULL,
    UNIQUE (jour_semaine, ouvre_a),
    CONSTRAINT chk_horaire_service_jour  CHECK (jour_semaine BETWEEN 1 AND 7),
    CONSTRAINT chk_horaire_service_plage CHECK (ouvre_a < ferme_a)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO horaire_service (jour_semaine, ouvre_a, ferme_a) VALUES
(1, '00:00:00', '23:59:59'),
(2, '00:00:00', '23:59:59'),
(3, '00:00:00', '23:59:59'),
(4, '00:00:00', '23:59:59'),
(5, '00:00:00', '23:59:59'),
(6, '00:00:00', '23:59:59'),
(7, '00:00:00', '23:59:59');
