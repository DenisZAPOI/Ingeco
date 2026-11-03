# 005. Inscription et mot de passe oublié par code SMS

- **Statut** : Acceptée
- **Date** : décidée le 02/11/2026 (inscription, audit F4) ; étendue le 03/11/2026 (mot de passe oublié)
- **Voir aussi** : [audit de sécurité](../audit-securite-2026-11-02.md), [006](006-sms-simules.md), [contrat d'API](../contrat-api.md)

## Contexte

Le téléphone est l'identifiant : une partie du public n'a pas de courriel, et le cahier des
charges l'impose (« inscription par téléphone, sans courriel obligatoire », critère P1 : « une
personne sans courriel crée son compte et le récupère par téléphone »). L'audit a montré qu'une
inscription sans preuve permettait de prendre le numéro de quelqu'un d'autre et de savoir qui
utilise le service.

## Décision

- **Inscription** en deux temps : un code de 6 chiffres par SMS, valable 10 minutes ; le compte
  n'est créé qu'avec le bon code. L'inscription en attente reste en mémoire, rien n'est écrit en
  base avant.
- **Mot de passe oublié** : un code de 8 chiffres par SMS, valable 15 minutes, rangé dans les
  colonnes du code d'activation, puis saisi sur l'écran d'activation avec le nouveau mot de passe.
  Aucun SMS pour un administrateur (une carte SIM volée ne doit pas ouvrir tout le service) ni
  pour un compte suspendu.
- Dans les deux cas, la même réponse que le numéro ait un compte ou non, et au plus 3 codes par
  heure pour un numéro, 10 pour une adresse réseau.

## Alternatives écartées

- **Inscription directe sans preuve** : faille F4 de l'audit.
- **Lien par courriel** : beaucoup d'usagers n'en ont pas.
- **Mot de passe oublié seulement par le centre d'appel** : contraire au critère P1, et le centre
  d'appel n'est pas toujours joignable.
- **Une table des codes pour le mot de passe oublié** : un changement de schéma inutile, les
  colonnes du code d'activation suffisent.

## Conséquences

- De vrais SMS auront un coût à la mise en service (question posée à la cliente).
- Un code demandé par SMS remplace un code remis par l'équipe : la personne qui en a reçu un
  du centre d'appel doit utiliser le plus récent.
- En démonstration (`LOAD_DEMO_DATA`), les codes sont fixes : `123456` et `12345678`.
