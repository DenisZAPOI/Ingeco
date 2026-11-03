-- 003 : vue v_stats_courses_par_jour (tableau de bord administrateur)
-- 03/11/2026, Kurtys TSHIBOLA (équipe BD), issue #23 (UC56, contrat 6.4)
-- Retour arrière : DROP VIEW v_stats_courses_par_jour;
--
-- Une ligne par jour de demande, en heure de Guyane (UTC-3, sans heure
-- d'été) : une course demandée à 22 h à Cayenne compte pour ce jour-là,
-- pas pour le lendemain en UTC. Toutes les colonnes sont des comptes ou des
-- sommes : l'API les additionne sur la période choisie, par exemple
--   SELECT SUM(nb_demandes), SUM(nb_terminees) FROM v_stats_courses_par_jour
--   WHERE jour BETWEEN :du AND :au;
--
-- Propre à MySQL : CONVERT_TZ avec un décalage fixe ('-03:00'), qui ne
-- demande pas les tables de fuseaux. Équivalent SQLite :
-- date(cree_le, '-3 hours').

CREATE VIEW v_stats_courses_par_jour AS
SELECT
    DATE(CONVERT_TZ(cree_le, '+00:00', '-03:00'))                         AS jour,
    COUNT(*)                                                              AS nb_demandes,
    SUM(CASE WHEN statut = 'terminee' THEN 1 ELSE 0 END)                  AS nb_terminees,
    SUM(CASE WHEN statut = 'annulee' THEN 1 ELSE 0 END)                   AS nb_annulees,
    -- Payée (ou rien à payer) mais aucun chauffeur ne l'a prise : la
    -- demande que le service n'a pas su servir
    SUM(CASE WHEN statut = 'expiree' AND statut_paiement IN ('rembourse', 'non_requis')
             THEN 1 ELSE 0 END)                                           AS nb_expirees_sans_chauffeur,
    -- Jamais payée à temps : paiement abandonné
    SUM(CASE WHEN statut = 'expiree' AND statut_paiement = 'en_attente'
             THEN 1 ELSE 0 END)                                           AS nb_expirees_sans_paiement,
    SUM(CASE WHEN canal = 'telephone' THEN 1 ELSE 0 END)                  AS nb_par_telephone,
    SUM(CASE WHEN statut_paiement = 'rembourse' THEN 1 ELSE 0 END)        AS nb_remboursees,
    SUM(CASE WHEN statut_paiement = 'rembourse' THEN prix_centimes ELSE 0 END) AS montant_rembourse_centimes,
    SUM(CASE WHEN statut = 'terminee' THEN prix_centimes ELSE 0 END)      AS montant_terminees_centimes
FROM course
GROUP BY DATE(CONVERT_TZ(cree_le, '+00:00', '-03:00'));
