-- 023 : table etape_course (journal des étapes d'une course, avec leur auteur)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #55 (cahier des charges §7.4, P1)
-- Retour arrière : DROP TABLE etape_course;
--
-- L'arrivée, le début, la fin, l'absence et les incidents doivent être
-- horodatés AVEC LEUR AUTEUR (chauffeur, usager, opérateur,
-- administrateur). Plutôt qu'une colonne id_..._par par état, un journal :
-- une ligne par étape. Les colonnes de dates de course restent (lecture
-- rapide, CHECK) ; le journal ajoute l'auteur et l'historique complet, y
-- compris ce qu'une colonne écrase (plusieurs désistements, plusieurs
-- incidents, un paiement qui échoue puis réussit).
--
-- id_auteur NULL : étape faite par l'application elle-même (expiration,
-- tâche de l'API). L'API écrit la ligne dans la même transaction que le
-- changement de course.
--
-- Une ligne n'est JAMAIS modifiée ni supprimée par l'API (seule la remise
-- à zéro de la démo efface le journal, avant les courses). Pas de
-- déclencheur pour l'interdire : il bloquerait aussi cette remise à zéro.
--
-- commentaire : surtout pour un incident (obligatoire dans ce cas). Jamais
-- de donnée de santé ni de diagnostic (§12) : l'écran doit le rappeler.

CREATE TABLE etape_course (
    id_etape     INT AUTO_INCREMENT PRIMARY KEY,
    id_course    INT NOT NULL,
    id_auteur    INT,
    type         ENUM('creee','payee','paiement_echoue','acceptee','desistement','chauffeur_arrive',
                      'demarree','terminee','annulee','expiree','passager_absent','remboursee',
                      'incident') NOT NULL,
    survenue_le  DATETIME NOT NULL,
    commentaire  VARCHAR(500),
    FOREIGN KEY (id_course) REFERENCES course(id_course),
    FOREIGN KEY (id_auteur) REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT chk_etape_course_incident    CHECK (type <> 'incident' OR commentaire IS NOT NULL),
    CONSTRAINT chk_etape_course_commentaire CHECK (commentaire IS NULL OR commentaire <> '')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Le journal d'une course, dans l'ordre
CREATE INDEX idx_etape_course_course ON etape_course(id_course, survenue_le);
-- Les incidents récents (administrateur)
CREATE INDEX idx_etape_course_type ON etape_course(type, survenue_le);
