# Accueil de mespilotis — constats observés

Audit réel du 19 septembre 2026, fait en session locale sur le Mac, là où vivent le code et la skill.
Complète la grille [`mespilotis-accueil-ux-audit.md`](mespilotis-accueil-ux-audit.md), écrite sans accès au site.

**Méthode.** Lecture du générateur (`scripts/build_dashboard.py`, `scripts/render_hub.py`, `scripts/render_common.py`, `scripts/deploy-pages.sh`), build local (`python3 scripts/build_dashboard.py`, sans rafraîchissement Pennylane, sans déploiement), site servi en local, captures pleine page à 390 px et 1440 px avec mesures dans la page (hauteurs, tailles de police, contrastes).

**Captures.** [`mespilotis-accueil-mobile.png`](mespilotis-accueil-mobile.png) et [`mespilotis-accueil-desktop.png`](mespilotis-accueil-desktop.png). Ce dépôt étant **public**, les captures poussées ici sont **anonymisées** : chiffres remplacés par des zéros, clients par « CLIENT A, B… », courbe de trésorerie retirée. La mise en page est intacte, à un détail près : un libellé de navigation raccourci rend le menu mobile un peu plus court que le vrai (341 px mesurés sur la page réelle). Les captures réelles restent sur le Mac. Aucun montant ni nom de client n'est repris dans cette note.

Les chemins `scripts/…`, `data/…`, `skills/…` sont relatifs au projet mespilotis (dossier local `+++PRO/CLAUDE`), pas à ce dépôt.

---

## 0. Ce qui change par rapport à la grille

La grille supposait un accueil qui serait soit une redirection vers Pilote, soit un hub de tuiles. **Ni l'un ni l'autre.** Le hub `/dashboard/` a été refondu le 18 septembre, la veille de la grille (`scripts/render_hub.py:1-18`, « audit UX + maquette validée »). Il fait déjà l'essentiel de la cible du § 5 de la grille :

1. un **verdict en une phrase** (nombre d'urgences + trésorerie à 90 jours) ;
2. les **actions triées** Urgent / Cette semaine / À venir, avec montant, échéance, lien source et case à cocher ;
3. la **trésorerie à 90 jours** selon trois lectures, avec courbe ;
4. une **navigation en trois groupes** avec indicateurs d'état.

Quatre hypothèses de la grille sont donc fausses (B, C en partie, G, H en partie), et le plan d'action doit être recentré : il ne s'agit plus de construire l'accueil mais de **corriger quatre défauts précis** et d'y **brancher le briefing**.

Autres écarts factuels avec la grille :

| La grille disait | Constaté |
|---|---|
| Mises à jour manuelles « tous les un à trois jours » | Build + déploiement **automatiques deux fois par jour** (launchd `com.delarque.deploy-dashboard`, 4 h 50 et 13 h). Dernier déploiement réussi : ce matin. |
| Le cabinet partage le même accueil | Le runbook Access indique que **tout `/dashboard/` est réservé à Sébastien**, plus une application dédiée Foyer (`docs/runbooks/cloudflare-access-foyer.md:8-9`, `scripts/deploy-pages.sh:3-4`). Le cabinet a sa propre page, `/dashboard/pilote/conseil/`. |
| Le brief du matin est produit par la skill « concierge » | **Non.** Le brief vient de la tâche planifiée `briefing-quotidien` (5 h, lun.–sam., console + Telegram). La skill `concierge` est un assistant de boîte mail à la demande (§ 4). |
| Montant IRCEC de fin d'année | Le snapshot des provisions porte un montant **différent** de celui cité dans la grille. La grille citait un mail ; la source à jour est `data/provisions-snapshot.json`. |
| Dix entrées de menu à plat | Dix liens, mais **déjà regroupés** en Activité / Production / Perso. |

---

## 1. La vraie page d'accueil

- `/` → redirection 302 vers `/dashboard/` (`scripts/deploy-pages.sh:93`, fichier `_redirects`). **Pas** de redirection vers `/dashboard/pilote/`.
- `/dashboard/` est le hub, généré en dernier par `build_dashboard.py:326-331` via `render_hub(resume_hub(...))`. Tous ses chiffres viennent des mêmes fonctions que les pages de détail ; chaque bloc est isolé par `_sur()` (`render_hub.py:73-79`) et ne fait jamais tomber le build.
- Page autonome : elle n'utilise pas le gabarit commun `render_page` de `render_common.py`. Conséquence : elle n'hérite **pas** de la ligne de fraîcheur honnête des pages internes (critère C).

---

## 2. Les dix critères

Légende : **Constaté** = le défaut supposé par la grille existe ; **Non constaté** = le défaut n'existe pas (déjà traité) ; **Partiel**.

### A. Friction d'entrée — non vérifiable dans le code, sauf PWA

| Point | Constat | Preuve |
|---|---|---|
| Durée de session Access | **Non vérifiable ici.** Le réglage vit dans Zero Trust, pas dans le dépôt. Le runbook dit seulement « la même que l'application du dashboard ». | `docs/runbooks/cloudflare-access-foyer.md:21` |
| Fournisseur d'identité | **Non vérifiable ici.** Le runbook ne nomme pas la méthode (« un fournisseur d'identité ou One-time PIN »). | idem, l. 24-28 |
| Manifeste PWA | **Constaté : absent.** Aucun `rel="manifest"`, aucun `apple-touch-icon` dans les `render_*.py`. | `grep` sur `scripts/render_*.py` : zéro résultat |

