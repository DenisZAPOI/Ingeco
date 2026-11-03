# 001. Flask, Pydantic et un OpenAPI généré pour le back

- **Statut** : Acceptée
- **Date** : décidée le 06/10/2026 (socle du projet)
- **Voir aussi** : [architecture.md](../architecture.md#1-back-end-backend), [011](011-types-generes.md)

## Contexte

Deux développeurs en BUT 3, trois mois de développement, un client qui attend un prototype
démontrable mi-décembre. Le cahier des charges recommande Node.js ou Python (Django, FastAPI)
avec une API REST documentée en OpenAPI (palier P2). Denis connaît déjà un socle Flask complet,
celui de ProjectOrganizer (R5.A.05) : couches, validation, Swagger, tests.

## Décision

Python 3.14 et **Flask**, avec **Pydantic** pour valider les entrées et décrire les sorties, et
**flask-pydantic-spec** pour générer l'OpenAPI et le Swagger depuis ces mêmes modèles. Chaque
route déclare tous ses codes d'erreur. Versions figées dans `BACKEND/requirements.txt`.

## Alternatives écartées

- **FastAPI** : validation et OpenAPI intégrés, mais personne dans l'équipe ne le connaît, et
  Flask-SocketIO (temps réel, [014](014-socket-io.md)) est mûr côté Flask. Le gain ne valait pas
  de réapprendre un socle.
- **Django + Django REST Framework** : très complet (ORM, administration), mais lourd pour une
  API seule, et son ORM pousse à créer les tables depuis le code, alors que la base appartient à
  l'équipe BD ([002](002-couches-et-repositories.md)).
- **Node.js (NestJS, Express)** : un seul langage avec le front, mais un socle à construire de zéro.

## Conséquences

- L'OpenAPI est la source du contrat : le front en tire ses types ([011](011-types-generes.md)),
  la CI vérifie qu'ils sont à jour.
- Une réponse non conforme à son modèle renvoie `500` : les écarts se voient tout de suite.
- Flask est synchrone : suffisant pour quelques dizaines de trajets par jour. Une charge de
  100 utilisateurs simultanés (palier P3) demanderait des mesures.
