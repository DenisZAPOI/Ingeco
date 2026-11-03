-- 005 : vue v_stats_courses_par_motif (tableau de bord administrateur)
-- 03/11/2026, Kurtys TSHIBOLA (équipe BD), issue #23 (UC56, contrat 6.4)
-- Retour arrière : DROP VIEW v_stats_courses_par_motif;
--
-- Une ligne par jour (heure de Guyane) et par motif du trajet. Même usage
-- que 004 :
--   SELECT motif, SUM(nb_demandes) FROM v_stats_courses_par_motif
--   WHERE jour BETWEEN :du AND :au GROUP BY motif;
-- La vue ne cite aucun motif : si leur liste change (le cahier des charges
-- parle d'entretien, de formation, de premier mois d'emploi, de démarche),
-- elle suit sans être modifiée.
--
-- Propre à MySQL : CONVERT_TZ (voir 003).

CREATE VIEW v_stats_courses_par_motif AS
SELECT
    DATE(CONVERT_TZ(cree_le, '+00:00', '-03:00'))                         AS jour,
    motif,
    COUNT(*)                                                              AS nb_demandes,
    SUM(CASE WHEN statut = 'terminee' THEN 1 ELSE 0 END)                  AS nb_terminees
FROM course
GROUP BY DATE(CONVERT_TZ(cree_le, '+00:00', '-03:00')), motif;