**Reco confirmée**, mais c'est une action de Sébastien dans Zero Trust (le runbook pose la règle : « Claude ne touche pas à Access »). À faire sur **les deux** applications Access (dashboard et Foyer), sinon la seconde personne du foyer garde la friction. Lire la valeur actuelle avant de la changer : c'est la seule hypothèse de la grille qui reste ouverte.

### B. Hiérarchie — non constaté (déjà une vue d'ensemble)

L'accueil répond sans clic aux trois questions du § 1 de la grille : verdict (`render_hub.py:249-267`), actions (`:143-193`), trésorerie (`:341-375`), trois chiffres secondaires (`:378-399`). Les modules sont dans la colonne de navigation avec indicateur quand il sert : « 1 retard » sur Fiscal, « 2 actions » sur Foyer, solde si tension sur Pilote (`:402-440`).

**Reco de la grille corrigée** : inutile de refaire l'accueil en cinq blocs. Le défaut réel est **sur téléphone** (critère H) : la navigation passe avant le verdict.

### C. Fraîcheur — partiel, avec un défaut d'honnêteté

| Point | Constat | Preuve |
|---|---|---|
| Horodatage en tête | **Présent** : « Samedi 19 septembre, données à jour à 9h43 ». | `render_hub.py:449-450`, capture |
| Que dit cette heure ? | **Défaut.** C'est l'heure du *build* (`datetime.now`), pas celle des données. Lors de cet audit, le build local a affiché « données à jour à 9h43 » alors que le snapshot Pennylane datait de 5 h 51. Quand le rafraîchissement Pennylane échoue (cas prévu, non bloquant : `deploy-pages.sh:34-35`), le hub affirme quand même « à jour ». | `data/pennylane-snapshot.json` → `generated_at` |
| Badge au-delà de 48 h | **Absent sur le hub.** La page est statique : ouverte trois jours plus tard, elle affiche toujours la même phrase, sans alerte. L'attribut `data-generated` est posé sur `<body>` (`render_hub.py:587`) mais aucun script ne le lit. | `render_hub.py:595-609` (seul script : les cases à cocher) |
| Pages internes | **Déjà traité, et bien** : pied de page à trois horodatages distincts (données Pennylane + badge « vieilles de N j », dernier déploiement réussi, génération). | `render_common.py:49-81` |
| Build automatique | **Déjà fait** : launchd, 4 h 50 et 13 h ; statut écrit dans `data/deploy-status.json`. | `~/Library/LaunchAgents/com.delarque.deploy-dashboard.plist` |

**Reco corrigée.** Ne pas créer un nouveau système : faire lire au hub le `generated_at` du snapshot (comme `render_common.py:64`) et ajouter dix lignes de JavaScript qui calculent l'âge *à l'ouverture* à partir de `data-generated` (orange > 48 h, rouge > 5 j). Le calcul doit être côté navigateur : un badge calculé au build ne vieillit pas.

### D. Deltas — partiel

- Le CA encaissé porte un delta **daté** : « +N % par rapport au 19 septembre 2025 » (`render_hub.py:128-135`, `:382-386`). C'est un delta sur un an, en pourcentage.
- **Aucun delta « depuis le dernier build / la dernière visite »**, ni sur le CA, ni sur le facturé non encaissé, ni sur la trésorerie.
- La matière existe : `scripts/build_dashboard_history.py` tourne à chaque déploiement (`deploy-pages.sh:40`) et archive un snapshot.

