-- 021 : v_chauffeur_en_ligne compte « chauffeur arrivé » comme une course en cours
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), suite de l'issue #54 (migration 020)
-- Retour arrière : rejouer le CREATE VIEW de la migration 007 avec CREATE OR REPLACE.
--
-- Un chauffeur arrivé au point de départ (statut chauffeur_arrive, migration
-- 020) attend son passager : il n'est pas libre pour une autre course,
-- qu'elle soit immédiate ou programmée. Seul a_course_en_cours change ;
-- les colonnes et la requête de l'API (en tête de la migration 007) restent
-- les mêmes.

CREATE OR REPLACE VIEW v_chauffeur_en_ligne AS
SELECT
    ch.id_utilisateur        AS id_chauffeur,
    ch.derniere_lat,
    ch.derniere_lng,
    ch.derniere_position_le,
    v.est_accessible,
    v.nombre_places,
    CASE WHEN EXISTS (
        SELECT 1 FROM course c
        WHERE c.id_chauffeur = ch.id_utilisateur
          AND (c.statut IN ('chauffeur_arrive', 'en_cours')
               OR (c.statut = 'acceptee' AND c.prevue_le IS NULL))
    ) THEN 1 ELSE 0 END      AS a_course_en_cours,
    (
        SELECT MIN(c.prevue_le) FROM course c
        WHERE c.id_chauffeur = ch.id_utilisateur
          AND c.statut = 'acceptee' AND c.prevue_le IS NOT NULL
    )                        AS prochaine_course_prevue_le
FROM chauffeur ch
JOIN utilisateur u ON u.id_utilisateur = ch.id_utilisateur
JOIN vehicule v    ON v.id_chauffeur   = ch.id_utilisateur
WHERE u.statut = 'actif'
  AND ch.est_disponible = TRUE
  AND ch.derniere_lat IS NOT NULL;
