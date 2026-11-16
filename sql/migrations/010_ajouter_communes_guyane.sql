-- 010 : toutes les communes de Guyane, et la colonne desservie
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #52 (cahier des charges §5 M9)
-- Retour arrière :
--   DELETE FROM commune WHERE id_commune > 3;  -- seulement si rien n'y renvoie
--   ALTER TABLE commune DROP INDEX idx_commune_desservie, DROP COLUMN desservie;
--
-- Jusqu'ici, la table ne contenait que les communes desservies par les
-- trajets. Les offres d'emploi et les services d'aide peuvent être
-- ailleurs (Kourou, Saint-Laurent-du-Maroni…) : la table liste désormais
-- les 22 communes, et la colonne desservie dit lesquelles reçoivent des
-- trajets. L'administrateur la change (zones réglables, M9).
--
-- POUR L'API : les départs et arrivées d'une course se choisissent parmi
-- les communes WHERE desservie = TRUE, et plus parmi toute la table.
-- Une course déjà enregistrée garde sa commune même si elle n'est plus
-- desservie ensuite.
--
-- Zone du pilote, PROVISOIRE (docs/decisions.md) : Cayenne,
-- Rémire-Montjoly et Matoury, qui gardent leurs identifiants 1 à 3 (les
-- courses de démo y renvoient). Les autres sont ajoutées dans l'ordre
-- alphabétique, non desservies.

ALTER TABLE commune
    ADD COLUMN desservie BOOLEAN NOT NULL DEFAULT FALSE;

UPDATE commune SET desservie = TRUE WHERE id_commune IN (1, 2, 3);

INSERT INTO commune (nom, desservie) VALUES
('Apatou',                  FALSE),
('Awala-Yalimapo',          FALSE),
('Camopi',                  FALSE),
('Grand-Santi',             FALSE),
('Iracoubo',                FALSE),
('Kourou',                  FALSE),
('Macouria',                FALSE),
('Mana',                    FALSE),
('Maripasoula',             FALSE),
('Montsinéry-Tonnegrande',  FALSE),
('Ouanary',                 FALSE),
('Papaïchton',              FALSE),
('Régina',                  FALSE),
('Roura',                   FALSE),
('Saint-Élie',              FALSE),
('Saint-Georges',           FALSE),
('Saint-Laurent-du-Maroni', FALSE),
('Saül',                    FALSE),
('Sinnamary',               FALSE);

-- Liste des communes proposées pour un trajet
CREATE INDEX idx_commune_desservie ON commune(desservie, nom);
