-- 017 : questionnaire d'orientation rempli et plan d'action (module M1)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #50 (cahier des charges §7.1, P1 ; RGPD art. 22)
-- Retour arrière :
--   DROP TABLE etape_plan; DROP TABLE plan_action;
--   DROP TABLE reponse_questionnaire; DROP TABLE questionnaire;
--
-- Les questions et les règles du plan restent dans le code de l'API
-- (traduites avec l'interface). La base garde seulement les réponses d'un
-- usager et le plan qui en est sorti, sous forme de CODES fixés par le
-- code (situation -> sans_emploi…), jamais de libellés.
--
-- CHAMPS INTERDITS (cahier des charges §12) : nationalité, situation de
-- séjour, numéro de sécurité sociale, origine, diagnostic médical. Aucune
-- colonne ne les porte, et aucun code de réponse ne doit les porter : un
-- frein s'écrit comme un besoin (besoin_garde, besoin_vehicule_adapte),
-- jamais comme un diagnostic. La seule zone libre (texte, 500 caractères)
-- sert aux expériences informelles ; l'écran doit le rappeler.
--
-- Aucune décision automatique (RGPD art. 22) : un conseiller ou un
-- administrateur peut reprendre le plan. modifie_le et id_modifie_par
-- disent qui l'a fait et quand.
--
-- Un usager peut refaire le questionnaire : chaque passage est gardé, le
-- plus récent fait foi (index idx_questionnaire_usager).

CREATE TABLE questionnaire (
    id_questionnaire  INT AUTO_INCREMENT PRIMARY KEY,
    id_usager         INT NOT NULL,
    rempli_le         DATETIME NOT NULL,
    FOREIGN KEY (id_usager) REFERENCES usager(id_utilisateur)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Le questionnaire le plus récent d'un usager
CREATE INDEX idx_questionnaire_usager ON questionnaire(id_usager, rempli_le);

-- Une ligne par réponse ; plusieurs lignes pour une question à choix
-- multiples (une par choix coché)
CREATE TABLE reponse_questionnaire (
    id_questionnaire  INT NOT NULL,
    code_question     VARCHAR(50) NOT NULL,
    code_reponse      VARCHAR(50) NOT NULL,
    -- Seulement pour une réponse libre (expériences informelles)
    texte             VARCHAR(500),
    PRIMARY KEY (id_questionnaire, code_question, code_reponse),
    FOREIGN KEY (id_questionnaire) REFERENCES questionnaire(id_questionnaire),
    -- Des codes, pas des phrases : minuscules, chiffres et _
    CONSTRAINT chk_reponse_questionnaire_codes CHECK (
        code_question REGEXP '^[a-z0-9_]+$' AND code_reponse REGEXP '^[a-z0-9_]+$'
    ),
    CONSTRAINT chk_reponse_questionnaire_texte CHECK (texte IS NULL OR texte <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Un plan par questionnaire rempli
CREATE TABLE plan_action (
    id_plan           INT AUTO_INCREMENT PRIMARY KEY,
    id_questionnaire  INT NOT NULL UNIQUE,
    cree_le           DATETIME NOT NULL,
    -- La dernière reprise par une personne ; NULL tant que personne n'y a touché
    modifie_le        DATETIME,
    id_modifie_par    INT,
    FOREIGN KEY (id_questionnaire) REFERENCES questionnaire(id_questionnaire),
    FOREIGN KEY (id_modifie_par)   REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT chk_plan_action_modification CHECK ((modifie_le IS NULL) = (id_modifie_par IS NULL)),
    CONSTRAINT chk_plan_action_dates        CHECK (modifie_le IS NULL OR modifie_le >= cree_le)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- De 3 à 5 étapes (le minimum de 3 est une règle de l'API : une base ne
-- compte pas les lignes d'une autre table dans un CHECK)
CREATE TABLE etape_plan (
    id_plan     INT NOT NULL,
    ordre       TINYINT NOT NULL,
    code_etape  VARCHAR(50) NOT NULL,
    -- Ce qui est proposé à cette étape : un service d'aide, une offre, ou rien
    id_service  INT,
    id_offre    INT,
    -- L'usager coche l'étape ; NULL tant qu'elle n'est pas faite
    faite_le    DATETIME,
    PRIMARY KEY (id_plan, ordre),
    FOREIGN KEY (id_plan)    REFERENCES plan_action(id_plan),
    FOREIGN KEY (id_service) REFERENCES service_aide(id_service),
    FOREIGN KEY (id_offre)   REFERENCES offre_emploi(id_offre),
    CONSTRAINT chk_etape_plan_ordre       CHECK (ordre BETWEEN 1 AND 5),
    CONSTRAINT chk_etape_plan_code        CHECK (code_etape REGEXP '^[a-z0-9_]+$'),
    CONSTRAINT chk_etape_plan_proposition CHECK (id_service IS NULL OR id_offre IS NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
