-- 009 : table langue (langues de l'interface et des contenus traduits)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issues #48 et #49 (ADR 018)
-- Retour arrière : DROP TABLE langue;
--
-- Les cinq langues de l'application (entretien du 03/11/2026), avec les
-- mêmes codes que l'interface (FRONTEND/src/i18n). Une table plutôt
-- qu'un CHECK répété dans chaque table de traduction : ajouter une langue
-- est un simple INSERT, et une faute de frappe dans un code est refusée
-- par la clé étrangère.
--
-- Le français est la langue de référence : les textes des offres, des
-- services et des fiches sont en français dans leur table, et les tables
-- *_traduction ne contiennent que les autres langues.

CREATE TABLE langue (
    code     VARCHAR(10)  PRIMARY KEY,  -- fr | gcr | ht | pt-BR | en
    libelle  VARCHAR(50)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO langue (code, libelle) VALUES
('fr',    'Français'),
('gcr',   'Créole guyanais'),
('ht',    'Créole haïtien'),
('pt-BR', 'Portugais du Brésil'),
('en',    'Anglais');
