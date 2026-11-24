# En route pour l'emploi

Une application pour se rendre à l'emploi en Guyane : s'orienter (questionnaire et plan
d'action), trouver une offre, une formation ou un service d'aide, et surtout **s'y rendre**,
grâce à un service de trajets solidaires qui met en relation usagers et chauffeurs.

Client : **Ingeco Territoires** (association loi 1901). Projet de BUT 3 Informatique, IUT de
Montreuil.

> **Projet étudiant — démonstrateur.** Les comptes, les offres et les trajets sont des exemples ;
> le paiement et les SMS sont simulés : aucune carte n'est débitée, aucun SMS n'est envoyé.

**Auteurs** : Denis ZAPOI, Yanis OUADAH, Baptiste DURAND-KEOHAVONG, Kurtys TSHIBOLA, Boude
HANOUNE (rôles dans [AUTHORS](AUTHORS), repris dans la page « À propos » de l'application).

**Sommaire**

- [Partie 1 — Lancer l'application](#partie-1--lancer-lapplication) : pour tout le monde, sans
  rien connaître à la programmation
- [Partie 2 — Développeurs et équipe base de données](#partie-2--développeurs-et-équipe-base-de-données)

---

# Partie 1 — Lancer l'application

Suivre les étapes dans l'ordre et **copier-coller** les commandes sans les modifier.

**Il faut** : un ordinateur Windows 10 ou 11 (sur Mac, même principe), Internet, 5 Go libres, et
environ 45 minutes la première fois. Ensuite, l'application démarre en une minute.

Les étapes 1 à 4 ne se font **qu'une fois**.

### 1. Installer Docker Desktop

Docker Desktop est un programme gratuit qui installe et lance toute l'application.

1. Télécharger **Docker Desktop pour Windows** sur https://www.docker.com/products/docker-desktop/.
2. L'installer en gardant les choix proposés, puis **redémarrer** l'ordinateur si demandé.
3. Ouvrir Docker Desktop, accepter les conditions (on peut passer la création de compte avec
   **« Skip »**) et attendre **« Engine running »** en bas à gauche.

Docker Desktop doit être **ouvert** chaque fois qu'on utilise l'application.

### 2. Télécharger le projet

1. Sur https://github.com/DenisZAPOI/Ingeco, cliquer sur le bouton vert **« Code »**, puis
   **« Download ZIP »**.
2. Clic droit sur le fichier téléchargé, **« Extraire tout… »**, puis déplacer le dossier
   `Ingeco-main` sur le **Bureau**.

**Ouvrir une fenêtre de commandes dans ce dossier** (on en aura besoin à chaque étape) : ouvrir
le dossier `Ingeco-main`, cliquer dans la **barre d'adresse** en haut, taper **`cmd`** puis
**Entrée**. Une fenêtre noire s'ouvre : on y colle les commandes (clic droit) et on valide avec
**Entrée**.

### 3. Créer le fichier de réglages

L'application a besoin de trois mots de passe propres à chaque ordinateur. Dans la fenêtre noire :

1. Copier le fichier de réglages d'exemple :

   ```bat
   copy .env.example .env
   ```

2. Fabriquer un mot de passe au hasard, **trois fois** (flèche du haut puis Entrée pour relancer) :

   ```bat
   powershell -NoProfile -Command "$b=New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); -join ($b | ForEach-Object { $_.ToString('x2') })"
   ```

3. Ouvrir les réglages avec `notepad .env`. Sur les lignes `MYSQL_ROOT_PASSWORD=`,
   `MYSQL_PASSWORD=` et `FLASK_SECRET_KEY=`, remplacer le texte après le `=` par **l'un** des trois
   mots de passe (sélection à la souris, `Ctrl + C`, `Ctrl + V`), sans espace. Enregistrer
   (`Ctrl + S`) et fermer, sans toucher aux autres lignes.

Ces mots de passe ne se partagent pas : chacun crée les siens.

### 4. Construire et lancer l'application

```bat
docker compose up -d --build
```

La première fois : **5 à 15 minutes**. C'est fini quand des lignes `Started` ou `Healthy`
s'affichent et que la fenêtre attend une nouvelle commande.

### 5. Ouvrir l'application

Aller sur **http://localhost:5173** dans Chrome, Edge ou Firefox. Pour la voir comme sur un
téléphone : `F12`, puis `Ctrl + Maj + M`.

### Comptes de test

Des personnes fictives, déjà créées. **Mot de passe de tous les comptes : `Trajet-2026!`**

| Pour essayer… | Téléphone | Compte |
|---|---|---|
| Réserver un trajet | `0694 00 00 01` | Alice, usager |
| Accepter et conduire une course | `0694 00 00 03` | Chloé, chauffeur |
| Gérer les comptes | `0694 00 00 06` | Farid, administrateur |

- **Créer un compte** : avec un numéro inventé commençant par 0694. Le code « reçu par SMS » est
  toujours **`123456`**.
- **Mot de passe oublié** : le code est toujours **`12345678`**.
- **Jouer l'usager et le chauffeur en même temps** : ouvrir une fenêtre de navigation privée
  (`Ctrl + Maj + N`) et s'y connecter avec l'autre compte.

Tous les comptes de test : [docs/developpement.md](docs/developpement.md#comptes-de-test--détails).

### Les fois suivantes

Ouvrir Docker Desktop, attendre « Engine running », puis dans une fenêtre noire ouverte dans
`Ingeco-main` :

| Pour… | Commande |
|---|---|
| Lancer l'application | `docker compose up -d` |
| L'arrêter | `docker compose down` |
| Installer une nouvelle version (nouveau ZIP, avec son ancien `.env` recopié dedans) | `docker compose up -d --build` |

#### Remettre la démo à zéro

Les comptes et les trajets reviennent à leur état de départ (l'application doit être lancée) :

```bash
docker compose exec db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --default-character-set=utf8mb4 "$MYSQL_DATABASE" < /sql/demo-data.sql'
```

Pour tout effacer et repartir d'une base neuve : `docker compose down -v`, puis
`docker compose up -d`.

### En cas de problème

| Ce qu'on voit | Ce qu'il faut faire |
|---|---|
| `'docker' n'est pas reconnu…` | Docker Desktop n'est pas installé, ou l'ordinateur n'a pas redémarré : refaire l'étape 1, puis rouvrir la fenêtre noire |
| `error during connect` ou `Is the docker daemon running?` | Ouvrir Docker Desktop, attendre « Engine running », relancer la commande |
| `no configuration file provided` | La fenêtre noire n'est pas dans le dossier `Ingeco-main` (étape 2) |
| `required variable … is missing` ou `FLASK_SECRET_KEY must be generated` | Le fichier `.env` est incomplet : refaire l'étape 3, puis `docker compose up -d` |
| `port is already allocated` | L'application tourne déjà, ou un autre programme prend la place : `docker compose down`, puis relancer ; sinon redémarrer l'ordinateur |
| La page ne s'ouvre pas, ou « Le service ne répond pas » | Attendre une minute après `docker compose up -d`. Sinon, dans Docker Desktop, onglet **Containers**, regarder si un conteneur est rouge |
| Mot de passe refusé | `Trajet-2026!` : majuscule au début, point d'exclamation à la fin. Hugo (`0694 00 00 08`) est volontairement suspendu |

Si le problème continue : copier le texte de la fenêtre noire et l'envoyer à un développeur, avec
une capture d'écran.

---

# Partie 2 — Développeurs et équipe base de données

**Stack** : Python 3.14 et Flask (API), React 19 et TypeScript (interface, PWA), MySQL 8.4 (base,
dans Docker). Swagger de l'API : http://localhost:5000/apidoc/swagger.

**Démarrage rapide en développement** (prérequis : Python 3.14, Node.js 24, Docker) :

```bash
# 1. La base (depuis la racine du dépôt)
git clone https://github.com/DenisZAPOI/Ingeco.git && cd Ingeco
cp .env.example .env                 # remplacer les deux mots de passe et FLASK_SECRET_KEY
docker compose up -d db              # la base seule, port 3307

# 2. L'API (un terminal, dans BACKEND/)
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt
cp .env.example .env                 # générer FLASK_SECRET_KEY
.venv/Scripts/python -m app          # http://localhost:5000

# 3. L'interface (un autre terminal, dans FRONTEND/)
npm install && cp .env.example .env
npm run dev                          # http://localhost:5173
```

**Où trouver quoi**

| Pour… | Lire |
|---|---|
| Installer, lancer, tester, ports, comptes de test, règles de travail | [docs/developpement.md](docs/developpement.md) |
| Organisation du code et règles de chaque couche (**avant d'écrire du code**) | [docs/architecture.md](docs/architecture.md) |
| L'équipe base de données : `sql/`, migrations, vues, export, demandes de schéma | [docs/guide-equipe-bd.md](docs/guide-equipe-bd.md) |
| Le besoin du client (le cahier des charges est la source de vérité) | [cahier des charges v1.0](docs/cahier-des-charges-v1.0.docx), [expression des besoins](docs/expression-des-besoins.pdf) |
| Ce qui est décidé, et les valeurs provisoires | [docs/decisions.md](docs/decisions.md) |
| Le pourquoi de chaque choix technique | [docs/adr/](docs/adr/README.md) |
| Couleurs, composants, ton des textes | [docs/charte-graphique.md](docs/charte-graphique.md) |
| Contrat d'API, cas d'utilisation | [docs/contrat-api.md](docs/contrat-api.md), [docs/cas-d-utilisation.md](docs/cas-d-utilisation.md) |
| Comptes des services externes (GitHub, OpenRouteService…) et leur passation | [docs/comptes-externes.md](docs/comptes-externes.md) |
| Passer du démonstrateur à un vrai service | [docs/passage-en-production.md](docs/passage-en-production.md) |
| Ce qui reste à faire | [docs/reste-a-faire-2026-11-22.md](docs/reste-a-faire-2026-11-22.md) |

**Règles essentielles** : pas de push sur `main`, une branche et une pull request relue par
fonctionnalité ; la CI doit passer pour merger ; secrets dans `.env`, jamais sur GitHub ; aucune
donnée personnelle réelle dans les tests ; les développeurs ne modifient pas `sql/` (sauf
`sql/demo-data.sql`).
