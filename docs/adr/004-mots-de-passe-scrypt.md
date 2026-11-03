# 004. Mots de passe et codes hachés en scrypt, avec limites d'essais

- **Statut** : Acceptée
- **Date** : décidée le 19/10/2026 ; limites renforcées le 02/11/2026 (audit, F5)
- **Voir aussi** : [audit de sécurité](../audit-securite-2026-11-02.md), [007](007-etat-en-memoire.md)

## Contexte

Le cahier des charges exige des mots de passe hachés (P1) et une limitation des abus (P2). Les
codes d'activation et les codes SMS ouvrent un compte aussi sûrement qu'un mot de passe. L'audit
du 02/11 a mesuré qu'un hachage coûte environ 110 ms et 32 Mo : sans limite, quelques dizaines de
requêtes suffisent à bloquer l'API.

## Décision

Mots de passe et codes hachés en **scrypt** par Werkzeug (déjà installé avec Flask), comparés en
temps constant, et un faux hachage quand le compte n'existe pas, pour ne pas révéler qui a un
compte. Au plus 4 hachages en même temps, sinon `429`. Les essais sont comptés **avant** le
hachage : 5 échecs en 15 minutes par numéro, 30 par adresse réseau.

## Alternatives écartées

- **bcrypt ou Argon2** : aussi solides, mais une dépendance de plus, alors que Werkzeug fournit
  déjà scrypt.
- **Hachage rapide (SHA-256, même salé)** : cassable en masse si la base fuit.
- **CAPTCHA** : pénible pour un public peu à l'aise avec le numérique, et souvent illisible sur un
  petit écran.

## Conséquences

- Les limites sont en mémoire, valables pour un seul processus de l'API ([007](007-etat-en-memoire.md)).
- Une association qui inscrit plusieurs personnes depuis la même connexion reste sous les
  limites par adresse, réglées larges exprès.
