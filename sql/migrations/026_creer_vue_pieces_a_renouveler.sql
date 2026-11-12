-- 026 : vue v_piece_chauffeur_a_renouveler (pièces expirées ou qui expirent dans 30 jours)
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #56 (statut supprime : migration 025)
-- Retour arrière : DROP VIEW v_piece_chauffeur_a_renouveler;
--
-- Pour l'administrateur : pour chaque chauffeur dont le compte n'est pas
-- supprimé, et pour chaque type de pièce, la pièce EN VIGUEUR (celle qui
-- expire le plus tard), quand elle est expirée ou qu'elle expire dans les
-- 30 jours. Les plus urgentes d'abord :
--   SELECT * FROM v_piece_chauffeur_a_renouveler ORDER BY jours_restants;
--
-- « Aujourd'hui » est le jour de Cayenne (UTC-3), comme dans les vues des
-- statistiques : une pièce qui expire le 30 est encore valable le 30 au
-- soir en Guyane. jours_restants : 0 = dernier jour, négatif = expirée.
-- La fenêtre de 30 jours est celle de l'issue ; la changer = une
-- migration qui remplace la vue.
--
-- Un type de pièce jamais enregistré n'apparaît pas : toutes ne sont pas
-- exigées de tous les chauffeurs (contrôle technique selon l'âge du
-- véhicule). La liste des pièces obligatoires reste une règle de l'API.

CREATE VIEW v_piece_chauffeur_a_renouveler AS
SELECT
    p.id_chauffeur,
    u.prenom,
    u.nom,
    u.telephone,
    u.statut                                                     AS statut_compte,
    p.type,
    p.expire_le,
    DATEDIFF(p.expire_le, DATE(CONVERT_TZ(UTC_TIMESTAMP(), '+00:00', '-03:00'))) AS jours_restants,
    p.verifiee_le,
    p.id_verifiee_par
FROM piece_chauffeur p
JOIN utilisateur u ON u.id_utilisateur = p.id_chauffeur
WHERE u.statut <> 'supprime'
  -- La pièce en vigueur : aucune pièce du même type n'expire plus tard
  AND NOT EXISTS (
      SELECT 1 FROM piece_chauffeur p2
      WHERE p2.id_chauffeur = p.id_chauffeur
        AND p2.type = p.type
        AND (p2.expire_le > p.expire_le
             OR (p2.expire_le = p.expire_le AND p2.id_piece > p.id_piece))
  )
  AND DATEDIFF(p.expire_le, DATE(CONVERT_TZ(UTC_TIMESTAMP(), '+00:00', '-03:00'))) <= 30;
