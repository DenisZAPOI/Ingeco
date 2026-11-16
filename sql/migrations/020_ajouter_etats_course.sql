-- 020 : états « chauffeur arrivé » et « passager absent », paiement « échoué »
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #54 (cahier des charges §7.4, P1)
-- Retour arrière (seulement si aucune course n'utilise les nouvelles valeurs) :
--   ALTER TABLE course DROP CHECK chk_course_arrivee, DROP CHECK chk_course_absent,
--       DROP CHECK chk_course_absent_paiement, DROP COLUMN arrivee_le, DROP COLUMN absent_le;
--   puis remettre les ENUM et les CHECK chk_course_chauffeur, chk_course_paiement et
--   chk_course_attente_paiement de schema-mvp.sql.
--
-- Cycle de vie de statut, complété (schema-mvp.sql, partie 8) :
--   attente_paiement --paiement--> en_attente --> acceptee --> chauffeur_arrive --> en_cours --> terminee
--                                       ^------ désistement ----'          |
--                                                                          '--> passager_absent
--   attente_paiement, en_attente           --> expiree
--   attente_paiement, en_attente, acceptee --> annulee
--
-- chauffeur_arrive : le chauffeur est au point de départ (arrivee_le).
-- Le chauffeur peut aussi démarrer sans l'avoir signalé : arrivee_le peut
-- rester NULL sur une course en_cours ou terminee (les courses déjà
-- enregistrées n'en ont pas).
-- passager_absent : état final, déclaré par le chauffeur après son arrivée
-- (absent_le >= arrivee_le). Règle PROVISOIRE (docs/decisions.md, en
-- attente de la cliente) : il attend 10 minutes, et le passager est
-- remboursé. Le délai est une règle de l'API ; la base vérifie seulement
-- qu'une course où le passager est absent avait bien été payée.
--
-- Paiement « echoue » : la tentative a échoué, rien n'est débité
-- (payee_le reste NULL). La course reste en attente_paiement, l'usager
-- peut réessayer avant expire_le ; sinon elle expire, paiement échoué.
-- Un paiement échoué n'apparaît jamais comme réussi (§7.4).

ALTER TABLE course
    MODIFY COLUMN statut ENUM('attente_paiement','en_attente','acceptee','chauffeur_arrive','en_cours',
                              'terminee','annulee','expiree','passager_absent') NOT NULL,
    MODIFY COLUMN statut_paiement ENUM('non_requis','en_attente','paye','echoue','rembourse') NOT NULL,
    ADD COLUMN arrivee_le DATETIME NULL AFTER acceptee_le,
    ADD COLUMN absent_le  DATETIME NULL AFTER expiree_le;

ALTER TABLE course
    DROP CHECK chk_course_chauffeur,
    DROP CHECK chk_course_paiement,
    DROP CHECK chk_course_attente_paiement;

ALTER TABLE course
    -- Un chauffeur si et seulement si la course est prise ; une course
    -- annulée peut l'avoir été avant ou après l'acceptation
    ADD CONSTRAINT chk_course_chauffeur CHECK (
        statut = 'annulee'
        OR (id_chauffeur IS NOT NULL)
           = (statut IN ('acceptee','chauffeur_arrive','en_cours','terminee','passager_absent'))
    ),
    -- Pas d'impayé : une course proposée ou prise est payée ou sans part usager
    ADD CONSTRAINT chk_course_paiement CHECK (
        statut NOT IN ('en_attente','acceptee','chauffeur_arrive','en_cours','terminee')
        OR statut_paiement IN ('paye','non_requis')
    ),
    -- En attente de paiement : pas encore payé, ou une tentative a échoué
    ADD CONSTRAINT chk_course_attente_paiement CHECK (
        statut <> 'attente_paiement' OR statut_paiement IN ('en_attente','echoue')
    ),
    -- Arrivée obligatoire pour ces deux états, impossible avant l'acceptation
    ADD CONSTRAINT chk_course_arrivee CHECK (
        (statut NOT IN ('chauffeur_arrive','passager_absent') OR arrivee_le IS NOT NULL)
        AND (statut NOT IN ('attente_paiement','en_attente','acceptee','expiree') OR arrivee_le IS NULL)
        AND (arrivee_le IS NULL OR arrivee_le >= acceptee_le)
    ),
    ADD CONSTRAINT chk_course_absent CHECK (
        (absent_le IS NOT NULL) = (statut = 'passager_absent')
        AND (absent_le IS NULL OR absent_le >= arrivee_le)
    ),
    -- Le passager absent avait payé (ou n'avait rien à payer) : la course
    -- avait été proposée aux chauffeurs
    ADD CONSTRAINT chk_course_absent_paiement CHECK (
        statut <> 'passager_absent' OR statut_paiement IN ('paye','rembourse','non_requis')
    );
