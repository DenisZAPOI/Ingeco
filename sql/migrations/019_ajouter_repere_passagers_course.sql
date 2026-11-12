-- 019 : repère, nombre de passagers et bagages sur une course
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #53 (cahier des charges §7.4, P1)
-- Retour arrière :
--   ALTER TABLE course DROP CHECK chk_course_passagers, DROP CHECK chk_course_reperes,
--       DROP COLUMN repere_depart, DROP COLUMN repere_arrivee,
--       DROP COLUMN nombre_passagers, DROP COLUMN avec_bagages;
--
-- En plus de l'adresse : un repère en texte libre (« devant la
-- pharmacie »), facultatif. Le point choisi sur la carte n'a pas besoin de
-- colonne : il remplit lat_depart / lng_depart, qui existent déjà.
--
-- Nombre de passagers : même borne que vehicule.nombre_places (1 à 8).
-- Une course ne doit être proposée qu'aux véhicules qui ont assez de
-- places : règle de l'API, la vue v_chauffeur_en_ligne donne déjà
-- nombre_places.
--
-- Les courses déjà enregistrées reçoivent 1 passager, sans bagages, sans
-- repère.

ALTER TABLE course
    ADD COLUMN repere_depart     VARCHAR(255) NULL AFTER id_commune_depart,
    ADD COLUMN repere_arrivee    VARCHAR(255) NULL AFTER id_commune_arrivee,
    ADD COLUMN nombre_passagers  TINYINT NOT NULL DEFAULT 1 AFTER besoin_vehicule_accessible,
    ADD COLUMN avec_bagages      BOOLEAN NOT NULL DEFAULT FALSE AFTER nombre_passagers,
    ADD CONSTRAINT chk_course_passagers CHECK (nombre_passagers BETWEEN 1 AND 8),
    -- Un repère vide s'écrit NULL
    ADD CONSTRAINT chk_course_reperes CHECK (
        (repere_depart IS NULL OR repere_depart <> '')
        AND (repere_arrivee IS NULL OR repere_arrivee <> '')
    );