**Reco confirmée, priorité inchangée (P2).** Le hub répond déjà à « qu'est-ce que je dois faire » ; le delta est un confort.

### E. Échéances à 90 jours — constaté (le trou le plus coûteux)

Le hub n'affiche que **deux** sortes d'échéances fiscales : celles **en retard** (`render_hub.py:153-161`) et **la prochaine** (`next_echeance`, `:185-192`). Aujourd'hui : un retard et l'échéance du 15 octobre.

Or `data/provisions-snapshot.json` contient **quatre échéances dans les 90 jours** (mi-octobre, début novembre, acompte de TVA du 15 décembre, régularisation IRCEC du 31 décembre) et un total `totals.total_90j` déjà calculé. L'acompte de TVA et l'IRCEC, les deux exemples de la grille, **ne sont pas sur l'accueil**.

**Reco confirmée, P0.** Dans `_actions`, remplacer le seul `next_echeance` par la boucle sur `prov["echeances"]` dont la date tombe avant aujourd'hui + 90 jours, et afficher `total_90j` dans le titre du groupe « À venir ». La donnée est prête ; c'est une demi-heure.

### F. Qualité des données — constaté

Le bloc existe dans Pilote, en pied de page, replié dans un `<details>` : « Qualité des données : N signal(aux) au dernier build » (`render_pilotage.py:1241-1282`). Il a un compteur, contrairement à l'hypothèse. Mais **rien ne remonte sur le hub** : ni badge, ni compteur. Le seul écho est la phrase « Données Pennylane à rafraîchir » quand le moteur de trésorerie se déclare `stale` (`render_hub.py:346-347`).

