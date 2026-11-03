# 014. Socket.IO pour le temps réel

- **Statut** : Proposée (étape 4, sprint 1)
- **Date** : –
- **Voir aussi** : [architecture.md](../architecture.md#temps-réel), [questions de la visio du 04/11](../questions-sprint-2026-11-04.md#le-nouveau-cahier-des-charges-v10)

## Contexte

Le sujet de la SAÉ demande un suivi en temps réel et la géolocalisation des chauffeurs.
Aujourd'hui, les écrans ont un bouton « Actualiser ». Le cahier des charges v1.0, lui, classe le
« suivi GPS en temps réel » hors périmètre : la question est posée à la cliente et aux
enseignants le 04/11/2026.

## Décision proposée

**Flask-SocketIO** côté back (déjà installé dans le socle), **socket.io-client** côté front. Un
salon par course ; les services émettent **après** la validation de leur transaction. Événements
prévus : `ride:updated`, `ride:offer`, `ride:offer-closed`, `driver:location`. Le bouton
« Actualiser » reste en secours.

## Alternatives écartées

- **WebSocket natif** : plus léger, mais il faudrait réécrire la reconnexion, les salons et le
  repli quand le WebSocket est bloqué.
- **Interroger l'API toutes les N secondes** : simple, mais coûteux en données et en batterie sur
  un réseau faible.
- **Server-Sent Events** : un seul sens, et moins bien intégré à Flask.
- **Notifications push** : peu fiables en application web sur iPhone.

## Conséquences

- Environ 15 Ko compressés de plus pour socket.io-client, chargés seulement une fois connecté.
- Les verrous en mémoire ([007](007-etat-en-memoire.md)) et Socket.IO supposent tous deux un seul
  processus d'API, ou un serveur de messages (Redis) entre plusieurs.
- **Si la cliente confirme le temps réel hors périmètre**, cette fiche passe à « Abandonnée » et
  le bouton « Actualiser » reste la règle.
