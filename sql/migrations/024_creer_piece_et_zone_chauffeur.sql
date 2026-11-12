-- 024 : pièces du chauffeur et communes où il accepte de rouler
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #56 (cahier des charges §7.4, P1)
-- Retour arrière : DROP TABLE chauffeur_commune; DROP TABLE piece_chauffeur;
--
-- Dossier du chauffeur : les pièces sont VÉRIFIÉES EN PERSONNE par
-- l'administrateur (visio 1). On ne stocke aucun fichier ni aucun numéro
-- (permis, carte…), seulement le type, la date d'expiration, qui a vérifié
-- et quand (minimisation, §2).
--
-- Historique gardé : une nouvelle ligne à chaque renouvellement, jamais de
-- mise à jour. La pièce en vigueur d'un type est celle qui expire le plus
-- tard. expire_le est le dernier jour de validité.
--
-- Suspension à l'expiration : l'API passe utilisateur.statut à
-- 'suspendu' (valeur qui existe déjà) quand une pièce en vigueur est
-- expirée. La vue v_piece_chauffeur_a_renouveler (migration 026) donne à
-- l'administrateur ce qui expire bientôt.
--
-- Zones : les communes où le chauffeur accepte de rouler. Aucune ligne =
-- toute la zone desservie. Seules les communes desservies ont un sens
-- (commune.desservie, migration 010) : règle de l'API à l'enregistrement.

CREATE TABLE piece_chauffeur (
    id_piece         INT AUTO_INCREMENT PRIMARY KEY,
    id_chauffeur     INT NOT NULL,
    type             ENUM('permis','carte_professionnelle_vtc','assurance','carte_grise','controle_technique') NOT NULL,
    expire_le        DATE NOT NULL,
    verifiee_le      DATETIME NOT NULL,
    id_verifiee_par  INT NOT NULL,
    FOREIGN KEY (id_chauffeur)    REFERENCES chauffeur(id_utilisateur),
    FOREIGN KEY (id_verifiee_par) REFERENCES utilisateur(id_utilisateur)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pièce en vigueur d'un chauffeur pour un type ; pièces qui expirent bientôt
CREATE INDEX idx_piece_chauffeur_type ON piece_chauffeur(id_chauffeur, type, expire_le);
CREATE INDEX idx_piece_chauffeur_expiration ON piece_chauffeur(expire_le);

CREATE TABLE chauffeur_commune (
    id_chauffeur  INT NOT NULL,
    id_commune    INT NOT NULL,
    PRIMARY KEY (id_chauffeur, id_commune),
    FOREIGN KEY (id_chauffeur) REFERENCES chauffeur(id_utilisateur),
    FOREIGN KEY (id_commune)   REFERENCES commune(id_commune)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chauffeurs qui acceptent une commune (proposer une course)
CREATE INDEX idx_chauffeur_commune_commune ON chauffeur_commune(id_commune);
