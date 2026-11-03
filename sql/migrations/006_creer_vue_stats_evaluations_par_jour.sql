-- 006 : vue v_stats_evaluations_par_jour (note moyenne, satisfaction)
-- 03/11/2026, Kurtys TSHIBOLA (équipe BD), issue #23 (UC56, contrat 6.4)
-- Retour arrière : DROP VIEW v_stats_evaluations_par_jour;
--
-- Une ligne par jour d'évaluation (heure de Guyane). La vue donne des
-- sommes et non des moyennes : la moyenne d'une période ne s'obtient pas
-- en faisant la moyenne des moyennes de chaque jour. Sur une période :
--   note moyenne         = SUM(somme_notes) / SUM(nb_evaluations)
--   taux de satisfaction = SUM(nb_notes_4_ou_5) / SUM(nb_evaluations)
-- (objectif de la cliente : plus de 90 % de notes à 4 ou 5 sur 5).
-- Sans évaluation sur la période, SUM(nb_evaluations) est NULL : afficher
-- « pas encore de note », pas 0.
--
-- Propre à MySQL : CONVERT_TZ (voir 003).

CREATE VIEW v_stats_evaluations_par_jour AS
SELECT
    DATE(CONVERT_TZ(cree_le, '+00:00', '-03:00'))                         AS jour,
    COUNT(*)                                                              AS nb_evaluations,
    SUM(note)                                                             AS somme_notes,
    SUM(CASE WHEN note >= 4 THEN 1 ELSE 0 END)                            AS nb_notes_4_ou_5
FROM evaluation
GROUP BY DATE(CONVERT_TZ(cree_le, '+00:00', '-03:00'));
