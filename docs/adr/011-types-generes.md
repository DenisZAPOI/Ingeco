# 011. Types TypeScript générés depuis l'OpenAPI

- **Statut** : Acceptée
- **Date** : décidée le 06/10/2026 (socle)
- **Voir aussi** : [001](001-flask-pydantic-openapi.md), [architecture.md](../architecture.md#règles)

## Contexte

Le back et le front évoluent en même temps, à deux développeurs. Un champ renommé côté back qui
casse un écran sans que personne ne le voie, c'est le genre d'erreur qui apparaît pendant une
démonstration.

## Décision

Les types du front (`FRONTEND/src/types/api.ts`) sont **générés** par openapi-typescript depuis
l'OpenAPI du back (`npm run api:types`), jamais écrits à la main. La CI les régénère et échoue
s'ils diffèrent de ceux du dépôt.

## Alternatives écartées

- **Types écrits à la main** : se désynchronisent sans bruit.
- **Client complet généré** (openapi-generator, orval) : plus de code produit et une dépendance
  d'exécution ; un seul `fetch` maison (`api/client.ts`) suffit.
- **tRPC ou GraphQL** : imposent une technologie commune aux deux côtés, alors que le back est en
  Python.

## Conséquences

- Après un changement de DTO, TypeScript montre tous les écrans touchés.
- Il faut lancer le back pour régénérer les types : une étape de plus avant la pull request.
