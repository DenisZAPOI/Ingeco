# Comptes des services externes : ouverture et passation

L'application s'appuie sur des services en ligne qui demandent un compte (le dépôt du code, une
clé d'API…). Le cahier des charges (§20) fixe trois règles :

- ces comptes sont ouverts **au nom d'Ingeco Territoires ou de l'IUT**, jamais au nom personnel
  d'un étudiant ;
- **0 € de licence, aucune carte bancaire personnelle** : uniquement des offres gratuites ou des
  modes test ;
- les **accès sont remis à la fin du projet** (vers le 10/01/2027), pour que l'application puisse
  continuer sans nous.

## Les comptes

| Service | À quoi il sert | Où va l'accès | Aujourd'hui |
|---|---|---|---|
| **GitHub** (dépôt `DenisZAPOI/Ingeco`) | Le code, son historique, les vérifications automatiques (CI), les demandes à l'équipe BD | Invitations sur le dépôt | Compte personnel de Denis ZAPOI. **À transférer** à un compte ou une organisation d'Ingeco ou de l'IUT (choix à faire avec la cliente) |
| **OpenRouteService** | Recherche d'adresses et distance par la route (données OpenStreetMap) | `ORS_API_KEY` dans `BACKEND/.env` | Facultatif : sans clé, lieux fictifs. Compte à ouvrir au nom d'Ingeco ou de l'IUT avant la mise en service. Quotas gratuits à vérifier |
| **Hébergement de la démo** | Mettre l'application en ligne | Selon l'hébergeur choisi | Pas encore choisi (fin de projet) |
| **Prestataire de paiement** (Stripe ou équivalent) | Payer un trajet par carte | Clés dans `BACKEND/.env` | Pas utilisé : paiement simulé dans l'API. Si on en branche un, **mode test uniquement**, compte au nom d'Ingeco |
| **Envoi de SMS** | Codes d'inscription, alertes de trajet | Clés dans `BACKEND/.env` | Pas utilisé : SMS simulés, écrits dans les journaux de l'API |

Tout nouveau service s'ajoute à ce tableau **avant** d'être utilisé, avec sa fiche de décision
([docs/adr/](adr/README.md)).

## Ouvrir un compte

1. Demander à la cliente (ou à l'IUT) **l'adresse e-mail** à utiliser : une adresse de la
   structure, pas celle d'un étudiant.
2. Choisir l'**offre gratuite** ou le **mode test**. Si le service demande une carte bancaire,
   s'arrêter et en parler à la cliente.
3. Noter dans le tableau ci-dessus le service, l'adresse du compte et la date d'ouverture (jamais
   le mot de passe ni la clé).

## Ranger les accès

- Les **clés d'API** vont seulement dans les fichiers `.env`, qui ne sont jamais envoyés sur
  GitHub. Jamais dans le code, jamais dans un message WhatsApp ou un e-mail.
- Les **mots de passe des comptes** se transmettent de vive voix ou par un gestionnaire de mots de
  passe partagé avec la cliente, jamais par écrit en clair.

## Remettre les accès en fin de projet

Pour la suite (passer du démonstrateur à un vrai service : options, chantiers, ordre conseillé),
voir [passage-en-production.md](passage-en-production.md).

Avant le 10/01/2027, avec la cliente, pour chaque compte du tableau :

1. **Donner la main** : transférer le dépôt GitHub (Settings → General → Danger Zone → *Transfer
   ownership*) ; pour les autres services, passer l'adresse e-mail et le mot de passe du compte à
   ceux de la cliente.
2. **Changer les clés** : en créer de nouvelles depuis le compte, les mettre dans le `.env` de
   l'application en ligne, puis supprimer les anciennes, que les étudiants connaissaient.
3. **Retirer l'accès des étudiants** (invitations GitHub, membres des comptes).
4. **Noter la remise** dans la note de transmission : quel compte, remis à qui, quand.
