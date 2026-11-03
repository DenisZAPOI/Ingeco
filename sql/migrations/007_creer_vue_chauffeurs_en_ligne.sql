-- 007 : vue v_chauffeur_en_ligne (chauffeurs à qui proposer une course)
-- 03/11/2026, Kurtys TSHIBOLA (équipe BD), issue #24 (contrat 6.1)
-- Retour arrière : DROP VIEW v_chauffeur_en_ligne;
--
-- Les chauffeurs au compte actif, en ligne, avec une position connue, et
-- ce qu'il faut pour choisir à qui proposer une course immédiate. Une vue
-- ne prend pas de paramètre : le point de départ, l'âge maximal de la
-- position (5 min), le rayon (10 km) et la fenêtre de 60 min restent des
-- réglages de l'API, appliqués dans la requête qui lit la vue.
--
-- Course active (contrat 3.3) : une course en_cours, ou acceptee
-- immédiate, donne a_course_en_cours = 1. Pour les courses acceptées
-- programmées, la vue donne la plus proche (prochaine_course_prevue_le) :
-- elle rend le chauffeur indisponible si elle tombe dans les 60 prochaines
-- minutes, ou si son heure est passée sans que le trajet ait démarré.
--
-- La vue est en SQL standard (CASE, EXISTS, sous-requêtes) : elle se crée
-- aussi sous SQLite. La distance est propre à MySQL : ST_Distance_Sphere,
-- en mètres, sur POINT(longitude, latitude). Requête de l'API sous MySQL :
--
--   SELECT id_chauffeur,
--          ST_Distance_Sphere(POINT(derniere_lng, derniere_lat),
--                             POINT(:lng_depart, :lat_depart)) / 1000 AS distance_km
--   FROM v_chauffeur_en_ligne
--   WHERE derniere_position_le >= :position_recente_depuis   -- maintenant - 5 min
--     AND a_course_en_cours = 0
--     AND (prochaine_course_prevue_le IS NULL
--          OR prochaine_course_prevue_le > :maintenant_plus_60_min)
--     AND (:besoin_vehicule_accessible = 0 OR est_accessible = 1)
--   HAVING distance_km <= :rayon_km
--   ORDER BY distance_km;
--
-- Sous SQLite (tests), l'API garde son calcul en Python sur derniere_lat et
-- derniere_lng. Pas de colonne ni d'index spatial : avec 15 à 20
-- chauffeurs, lire toute la vue coûte moins qu'un index à tenir à jour à
-- chaque position envoyée.

CREATE VIEW v_chauffeur_en_ligne AS
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
          AND (c.statut = 'en_cours' OR (c.statut = 'acceptee' AND c.prevue_le IS NULL))
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