**Reco confirmée (P1, remontée d'un cran)** : un indicateur à côté de « Pilote » dans la navigation (« 3 signaux »), au même format que « 1 retard » sur Fiscal. Le mécanisme `hint` existe déjà (`render_hub.py:405-407`). Il faut exposer le compte depuis `render_pilotage` plutôt que le recalculer.

### G. Navigation — non constaté

Dix liens en trois groupes : **Activité** (Pilote, Simulateur, Fiscal, Banque), **Production** (Opérations, Contenu, Revue de presse, Pages cachées, Clauding si peuplé), **Perso** (Patrimoine, Foyer si publié) — `render_hub.py:421-436`. Ordre par usage, pas par date de création. Liens conditionnels masqués quand la page n'a pas de contenu (`:40-49`).

**Reco de la grille abandonnée** : le regroupement « Argent / Maison / Visibilité / Méthode » n'apporte rien de plus. Deux remarques mineures : Méthodologie et la page Conseil ne sont pas dans la navigation du hub ; les pages internes utilisent une autre barre (`render_common.py:148`), donc deux systèmes de navigation cohabitent.

### H. Lisibilité mobile — partiel : bons fondamentaux, un vrai défaut d'ordre

Mesures à 390 × 844 :

| Point | Constat | Preuve |
|---|---|---|
| `tabular-nums` | **Oui**, sur tout le `body`. | `render_hub.py:484` |
| Unités, milliers | **Oui** : espace fine insécable, « € », « HT » explicite, signe moins typographique. | `render_hub.py:36`, `:52-54` |
| Couleurs sémantiques | **Oui** : corail = retard/négatif, ambre = vigilance, sauge = calme ; le verdict est en texte, « la couleur ne porte rien seule ». | `render_hub.py:250`, `:478-479` |
| Bulles méthodo au tap | **Sans objet sur le hub** : aucune bulle, aucun attribut `title` ; les définitions des trois lectures sont écrites en clair sous chaque libellé. Sur les pages internes, la bulle « i » est un `<details>` (tap, Échap, clic extérieur), pas un survol. | mesure : 0 `[title]` ; `render_common.py:672-676` |
| Empilement des chiffres | **Oui** : sous 760 px, montant et échéance passent sous le titre ; sous 1080 px, la trésorerie passe sous les actions. | `render_hub.py:574-584` |
| Taille de corps | **Partiel** : corps à **15 px** (cible de la grille : 16). **29 éléments de texte sous 13 px** (étiquettes « Pro / Foyer », définitions, légendes, axes du graphique à 11 px). | `render_hub.py:484`, mesure |
| Contraste | **Partiel** : texte 15:1, gris moyen 6,9:1, corail 7,1:1, ambre 9,2:1. Mais le gris pâle `--faint` est à **4,0:1** sur les panneaux (seuil AA : 4,5:1), et c'est lui qui porte les textes de 12 px. | calcul WCAG sur `render_hub.py:475-479` |
| Ordre sur téléphone | **Défaut.** La navigation s'affiche **avant** le contenu et occupe 341 px. Le verdict commence à 406 px, la première action à **783 px sur 844** : au premier écran, on voit le menu et le verdict, **aucune action**. | mesure, capture mobile |
| Longueur de page | **Défaut.** 2 961 px, soit **3,5 écrans**. La trésorerie commence à 2 146 px. Sur desktop : 1 225 px, tout tient en 1,4 écran. | mesure |
| Mode sombre | Thème sombre unique (pas de bascule). Convient au soir ; en plein soleil, à éprouver à l'usage. | `render_hub.py:475` |

**Reco corrigée.** La passe mobile de la grille (2 h) se réduit à trois retouches dans le bloc `@media (max-width: 760px)` : (1) replier la navigation dans un `<details>` « Pages » fermé par défaut, ou la renvoyer en bas de page ; (2) passer `--faint` à environ `#8d918a` et les textes de 12 px à 13 px ; (3) corps à 16 px sous 760 px. Gain attendu : verdict + deux premières actions au premier écran.

### I. Publics — non constaté pour l'accueil, à vérifier dans Zero Trust

- D'après le runbook et l'en-tête du script de déploiement, le hub est **réservé à Sébastien** ; Foyer a sa propre application Access (deux adresses). Le cabinet ne voit donc pas le hub, ni Foyer, ni Patrimoine.
- Le cabinet a une page dédiée, `/dashboard/pilote/conseil/` (`build_dashboard.py:220-226`, `audience="conseil"`), avec sa propre barre d'en-tête (`render_common.py:149`).
- **Point à vérifier** : la grille cite des mails disant que Pilote et Fiscal ont été ouverts au cabinet. Si c'est le cas, il existe dans Zero Trust une politique ou une application que le dépôt ne décrit pas. À contrôler avec le testeur de politiques, comme le prévoit le runbook (l. 34-40) : quelles adresses entrent sur `/dashboard/`, `/dashboard/fiscal/`, `/dashboard/perso/` ?
- En-tête `Cf-Access-Authenticated-User-Email` : **non exploité** côté pages (site statique). Le Worker `integrations/mespilotis-api/src/index.js:85-103` fait mieux : il valide le jeton signé `Cf-Access-Jwt-Assertion` et compare l'adresse à `EMAIL_AUTORISE`.

**Reco de la grille abandonnée** (accueil « cabinet » par en-tête) : la séparation par chemin + applications Access existe déjà et elle est plus sûre qu'un affichage conditionnel côté page. Si le cabinet doit avoir une entrée, c'est `/dashboard/pilote/conseil/` qu'il faut lui donner comme adresse d'arrivée.

### J. Rituels — constaté (absent du hub), présent dans le briefing

Le hub ne varie pas selon le jour : `weekday()` ne sert qu'à écrire la date (`render_hub.py:450`). Le groupe « Cette semaine » contient toujours les relances, quel que soit le jour.

La logique de rituel existe **ailleurs** : le briefing quotidien a sa section LinkedIn lun./mer./ven. et sa priorisation URGENT → REVENU → STRATÉGIE. Elle arrivera sur l'accueil avec le branchement du § 4, sans code dédié.

**Reco confirmée en P2**, mais à traiter via le briefing, pas par un bloc « Cette semaine » codé en dur.

### Défaut hors grille : les cases à cocher

Les cases « fait » sont mémorisées dans le `localStorage` du navigateur (`render_hub.py:595-609`) : cochée sur le téléphone, une action reste ouverte sur le Mac, et inversement. Le Worker `mespilotis-api` synchronise déjà « lu / favori » de la page Revue entre appareils via KV ; le même mécanisme peut porter les cases du hub (P2).

---

## 3. Synthèse de la grille

| Critère | Hypothèse de la grille | Verdict |
|---|---|---|
| A. Friction d'entrée | Session par défaut, code e-mail seul | **Ouvert** (Zero Trust, hors dépôt) ; PWA absente : constaté |
| B. Hiérarchie | Redirection ou hub de tuiles | **Faux** : vue d'ensemble avec verdict |
| C. Fraîcheur | Date absente ou en pied de page | **Partiel** : date en tête, mais c'est l'heure du build, et pas de badge d'âge sur le hub |
| D. Deltas | Valeurs absolues | **Partiel** : delta annuel daté sur le CA, rien depuis la dernière visite |
| E. Échéances | Absentes de l'accueil | **Vrai à moitié** : retard + prochaine seulement ; TVA de décembre et IRCEC absentes |
| F. Qualité des données | Bloc textuel sans compteur, en bas de Pilote | **Partiel** : compteur présent dans Pilote, rien sur le hub |
| G. Navigation | Menu linéaire par ordre de création | **Faux** : trois groupes par usage |
| H. Lisibilité mobile | À vérifier | **Partiel** : fondamentaux bons ; navigation avant le contenu, 3,5 écrans, petits textes sous le seuil AA |
| I. Publics | Même page pour tous | **Faux d'après le dépôt** ; à confirmer dans Zero Trust |
| J. Rituels | Absents | **Vrai** sur le hub ; présents dans le briefing |

---

## 4. La skill concierge face au contrat `concierge.json`

### Ce que la skill fait réellement

`skills/concierge/SKILL.md` (dans le projet, pas dans `~/.claude/skills/`) est un **assistant de boîte mail à la demande**, pas un orchestrateur de routines :

1. collecte Gmail en trois passes (`--awaiting-reply`, `--flag-only`, `--fresh`), dédoublonnée par fil ;
2. classement par jugement (projet, intention, sensibilité) ;
3. garde-fou de quota (mode léger si la sonde est illisible — et c'est le cas en permanence tant que `limite_reference_plan` n'est pas calibré) ;
4. production : brouillons Gmail (jamais envoyés), fiches de préparation de devis, transfert des factures fournisseurs à Pennylane, classement des pièces jointes ;
5. sorties : `concierge/AAAA-MM-JJ-state.json` (journal au fil de l'eau) et `concierge/AAAA-MM-JJ-prep.md` (fiche lisible en huit sections).

Dernière fiche produite : 30 juin. Le « step 2 » (tâche planifiée matinale + alimentation du briefing) est noté « à faire » dans la mémoire du projet et n'existe pas.

**Le brief du matin vient d'ailleurs** : la tâche planifiée `~/.claude/scheduled-tasks/briefing-quotidien/SKILL.md` (5 h, lun.–sam.), qui lit TODO, agenda, rappels, Gmail (mêmes scripts que le concierge), CRM Airtable et Pennylane, puis sort un texte en console et un push Telegram. **Elle n'écrit aucun fichier structuré.**

### Contrat proposé vs existant

| Champ du contrat | Existe déjà ? | Où |
|---|---|---|
| `generated_at` | Non | — |
| `day_shape` | En texte | Briefing, section « Agenda » |
| `needs_you[]` | En texte | Briefing : « TOP 3 », « Mails sans réponse », « Rappels en retard », « Décisions bloquantes ». Concierge : sections 1, 4 et 6 de la fiche |
| `done[]` | Partiel | Concierge : `state.json` (brouillons créés, factures transférées, PJ classées). Rien dans le briefing |
| `deadlines[]` | **Oui, et mieux** | `data/provisions-snapshot.json`, calculé par le build. **À retirer du contrat** : la règle 4 de la grille (« aucun montant inventé ») l'impose |
| `data_quality` | **Oui** | `render_pilotage.py:1241+`. **À retirer du contrat**, même raison |
| `routines[]` | Non | Les tâches planifiées n'ont pas de journal commun |

Deux corrections au contrat, donc : il s'appelle **`data/briefing.json`** (c'est le briefing qui l'écrit ; le concierge pourra y ajouter ses brouillons plus tard), et il ne porte **que ce que le build ne sait pas** : mails, agenda, rappels, CRM, décisions. Les relances de factures et de devis, les échéances fiscales et la qualité des données restent calculées par le générateur — sinon le hub affichera deux fois « Relancer CLIENT A », une fois depuis Pennylane, une fois depuis le briefing.

```json
{
  "generated_at": "2026-09-19T05:04:00+02:00",
  "day_shape": "Deux rendez-vous le matin, après-midi libre.",
  "needs_you": [
    { "title": "Répondre à … (3 j sans réponse, relance ×2)",
      "why": "Demande de devis, fil muet de mon côté.",
      "source_url": "https://mail.google.com/mail/u/0/#inbox/<thread_id>",
      "due": "2026-09-19", "kind": "mail", "bucket": "urgent" }
  ],
  "done": [ { "title": "Brouillon prêt : …", "source_url": "…" } ],
  "sources_ko": ["airtable"]
}
```

`kind` ∈ `mail | agenda | rappel | crm | decision | chantier` — **jamais** `relance` ni `fiscal`. `bucket` ∈ `urgent | semaine | a_venir`, pour tomber directement dans les trois groupes du hub. Cinq items au plus, chacun avec une source.

### Le diff minimal

**1. Briefing** — `~/.claude/scheduled-tasks/briefing-quotidien/SKILL.md`, une section ajoutée avant le push Telegram :

> « Écrire `data/briefing.json` (schéma ci-dessus) : les 5 items au plus du TOP 3 + mails sans réponse en RELANCE + rappels en retard + décisions bloquantes, en excluant tout ce qui vient de Pennylane (le hub le calcule). Écriture atomique (fichier temporaire puis renommage). Puis lancer `python3 scripts/build_dashboard.py`. »

**2. Générateur** — `scripts/render_hub.py`, une trentaine de lignes :

- une fonction `_briefing(root, today)` qui lit `data/briefing.json`, rejette le fichier s'il date de plus de 24 h (un briefing d'hier ne doit pas passer pour celui d'aujourd'hui) ou s'il est mal formé, et ne garde que les `kind` autorisés ;
- dans `resume_hub` (`:196-217`) : `briefing = _sur("briefing", _briefing, root, today)` ;
- dans `_actions` (`:143-193`) : verser chaque item dans son groupe, avec `ctx` = « Mail », « Agenda »…, `lien` = (`source_url`, « Ouvrir le fil », externe). Le rendu, les cases à cocher et le compteur d'urgences du verdict fonctionnent sans autre changement ;
- `day_shape` : une phrase ajoutée au paragraphe `.lede` (`:457`) ;
- `done[]` : un `<details>` « Déjà réglé (N) » sous les groupes.

Aucun changement dans `build_dashboard.py` : le hub est déjà généré en dernier et isolé des pannes.

**3. Ordonnancement** — c'est le piège. launchd déploie à **4 h 50**, le briefing tourne à **5 h 00** : le fichier écrit à 5 h 04 ne serait en ligne qu'au déploiement de **13 h**. Deux options : décaler le créneau launchd du matin à 5 h 20 (une ligne dans le plist ; le plus simple), ou faire déclencher le déploiement par le briefing (plus fragile : un briefing qui échoue bloquerait la mise en ligne des chiffres). **Recommandation : décaler à 5 h 20.**

**4. Concierge** — rien dans l'immédiat. Quand son step 2 existera : en fin de Phase 5, ajouter à `data/briefing.json` ses « Réponses préparées » dans `done[]` (lien vers le brouillon) et ses « Flags à trancher » dans `needs_you[]`. `allowed-tools` contient déjà `Write`.

**5. Boutons « Demander au concierge »** — faisables (`navigator.clipboard.writeText`, cinq prompts en dur dans `render_hub.py`), mais **P2** : le hub mène déjà en un clic à la source de chaque action.

**Confidentialité.** `data/briefing.json` contiendra des objets de mails et des noms d'expéditeurs. Le hub est réservé à Sébastien, donc acceptable — à condition que la vérification du critère I confirme que personne d'autre n'entre sur `/dashboard/`. Ne jamais rendre ce bloc sur la page Conseil ni sur Foyer.

---

## 5. Changements concrets dans mespilotis

Rien n'a été modifié dans le projet. Le build local a seulement régénéré `site-web/dashboard/` et `contenu/INDEX.md`, comme le fait chaque déploiement.

### P0 — une session, moins de deux heures

| # | Changement | Fichier | Effort |
|---|---|---|---|
| 1 | **Horodatage honnête + badge d'âge sur le hub.** Afficher le `generated_at` du snapshot Pennylane (pas l'heure du build) ; script qui calcule l'âge à l'ouverture depuis `data-generated` : orange > 48 h, rouge > 5 j. | `scripts/render_hub.py:449-451` et `:595-609` ; réutiliser `_read_json_field` / `_fr_date_iso` de `scripts/render_common.py:49-81` ; test dans `tests/` | 30 min |
| 2 | **Toutes les échéances à 90 jours** dans « À venir », avec le total. | `scripts/render_hub.py:185-192` (boucle sur `prov["echeances"]`, `totals.total_90j`) | 30 min |
| 3 | **Téléphone : le verdict et les actions d'abord.** Navigation repliée ou renvoyée en bas sous 760 px. | `scripts/render_hub.py:575-584` (+ `_nav`, `:437-440`) | 30 min |
| 4 | **Session Access à 1 mois** sur les deux applications ; relever au passage la méthode de connexion et la liste des adresses autorisées (tranche A et I). | Zero Trust — action de Sébastien, hors dépôt | 15 min |

