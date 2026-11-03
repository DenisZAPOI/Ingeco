-- 004 : vue v_stats_courses_par_commune (tableau de bord administrateur)
-- 03/11/2026, Kurtys TSHIBOLA (équipe BD), issue #23 (UC56, contrat 6.4)
-- Retour arrière : DROP VIEW v_stats_courses_par_commune;
--
-- Une ligne par jour (heure de Guyane) et par commune de DÉPART. Le jour
-- reste dans la vue pour que l'API puisse filtrer une période :
--   SELECT id_commune, commune, SUM(nb_demandes) FROM v_stats_courses_par_commune
--   WHERE jour BETWEEN :du AND :au GROUP BY id_commune, commune;
-- Une commune sans aucune course n'apparaît pas : l'API complète à 0 avec
-- la liste des communes.
--
-- Propre à MySQL : CONVERT_TZ (voir 003).

CREATE VIEW v_stats_courses_par_commune AS
SELECT
    DATE(CONVERT_TZ(c.cree_le, '+00:00', '-03:00'))                       AS jour,
    m.id_commune                                                          AS id_commune,
    m.nom                                                                 AS commune,
    COUNT(*)                                                              AS nb_demandes,
    SUM(CASE WHEN c.statut = 'terminee' THEN 1 ELSE 0 END)                AS nb_terminees
FROM course c
JOIN commune m ON m.id_commune = c.id_commune_depart
GROUP BY DATE(CONVERT_TZ(c.cree_le, '+00:00', '-03:00')), m.id_commune, m.nom;
