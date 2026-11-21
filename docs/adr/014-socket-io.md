# 014. Socket.IO pour le temps réel

- **Statut** : Acceptée
- **Date** : 21/11/2026
- **Voir aussi** : [architecture.md](../architecture.md#temps-réel), [contrat-api.md](../contrat-api.md#5-temps-réel), [decisions.md](../decisions.md#ce-que-fixe-le-cahier-des-charges-v10)

## Contexte

Le sujet de la SAÉ demande un suivi en temps réel et la géolocalisation des chauffeurs.
Jusqu'ici, les écrans avaient un bouton « Actualiser ». Le cahier des charges v1.0, source de
vérité, classe le « suivi GPS en temps réel » hors périmètre. Décision du 03/11/2026 : le suivi en
temps réel est celui du **statut** du trajet (chauffeur trouvé, en route, terminé…) et des
offres faites aux chauffeurs, sans position du chauffeur montrée au passager.

## Décision

**Flask-SocketIO** côté back (déjà installé dans le socle), **socket.io-client** côté front
(licence MIT). Choix faits le 21/11/2026 :

- **Les événements sont des signaux, pas des données** : `ride:updated` donne `{ rideId, status }`,
  `offers:changed` rien. L'écran relit la course ou la liste par HTTP. Ce que chacun peut voir
  (téléphone, photo, prénom selon l'état) reste décidé à un seul endroit du back (`present()`),
  sans risque de fuite par un salon mal choisi. Coût : un aller-retour HTTP par changement.
- **Abonnement à la demande** : la page d'un trajet envoie `ride:follow { rideId }`, accepté
  seulement pour qui peut lire la course (même règle que `GET /rides/{id}`). La liste des offres
  envoie `offers:follow`, réservé aux chauffeurs, et rejoint le salon `drivers`.
- **Connexion authentifiée** par le cookie de session, comme une requête HTTP : refusée sans
  session valide. Le compte est relu à chaque abonnement (la connexion dure plus que le jeton de
  15 minutes) : un compte suspendu ne suit plus rien.
- **Émission après la validation de la transaction** : le service appelle
  `broadcast.ride_changed()` à côté de son écriture, et l'émission attend le commit
  (`database.after_commit`). Une écriture annulée n'annonce rien.
- **Connexion ouverte seulement sur les écrans suivis** (page d'un trajet, liste des offres),
  fermée en les quittant. La bibliothèque est chargée à la demande (`import()`).
- **Transport par défaut** de Socket.IO : long polling, puis passage au WebSocket. Le plus
  robuste sur les réseaux qui bloquent le WebSocket.
- **Relecture discrète** (`reloadQuietly` de `useRequest`) à chaque événement et à chaque
  (re)connexion : un événement perdu pendant une coupure n'est pas renvoyé. Pas de message de
  chargement, et un échec laisse l'écran tel quel.
- Si la connexion est refusée (jeton de 15 minutes expiré), le front renouvelle la session une
  fois, puis réessaie.
- Le bouton **« Actualiser » reste**, en secours.

## Alternatives écartées

- **WebSocket natif** : plus léger, mais il faudrait réécrire la reconnexion, les salons et le
  repli quand le WebSocket est bloqué.
- **Interroger l'API toutes les N secondes** : simple, mais coûteux en données et en batterie sur
  un réseau faible.
- **Server-Sent Events** : un seul sens, et moins bien intégré à Flask.
- **Notifications push** : peu fiables en application web sur iPhone.
- **La course complète dans l'événement** (prévue par le contrat v2) : un aller-retour de moins,
  mais une version par destinataire à calculer, et un salon mal choisi ferait fuiter un téléphone.
- **`ride:offer` / `ride:offer-closed` aux seuls chauffeurs proches** (contrat v2) : la distance
  à calculer au moment d'émettre, pour un gain faible ; la liste relue applique déjà le filtre.

## Conséquences

- Environ 15 Ko compressés de plus pour socket.io-client, chargés seulement sur les écrans suivis.
- Les verrous en mémoire ([007](007-etat-en-memoire.md)) et Socket.IO supposent tous deux un seul
  processus d'API, ou un serveur de messages (Redis) entre plusieurs. La liste des connexions
  (`sockets/handlers.py`) est aussi en mémoire.
- Sans suivi GPS, le trafic reste faible : un signal par changement d'état, pas une position
  toutes les quelques secondes, ce qui convient au réseau « Regular 2G ».
- Les messages Socket.IO ne sont pas dans l'OpenAPI : leurs types sont écrits à la main dans
  `FRONTEND/src/api/realtime.ts`, d'après la partie 5 du contrat.