### P1

| # | Changement | Fichier | Effort |
|---|---|---|---|
| 5 | **Brancher le briefing sur le hub** (`data/briefing.json`, § 4). | `~/.claude/scheduled-tasks/briefing-quotidien/SKILL.md` ; `scripts/render_hub.py` (`_briefing`, `resume_hub`, `_actions`, `.lede`) ; `tests/test_render_hub_briefing.py` | 2 h |
| 6 | **Décaler le déploiement du matin à 5 h 20**, après le briefing. | `~/Library/LaunchAgents/com.delarque.deploy-dashboard.plist` | 10 min |
| 7 | **Indicateur qualité des données** à côté de « Pilote ». | `scripts/render_pilotage.py:1241-1282` (exposer le compte) ; `scripts/render_hub.py:409-412` | 45 min |
| 8 | **Lisibilité** : `--faint` au-dessus de 4,5:1, textes de 12 px → 13 px, corps 16 px sous 760 px. | `scripts/render_hub.py:475-497`, `:575` | 30 min |

### P2

| # | Changement | Fichier | Effort |
|---|---|---|---|
| 9 | Deltas datés « depuis le dernier build » sous les trois chiffres. | `scripts/build_dashboard_history.py` ; `scripts/render_hub.py:378-399` | 2 h |
| 10 | Cases à cocher synchronisées entre appareils (KV, comme la Revue). | `integrations/mespilotis-api/src/index.js` ; `scripts/render_hub.py:595-609` | 2 h |
| 11 | Manifeste PWA + icône. | `site-web/dashboard/manifest.webmanifest` (nouveau) ; `<head>` de `scripts/render_hub.py:464-472` et de `scripts/render_common.py` | 45 min |
| 12 | Boutons « Demander au concierge » (5 prompts). | `scripts/render_hub.py` | 1 h |
| 13 | Concierge step 2 : écrire ses brouillons dans `data/briefing.json`. | `skills/concierge/SKILL.md` (Phase 5) | 1 h |

