# 016. Vitest pour les tests du front

- **Statut** : Acceptée
- **Date** : décidée le 03/11/2026 (traductions)
- **Voir aussi** : [013](013-traductions-maison.md), [CLAUDE.md](../../CLAUDE.md) (« Commandes »)

## Contexte

Le back a ses tests pytest depuis le début ; le front n'en avait aucun. Les traductions
([013](013-traductions-maison.md)) ont besoin d'une preuve automatique que le changement de
langue marche et qu'aucune langue n'oublie une clé. Le cahier des charges demande aussi des
tests automatisés sur les dates, calculées à l'heure de Guyane (§3), et des tests exécutés à
chaque modification (§18, P2).

## Décision

**Vitest 5.0.5**, en dépendance de développement. Il réutilise la configuration de Vite
(`vite.config.ts`, partie `test`) : rien à configurer en plus. Les tests (`src/**/*.test.ts`)
portent sur la logique pure (`lib/`, `i18n/`) et tournent dans Node, sans navigateur simulé.
`npm test` les lance ; la CI aussi, dans le contrôle « Front (lint + build) ».

## Alternatives écartées

- **Jest** : la référence historique, mais il faut le configurer pour TypeScript et les modules
  ES, ce que Vitest fait déjà avec Vite.
- **Pas d'outil, TypeScript seul** : il vérifie les clés, pas le changement de langue ni les
  dates.
- **Tests de bout en bout (Playwright)** : utiles pour les scénarios de démonstration, mais un
  navigateur à installer dans la CI ; à envisager plus tard, dans une autre fiche.

## Conséquences

- Aucun poids en plus pour l'utilisateur : une dépendance de développement seulement.
- Pas encore de tests de composants React : ils demanderaient un DOM simulé (jsdom), une
  dépendance de plus. À ajouter si un écran a une logique qui le justifie.
- Avant chaque pull request : `npm test`, en plus de `pytest`, du lint et du build.
