-- 022 : v_stats_courses_par_jour compte les passagers absents et les paiements échoués
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), suite de l'issue #54 (migration 020)
-- Retour arrière : rejouer le CREATE VIEW de la migration 003 avec CREATE OR REPLACE.
--
-- Même vue que la migration 003 (une ligne par jour de demande, en heure
-- de Guyane), avec deux colonnes de plus, en fin de liste pour ne rien
-- décaler :
--   - nb_passager_absent : le chauffeur est venu, le passager non ;
--   - nb_paiements_echoues : courses dont le dernier paiement a échoué
--     (elles finissent en général expirées).
-- Une course expirée après un paiement échoué compte désormais aussi dans
-- nb_expirees_sans_paiement : l'usager n'a jamais réussi à payer.

CREATE OR REPLACE VIEW v_stats_courses_par_jour AS
SELECT
    DATE(CONVERT_TZ(cree_le, '+00:00', '-03:00'))                         AS jour,
    COUNT(*)                                                              AS nb_demandes,
    SUM(CASE WHEN statut = 'terminee' THEN 1 ELSE 0 END)                  AS nb_terminees,
    SUM(CASE WHEN statut = 'annulee' THEN 1 ELSE 0 END)                   AS nb_annulees,
    -- Payée (ou rien à payer) mais aucun chauffeur ne l'a prise : la
    -- demande que le service n'a pas su servir
    SUM(CASE WHEN statut = 'expiree' AND statut_paiement IN ('rembourse', 'non_requis')
             THEN 1 ELSE 0 END)                                           AS nb_expirees_sans_chauffeur,
    -- Jamais payée à temps : paiement abandonné ou échoué
    SUM(CASE WHEN statut = 'expiree' AND statut_paiement IN ('en_attente', 'echoue')
             THEN 1 ELSE 0 END)                                           AS nb_expirees_sans_paiement,
    SUM(CASE WHEN canal = 'telephone' THEN 1 ELSE 0 END)                  AS nb_par_telephone,
    SUM(CASE WHEN statut_paiement = 'rembourse' THEN 1 ELSE 0 END)        AS nb_remboursees,
    SUM(CASE WHEN statut_paiement = 'rembourse' THEN prix_centimes ELSE 0 END) AS montant_rembourse_centimes,
    SUM(CASE WHEN statut = 'terminee' THEN prix_centimes ELSE 0 END)      AS montant_terminees_centimes,
    SUM(CASE WHEN statut = 'passager_absent' THEN 1 ELSE 0 END)           AS nb_passager_absent,
    SUM(CASE WHEN statut_paiement = 'echoue' THEN 1 ELSE 0 END)           AS nb_paiements_echoues
FROM course
GROUP BY DATE(CONVERT_TZ(cree_le, '+00:00', '-03:00'));