### Abandonné

Refonte de l'accueil en cinq blocs (B), regroupement du menu par question (G), accueil « cabinet » par en-tête Access (I), bloc « Cette semaine » codé en dur (J), `deadlines[]` / `data_quality` / `routines[]` dans le contrat JSON (§ 4).

---

## 6. Résumé

**Constaté.** L'accueil est un vrai cockpit depuis le 18 septembre : verdict, actions triées avec source, trésorerie à trois lectures, navigation groupée avec indicateurs, build automatique deux fois par jour. Les fondamentaux de lisibilité sont bons.

**Ce qui contredit la grille.** Pas de redirection ni de hub de tuiles ; menu déjà regroupé ; build déjà automatique ; le cabinet ne partage pas cet accueil (d'après le dépôt) ; la skill concierge n'est pas l'auteur du brief du matin ; les bulles méthodo sont déjà au tap.

**Les trois changements qui rapportent le plus.**

1. **Échéances à 90 jours sur l'accueil** (P0 n° 2) : la donnée est prête, l'acompte de TVA et l'IRCEC de décembre sont aujourd'hui invisibles. Trente minutes.
2. **Horodatage honnête + badge d'âge** (P0 n° 1) : le hub affirme « à jour » avec l'heure du build, même sur des données de repli. C'est le seul défaut qui peut faire prendre une mauvaise décision.
3. **Le briefing dans le hub** (P1 n° 5 et 6) : un fichier JSON, trente lignes dans `render_hub.py`, un créneau launchd décalé. C'est ce qui fait de l'accueil l'unique endroit du matin.
