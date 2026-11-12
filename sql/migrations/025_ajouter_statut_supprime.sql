-- 025 : statut « supprime » sur utilisateur (compte supprimé et anonymisé)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #32 (cahier des charges §6, P1), décision du 03/11/2026
-- Retour arrière (seulement si aucun compte n'est supprimé) :
--   ALTER TABLE utilisateur DROP CHECK chk_utilisateur_supprime, DROP CHECK chk_utilisateur_telephone_supprime;
--   ALTER TABLE utilisateur MODIFY COLUMN statut ENUM('actif','suspendu') NOT NULL DEFAULT 'actif';
--
-- Quand un administrateur traite une demande de suppression
-- (demande_suppression, migration 002), le compte n'est pas effacé : les
-- courses restent, pour les statistiques, mais sans identité. Le compte
-- passe au statut supprime : il ne peut plus se connecter et sort des
-- listes (règles de l'API).
--
-- Ce que la base impose à un compte supprimé :
--   - prénom et nom vides (colonnes NOT NULL : chaîne vide, pas NULL),
--     courriel NULL ;
--   - plus de mot de passe ni de code d'activation ;
--   - téléphone remplacé par +000 suivi de l'identifiant sur 9 chiffres
--     (+000000000042 pour le compte 42) : l'indicatif 000 n'existe pas,
--     donc aucune collision avec un vrai numéro, et la valeur respecte
--     chk_utilisateur_telephone. MySQL refuse qu'un CHECK lise une colonne
--     AUTO_INCREMENT : la base vérifie la forme (+000 et 9 chiffres),
--     l'API écrit le bon identifiant. Inversement, un compte qui n'est pas
--     supprimé ne peut pas avoir un numéro en +000.
--
-- À faire PAR L'API, dans la même transaction (la base ne peut pas le
-- vérifier d'une table à l'autre) :
--   UPDATE utilisateur
--      SET statut = 'supprime', prenom = '', nom = '', email = NULL,
--          telephone = CONCAT('+000', LPAD(id_utilisateur, 9, '0')),
--          mot_de_passe_hash = NULL, code_activation_hash = NULL,
--          code_activation_expire_le = NULL,
--          version_session = version_session + 1   -- ferme les sessions
--    WHERE id_utilisateur = :id;
--   -- un chauffeur : photo et dernière position effacées, hors ligne
--   UPDATE chauffeur SET photo = NULL, photo_modifiee_le = NULL, est_disponible = FALSE,
--          derniere_lat = NULL, derniere_lng = NULL, derniere_position_le = NULL
--    WHERE id_utilisateur = :id;
--   UPDATE demande_suppression SET traitee_le = :maintenant, id_traitee_par = :admin
--    WHERE id_utilisateur = :id AND traitee_le IS NULL;
-- Le commentaire d'une évaluation peut contenir un nom : à effacer aussi
-- (evaluation.commentaire = NULL) sur les courses de ce compte, si la
-- cliente le demande.

ALTER TABLE utilisateur
    MODIFY COLUMN statut ENUM('actif','suspendu','supprime') NOT NULL DEFAULT 'actif';

ALTER TABLE utilisateur
    ADD CONSTRAINT chk_utilisateur_supprime CHECK (
        statut <> 'supprime'
        OR (prenom = '' AND nom = '' AND email IS NULL
            AND mot_de_passe_hash IS NULL AND code_activation_hash IS NULL
            AND telephone REGEXP '^[+]000[0-9]{9}$')
    ),
    ADD CONSTRAINT chk_utilisateur_telephone_supprime CHECK (
        statut = 'supprime' OR telephone NOT LIKE '+000%'
    );
