# Charte graphique

Ce document fixe **à quoi ressemble l'application et comment on écrit ses textes**, pour que
chaque écran, quel que soit le développeur, ait le même aspect et se comprenne de la même façon.

Les valeurs vivent dans un seul fichier : [`FRONTEND/src/styles/global.css`](../FRONTEND/src/styles/global.css).
Ce document explique **pourquoi** elles sont ainsi et **quand** utiliser chacune. Si les deux ne
disent pas la même chose, c'est un bug : corriger l'un ou l'autre dans la même pull request.

## Sommaire

1. [Principes](#1-principes)
2. [Couleurs](#2-couleurs)
3. [Typographie](#3-typographie)
4. [Espacements, formes, tailles](#4-espacements-formes-tailles)
5. [Mise en page](#5-mise-en-page)
6. [Composants](#6-composants)
7. [Textes et ton](#7-textes-et-ton)
8. [Accessibilité](#8-accessibilité)
9. [Images et icônes](#9-images-et-icônes)
10. [Règles pour le code](#10-règles-pour-le-code)
11. [Liste de contrôle d'un nouvel écran](#11-liste-de-contrôle-dun-nouvel-écran)

---

## 1. Principes

Le public : des personnes en insertion, des seniors, des personnes à mobilité réduite, souvent
peu à l'aise avec le numérique, sur un téléphone Android d'entrée de gamme, en plein soleil, avec
un réseau faible. Chaque choix en découle.

1. **Une action principale par écran.** Un seul gros bouton vert ; le reste est secondaire.
2. **Gros, lisible, contrasté.** Texte de base à 18 px, cibles tactiles de 58 px de haut, contrastes
   bien au-dessus du minimum légal.
3. **Des mots simples.** Le texte dit ce qui se passe et quoi faire, sans jargon.
4. **Léger.** Police du téléphone, aucune image lourde, aucune bibliothèque d'interface.
5. **Pareil partout.** Un bouton, un champ, un message d'erreur ont toujours la même forme et la
   même place.

Thème **clair uniquement** : un seul thème à tester, et le meilleur contraste à l'extérieur.

---

## 2. Couleurs

Vert forêt et jaune soleil : l'identité de l'application, qui évoque la Guyane.

| Variable | Valeur | Usage | Contraste |
|---|---|---|---|
| `--color-primary` | `#0b5d3b` | Bouton principal, en-tête, liens, éléments actifs | 7,95:1 sur blanc |
| `--color-primary-hover` | `#08452c` | Survol du vert | 11,06:1 sur blanc |
| `--color-primary-soft` | `#e3efe9` | Fond léger vert (survol du bouton secondaire, message de réussite) | Texte vert dessus : 6,73:1 |
| `--color-on-primary` | `#ffffff` | Texte et bordures posés sur le vert | 7,95:1 |
| `--color-accent` | `#f2b705` | Anneau de focus dans l'en-tête, petits repères | **Jamais sur fond blanc** (1,82:1) ; 4,37:1 sur le vert ; texte foncé dessus : 9,57:1 |
| `--color-text` | `#1a1a1a` | Texte courant | 17,4:1 sur blanc |
| `--color-muted` | `#555555` | Texte secondaire (aide, note) | 7,46:1 sur blanc, 6,81:1 sur `surface` |
| `--color-background` | `#ffffff` | Fond de page, fond des champs | |
| `--color-surface` | `#f3f5f4` | Fond d'un encadré (`.panel`) | |
| `--color-border` | `#6b6b6b` | Bordure des champs | 5,33:1 sur blanc |
| `--color-error` | `#b3261e` | Erreur : texte, bordure du champ fautif | 6,54:1 sur blanc, 5,62:1 sur `error-soft` |
| `--color-error-soft` | `#fbeaea` | Fond d'un message d'erreur | |
| `--color-success` | `#0b5d3b` | Réussite (même vert) | |
| `--color-success-soft` | `#e3efe9` | Fond d'un message de réussite | |
| `--color-focus` | `#1a1a1a` | Anneau de focus (jaune dans l'en-tête) | 17,4:1 sur blanc |

Règles :

- **La couleur n'est jamais la seule information.** Une erreur a un texte ; une règle de mot de
  passe remplie a une coche ✓ ; un état a un mot.
- Le **vert** signale ce qu'on peut faire ou ce qui a réussi, le **rouge** uniquement une erreur.
- Pas de nouvelle couleur sans l'ajouter ici, avec son contraste mesuré (minimum 4,5:1 pour un
  texte, 3:1 pour une bordure ou une icône).

---

## 3. Typographie

**Police du système** (`--font-family`) : Roboto sur Android, San Francisco sur iPhone, Segoe UI
sur Windows. Zéro octet à télécharger, et des caractères que l'utilisateur connaît déjà.

| Élément | Taille | Graisse | Variable |
|---|---|---|---|
| Texte courant | 18 px (`1rem`) | normale | taille de `:root` (112,5 %) |
| Petit texte (mentions) | 16 px, **jamais moins** | normale | `--font-size-small` |
| Titre de page `h1` | 31,5 px | 700 | `--font-size-h1` |
| Titre de partie `h2` | 24,75 px | 700 | `--font-size-h2` |
| Libellé de champ, bouton, message | 18 px | 600 | `--font-weight-strong` |

- Interligne 1,5 pour le texte, plus serré pour les titres.
- **Un seul `h1` par écran**, qui dit où l'on est (« Se connecter », « Mon profil »). Puis des
  `h2` dans l'ordre, sans sauter de niveau.
- Pas de texte en majuscules, pas d'italique pour l'information importante : ils se lisent moins
  bien. Le gras sert à une donnée clé (un numéro, un prix), pas à des phrases entières.
- Tailles en `rem` : l'utilisateur qui agrandit le texte de son téléphone agrandit tout l'écran.

---

## 4. Espacements, formes, tailles

| Variable | Valeur | Usage |
|---|---|---|
| `--space-xs` | 4,5 px | Libellé ↔ champ |
| `--space-s` | 9 px | Champ ↔ bouton accolé |
| `--space-m` | 13,5 px | Marge intérieure d'un champ, d'un message |
| `--space` | 18 px | Espacement de base : entre deux champs, marges de page |
| `--space-l` | 27 px | Entre deux blocs |
| `--space-xl` | 36 px | Avant un titre de partie |
| `--radius` | 13,5 px | Coins de tout ce qui est cliquable ou encadré |
| `--border-width` | 2 px | Bordures de champ et de bouton |
| `--focus-width` | 3 px | Anneau de focus |
| `--touch-target` | 58,5 px | **Hauteur minimale** de tout ce qui se touche (le minimum recommandé est 48 px) |
| `--checkbox-size` | 27 px | Case à cocher |
| `--content-width` | 720 px | Largeur maximale du contenu |

On n'invente pas d'espacement : on prend le plus proche dans cette échelle.

---

## 5. Mise en page

- **Pensée pour le téléphone d'abord** (largeur de référence : 360 à 400 px), puis centrée sur
  ordinateur, à 720 px de large au plus.
- **Une seule colonne.** Un champ par ligne, en pleine largeur.
- **En-tête** vert : le nom de l'application (retour à l'accueil) à gauche, « Se déconnecter » à
  droite pour un utilisateur connecté. Rien d'autre.
- **Ordre d'un écran** : titre `h1`, une phrase d'explication si besoin, le contenu, puis le
  bouton principal **en bas, en pleine largeur** (`button-block`), puis les liens secondaires.
- Jamais de défilement horizontal. Vérifier chaque écran à 360 px de large.

---

## 6. Composants

Toujours réutiliser ces composants et ces classes ; un besoin nouveau → un nouveau composant
dans `components/`, documenté ici.

### Boutons

| Classe | Rendu | Quand |
|---|---|---|
| `button` | Fond vert, texte blanc | **L'action principale**, une seule par écran |
| `button button-secondary` | Fond blanc, bordure et texte verts | Les autres actions (« Afficher », « J'ai reçu un code ») |
| `button-block` | Pleine largeur | Boutons d'un formulaire ou d'un choix sur téléphone |
| `header-action` | Bordure blanche sur le vert | Action de l'en-tête uniquement |

- Le libellé est un **verbe** qui dit ce qui va se passer : « Créer mon compte », « Valider »,
  « Réserver ce trajet ». Jamais « OK », « Envoyer » seul ou « Cliquez ici ».
- Pendant l'envoi, le bouton est désactivé et dit « Envoi en cours… » (composant `Form`).
- Une action qui change de page est un lien (`<Link className="button">`), une action qui agit
  est un `<button>`.

### Formulaires

| Composant | Rôle |
|---|---|
| `Form` | Le formulaire, son message général et son bouton principal en bas |
| `TextField` | Libellé au-dessus, aide éventuelle, champ, erreur en dessous |
| `PasswordField` | Champ masqué avec « Afficher » ; pour un nouveau mot de passe, la liste des règles cochées pendant la saisie |
| `CheckboxField` | Case de 27 px ; toute la ligne est cliquable |

- **Le libellé est toujours visible**, au-dessus du champ. Le texte grisé dans le champ
  (`placeholder`) ne donne qu'un exemple (« 0694 12 34 56 »), jamais la consigne.
- Un champ facultatif le dit dans son libellé : « Adresse e-mail (facultatif) ». Les autres sont
  obligatoires, sans astérisque.
- Le bon clavier et le remplissage automatique : `type="tel"` et `inputMode="tel"` pour un
  téléphone, `inputMode="numeric"` pour un code, `autoComplete` toujours renseigné.
- **Une erreur s'affiche sous son champ**, en rouge et en texte, avec la bordure du champ en
  rouge. Le message général (« Vérifiez les informations en rouge. ») s'affiche au-dessus du
  bouton et reçoit le focus.

### Messages

| Classe | Quand |
|---|---|
| `alert alert-error` | Échec d'un envoi, erreur de chargement (avec « Réessayer ») |
| `alert alert-success` | Confirmation d'un enregistrement |
| `note` | Information secondaire, en gris (« Mot de passe oublié ? … ») |
| `panel` | Encadré gris clair pour regrouper une information (état du service, récapitulatif) |

Un message d'erreur porte `role="alert"`, une confirmation `role="status"` : un lecteur d'écran
les annonce.

### Chargement et erreur

Chaque appel au réseau passe par `RequestState` : « Chargement… » pendant l'attente, puis le
contenu, ou un message d'erreur avec un bouton « Réessayer ». Jamais d'écran blanc, jamais de
roue qui tourne sans fin (le client abandonne au bout de 15 s).

---

## 7. Textes et ton

- **Vouvoiement**, phrases courtes (moins de 15 mots si possible), une idée par phrase.
- **Les mots de l'usager**, pas ceux du code : « trajet » (pas « course » côté usager),
  « chauffeur », « bon solidaire », « centre d'appel », « J'ai reçu un code ». Côté chauffeur, on
  parle de « course ».
- **Un message d'erreur dit ce qui ne va pas et quoi faire** : « Numéro de téléphone invalide.
  Exemple : 0694 12 34 56. », « Trop d'essais. Réessayez dans 15 minutes. ». Jamais de code
  technique ni de mot anglais.
- Pas de sigle sans explication (pas de « PMR » seul : « véhicule adapté (fauteuil roulant) »).
- Formats français :

| Donnée | Format |
|---|---|
| Téléphone | `0694 12 34 56` (enregistré en `+594…`, affiché par `formatPhone`) |
| Prix | `12,50 €` (virgule, espace insécable avant €) |
| Date | `lundi 14 octobre` (l'année seulement si ce n'est pas l'année en cours) |
| Heure | `14 h 30` |
| Distance | `11,4 km` |

Les dates et heures s'affichent **à l'heure de Guyane**, quelle que soit l'heure du téléphone.

---

## 8. Accessibilité

Exigée par le cahier des charges (personnes à mobilité réduite, public peu à l'aise avec le
numérique). Objectif : niveau AA du référentiel WCAG.

- Contraste : 4,5:1 minimum pour un texte, 3:1 pour une bordure ou une icône (voir
  [Couleurs](#2-couleurs)).
- **Tout se fait au clavier**, et l'élément actif se voit : anneau de 3 px, foncé sur fond clair,
  jaune sur le vert de l'en-tête. Ne jamais supprimer `outline`.
- Toute zone qui se touche fait au moins `--touch-target` de haut.
- Chaque champ a un `<label>` relié ; l'erreur et l'aide sont reliées par `aria-describedby`
  (déjà fait dans `TextField`, `PasswordField`, `CheckboxField`).
- L'écran reste utilisable avec le texte agrandi à 200 %.
- Les animations sont coupées si le téléphone le demande (`prefers-reduced-motion`).
- La langue de la page est le français (`lang="fr"`).
- Un texte réservé aux lecteurs d'écran utilise la classe `visually-hidden`.

---

## 9. Images et icônes

- **Pas de photo, pas d'illustration décorative** : chaque kilo-octet compte sur le réseau
  guyanais.
- Une icône n'est jamais seule : elle accompagne un texte. Si elle est décorative,
  `aria-hidden="true"`.
- Icônes et logo en **SVG** intégré, dans les couleurs de la charte.
- Le logo actuel (`public/favicon.svg`) : une route vers l'horizon et un soleil jaune sur un carré
  vert arrondi. À remplacer si le client fournit le sien.
- La carte (étape 4) utilise les tuiles OpenStreetMap ; les repères (usager, chauffeur, arrivée)
  suivront les couleurs de la charte.

---

## 10. Règles pour le code

- **Aucune couleur, taille ou marge en dur** dans un composant ni dans une règle CSS : toujours
  une variable de `global.css`. Une valeur manquante s'ajoute dans `:root`, puis dans ce document.
- Pas d'attribut `style` dans le JSX, sauf valeur calculée (une position sur la carte, par
  exemple).
- Réutiliser les composants de `components/form/` et `components/ui/` avant d'en écrire un.
- Une nouvelle classe porte un nom qui dit ce qu'elle est (`ride-summary`), pas à quoi elle
  ressemble (`green-box`).
- Pas de bibliothèque d'interface ni de police web : décision prise pour la légèreté (voir
  [architecture.md](architecture.md)).

---

## 11. Liste de contrôle d'un nouvel écran

1. Un `h1` qui dit où l'on est, une seule action principale, en bas, en pleine largeur.
2. Uniquement des composants et des classes de cette charte, aucune valeur en dur.
3. Textes relus : vouvoiement, mots simples, verbes sur les boutons, erreurs qui disent quoi faire.
4. État de chargement et état d'erreur avec « Réessayer ».
5. Testé à 360 px de large : pas de défilement horizontal, tout se touche facilement.
6. Testé au clavier : tout est accessible, le focus se voit.
7. Texte agrandi à 200 % : rien ne se chevauche.
