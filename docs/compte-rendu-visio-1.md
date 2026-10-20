# Compte rendu : première visio avec la porteuse de projet

- **Date** : un mercredi d'octobre 2026, avant l'envoi des points à valider du 13/10/2026 (date
  exacte à compléter).
- **Présents** : la fondatrice et présidente d'Ingeco Territoires ; l'équipe projet (2
  développeurs, 3 étudiants parcours C).
- **Source** : retranscription automatique de l'appel, enregistré avec l'accord de tous. La
  retranscription n'est pas versionnée ; ce document en garde les décisions.

## Ce que la cliente a dit du projet

- Le service doit démarrer **en janvier 2027**. Le projet étudiant se termine vers le **10 janvier
  2027**.
- Ce n'est pas un Uber : la société travaille dans l'**insertion professionnelle**, la dimension
  sociale fait partie du projet. Mais l'application est **ouverte à tous** (salariés, femmes qui
  vont au travail ou en entretien, étudiants…), « comme un service VTC classique ».
- Sa principale inquiétude : le **GPS et la réception** des smartphones sur place.
- Logo, couleurs, identité visuelle : sans difficulté, à voir plus tard.

## Décisions et demandes

| Sujet | Ce qui a été dit | Où c'est repris |
|---|---|---|
| Zone du pilote | **Cayenne et environ 5 km autour**, avec les communes voisines : Rémire-Montjoly et Cogneau-Lamirande (Matoury). Un rayon kilométrique est à définir | [contrat-api.md](contrat-api.md) 3.6 et H18, UC10 |
| Chauffeurs | Recrutés **en personne** : entretien, vérification du permis, de l'âge et du véhicule. Une vingtaine de chauffeurs formés par la société. Contrôle d'identité en présentiel, au moins pour la première phase | UC52 (déjà en place depuis le 19/10/2026) |
| Formation des chauffeurs | « On va essayer de mettre en place des formations » | Hors MVP (UC76) |
| Transport de personnes handicapées | Agréments des chauffeurs pour transporter des personnes handicapées : souhaitable, **en deuxième partie** | Hors MVP (UC80) |
| Profil du chauffeur | Pour la sécurité, le passager doit voir **au moins le visage du chauffeur**, et un petit profil (« mini CV ») de la personne qui l'accompagne | UC15, [contrat-api.md](contrat-api.md) H19 |
| Paiement | **Carte bancaire uniquement**, pas d'argent qui circule entre deux personnes. Tout se paie **à la réservation** | Déjà en place (UC14) |
| Abonnement | « On va essayer aussi de mettre un système d'**abonnement mensuel** » (tant de courses, ou tant d'argent dépensé) | Non classé (UC79) |
| RGPD | Question sur les données personnelles et les cartes bancaires : la carte n'est jamais vue ni stockée par l'application (prestataire de paiement) | Contrat 3.3 et 6.9 |

Le centre d'appel n'a pas été abordé pendant cette visio.

## Organisation

- **Tutrice côté client** : Sophonie Delva, pour toutes les questions numériques. Les retours
  passent par elle.
- **Groupe WhatsApp** avec l'équipe et la tutrice, à créer.
- **Revue chaque mardi à 10 h** (créneau possible de 9 h à 12 h), 1 h à 1 h 30, avec un compte
  rendu de réunion. La cliente propose un outil d'IA de retranscription pour le produire.
- **Questions** : le document des questions importantes pour le MVP est à envoyer à la tutrice
  (fait le 13/10/2026 : [points-a-valider-porteur.pdf](points-a-valider-porteur.pdf)).
- **Cahier des charges** : la cliente doit nous transmettre un cahier des charges. Vérifier s'il
  diffère de la version 1 du 06/07/2026.
- **Bugs** : signalés par n'importe qui (client compris) dans les issues GitHub. Les
  développeurs traitent l'application, l'équipe BD la base.
