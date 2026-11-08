-- 008 : ajouter le rôle partner
-- 08/11/2026, BaptisteDK, issue #44
-- Retour arrière : DELETE FROM role WHERE code = 'partner';
INSERT INTO role (code, libelle)
VALUES ('partner', 'Référent partenaire');