# 006. SMS simulés dans les logs, sans donnée personnelle

- **Statut** : Acceptée
- **Date** : décidée le 02/11/2026 (premier SMS : expiration d'une course sans chauffeur)
- **Voir aussi** : [005](005-codes-sms.md), [decisions.md](../decisions.md) (Q14)

## Contexte

Le cahier des charges impose des SMS simulés et interdit l'envoi massif réel. Le RGPD interdit de
mettre un numéro ou un contenu personnel dans les journaux. Il faut pourtant pouvoir montrer en
démonstration qu'un SMS est parti.

## Décision

Un seul fichier envoie les SMS : `repository/sms_repository.py`. En simulation, il écrit une
ligne de journal par SMS avec son **type** (`registration_code`, `ride_expired_no_driver`…) et
l'identifiant du compte, **jamais** le numéro, le texte ni le code.

## Alternatives écartées

- **Vraie passerelle SMS** (Twilio, OVH…) : coût, compte bancaire, et contraire aux règles du
  projet.
- **Journal de démonstration avec le contenu des SMS** (que le cahier des charges suggère) : il
  contiendrait des codes qui ouvrent des comptes. On a choisi des codes fixes en démonstration
  plutôt qu'un journal lisible ([005](005-codes-sms.md)).

## Conséquences

- Passer à une vraie passerelle ne change qu'un fichier.
- Hors démonstration, les codes sont aléatoires et écrits nulle part : impossible de les lire,
  même pour l'équipe.
