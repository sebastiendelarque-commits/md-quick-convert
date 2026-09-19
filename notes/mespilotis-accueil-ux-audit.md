# Audit de l'accueil de mespilotis — UX/UI et productivité quotidienne

Notes du 19 septembre 2026.

> **Statut de cette note (mise à jour du 19 septembre, session locale).** L'audit réel est fait : voir [`mespilotis-accueil-ux-audit-constats.md`](mespilotis-accueil-ux-audit-constats.md) et les deux captures (`mespilotis-accueil-mobile.png`, `mespilotis-accueil-desktop.png`, anonymisées car ce dépôt est public). Cette grille reste le raisonnement de départ ; chaque hypothèse du § 2 porte désormais son verdict. **Le plan d'action du § 6 est remplacé par le § 5 des constats** : l'accueil avait été refondu la veille, et quatre hypothèses sur dix étaient fausses. Pour la même raison (dépôt public), les montants, noms et identifiants de cette grille ont été remplacés par des valeurs fictives.

---

## 0. Ce que j'ai pu établir, et ce que je n'ai pas pu voir

### Ce que je n'ai pas pu voir

| Chemin tenté | Résultat |
|---|---|
| `https://mespilotis.com/` et `/dashboard/` | Bloqué par le proxy réseau de la session (403 au CONNECT), avant même l'écran Cloudflare Access |
| `https://mespilotis.pages.dev/` | Idem |
| Dépôt GitHub `sebastiendelarque-commits/mespilotis` (et `mes-pilotis`) | Introuvable ou non autorisé pour l'app Claude ; seul `md-quick-convert` est visible |
| Skill « concierge » | Absente des skills claude.ai, des skills Notion, de Drive, de Gmail, et d'aucun titre de session sur les 300 dernières (24 août → 19 sept.) |
| Sessions « Mise à jour des pilotis », « Générateur du dashboard », « Dashboard Foyer »… | Sessions *bridge* (locales, sur le MacBook) : le code et la skill vivent sur ta machine, pas dans le cloud |

### Ce que j'ai pu établir

**L'outil.** mespilotis.com est ton cockpit de pilotage d'activité (photographe / vidéaste événementiel B2B). Domaine enregistré le 29 mai 2026 chez Cloudflare, hébergé sur Cloudflare Pages, protégé par Cloudflare Access (code à 6 chiffres reçu par e-mail). Site statique généré par un script Python (`build_dashboard.py`), mis à jour via des sessions Claude Code « Mise à jour des pilotis » tous les un à trois jours.

**Les modules connus** (par les mails et les titres de sessions) :

| Module | Ce qu'on en sait |
|---|---|
| `/dashboard/pilote/` — Pilotage | En haut, 3 chiffres maîtres (CA encaissé, encours, montants facturés). Dessous : cash net à 90 jours, provisions, DSO, concentration client. Chaque chiffre a une bulle « méthodo » ; un bloc « qualité des données » signale ce qui est fragile. Clients récurrents ajoutés le 8 sept. |
| `/dashboard/pilote/simulateur/` — Simulateur d'atterrissage | Projection de fin d'année. |
| `/dashboard/fiscal/` — Fiscal | Année par année : cotisations dues, sorties réelles du compte, optimisations. Ouvert au cabinet le 10 sept. |
| Prévisions cash entrantes / sortantes, frais fixes | Sessions du 11–12 sept. (« fiabilité prévisions et capacité »). |
| Foyer | Spec le 15 sept., implémentation 15–16 sept. |
| Patrimoine / retraite | Relevé de carrière, simulateur retraite (8–9 sept.). |
| Monitoring SEO hebdo, revue de presse, LinkedIn (revue mensuelle, routine nocturne), monitoring sous-traitance, stratégie mensuelle | Routines récurrentes qui alimentent ou accompagnent le site. |
| Glossaire méthodologie (8 fiches) | 12 sept. |

Autrement dit : en trois mois et demi, l'outil est passé de **2 pages** (Pilote + Simulateur, mail du 24 juillet au cabinet) à **une dizaine de modules**. C'est exactement le moment où un accueil se dégrade par accrétion si on ne le redessine pas.

**Les usages.** Trois publics distincts se connectent avec la même page d'entrée :

1. **Toi, le matin** (téléphone, 30 secondes) : où j'en suis, qu'est-ce qui a bougé, qu'est-ce que je dois faire aujourd'hui.
2. **Toi, en session de travail** (desktop, 20 minutes) : facturation, relances, point avant un appel au cabinet, simulation.
3. **Ton cabinet comptable** (deux interlocuteurs) et **un contact extérieur** : lecture ponctuelle, sans ton contexte. Ta comptable a écrit le 11 sept. qu'elle allait « prendre en main Pennylane ainsi que votre tableau de bord afin de voir comment je peux vous aider à optimiser leur utilisation ».

**Le rituel du matin existe déjà ailleurs.** L'artefact « Brief du matin » (31 août) montre le format qui marche pour toi : la journée dessinée en relief, trois blocs horaires, puis « Ce qui a besoin de toi » (5 items max, chacun relié à un fil Gmail) et « Déjà réglé ». Les sessions « Briefing quotidien » tournent quasi tous les jours depuis fin août. **Ce brief et l'accueil de mespilotis sont deux réponses à la même question, à deux endroits.** C'est le principal levier de productivité de cette note (§ 4).

---

## 1. Le rôle d'un accueil dans un outil de pilotage quotidien

Un accueil de cockpit n'est pas un sommaire. Il doit répondre en moins de dix secondes, sans clic, à trois questions :

1. **Où j'en suis** — la santé cash, en trois chiffres, pas plus.
2. **Qu'est-ce qui a changé** depuis ma dernière visite — les mouvements, pas les stocks.
3. **Qu'est-ce que je dois faire aujourd'hui** — trois à cinq actions, chacune avec sa source.

Tout le reste (modules, méthodo, historique) est à un clic, pas sur l'écran d'entrée.

Les mesures de productivité qui comptent, et que tu peux relever toi-même sur une semaine :

| Mesure | Comment la relever | Cible |
|---|---|---|
| Temps entre l'ouverture et la première décision | Chrono, 5 matins | < 30 s sur téléphone |
| Clics pour atteindre le chiffre que tu cherches le plus souvent (encours ? cash 90 j ?) | Compter | 0 (il est sur l'accueil) |
| Ouvertures « pour rien » (aucune action ni info nouvelle) | Coche dans une note | < 1 sur 5 |
| Connexions par jour × durée du code Cloudflare | Compter | 1 connexion / mois (§ 2-A) |
| Doutes sur la fraîcheur (« c'est à jour, ça ? ») | Coche | 0 : la date est affichée |

---

## 2. Grille d'audit (à cocher sur l'écran réel)

Pour chaque critère : pourquoi ça pèse sur ta journée, l'hypothèse que je fais sur l'état actuel, et la recommandation. Verdicts ajoutés après l'audit réel ; preuves dans la note de constats.

### A. Friction d'entrée (Cloudflare Access)

- **Pourquoi.** Chaque connexion = ouvrir la boîte mail, retrouver le code, le recopier. Sur téléphone, c'est 45 secondes et un changement d'appli. Si la session Access expire toutes les 24 h (valeur par défaut), c'est une friction quotidienne, sur chaque appareil.
- **Hypothèse — reste ouverte** (réglage Zero Trust, invisible dans le dépôt ; manifeste PWA : absent, constaté) : durée de session Access laissée par défaut ; connexion par code e-mail uniquement (deux codes demandés à cinq minutes d'écart le 29 mai, signe que le flux est pénible).
- **Reco.** Dans Cloudflare Zero Trust → Access → Applications → mespilotis → *Session duration* : passer à **1 mois** (maximum autorisé). Ajouter **Google** comme fournisseur d'identité pour ton compte (un tap), garder le code e-mail pour le cabinet (domaine `@fayette-associes.fr`). Ajouter un manifeste web pour installer le site sur l'écran d'accueil du téléphone (icône, plein écran).
- **Gain estimé** : 1 à 2 connexions/jour × 45 s ≈ **5 à 9 heures par an**, et surtout la disparition d'un micro-obstacle qui décourage le « coup d'œil » du matin.

### B. Hiérarchie : accueil = vue d'ensemble, pas hub de tuiles

- **Pourquoi.** Avec dix modules, la tentation est une grille de cartes « Pilote / Fiscal / Foyer / SEO… ». Chaque carte force un clic, et l'accueil ne répond alors à aucune des trois questions du § 1.
- **Hypothèse — fausse** (ni redirection ni tuiles : vue d'ensemble avec verdict, actions et trésorerie) : l'accueil actuel est soit une redirection vers `/dashboard/pilote/`, soit un hub de liens. Dans le premier cas, l'accueil *est* la page Pilote, et les autres modules ne sont visibles que via le menu. Dans le second, les chiffres sont à un clic.
- **Reco.** Un accueil en **une colonne, cinq blocs** (§ 5) : en-tête avec fraîcheur, 3 chiffres maîtres avec delta, « ce qui a besoin de toi », échéances à 90 jours, puis les modules avec **une ligne d'état chacun** (ex. « Fiscal · IRCEC 00 000 € au 31/12 · à jour »). Le module devient une ligne de statut, pas une porte fermée.

### C. Fraîcheur des données

- **Pourquoi.** Site statique = les chiffres datent du dernier build. Si le build a trois jours, l'encours affiché est faux et rien ne te le dit. Tu recroises alors dans Pennylane, ce qui annule l'intérêt du cockpit.
- **Hypothèse — partielle** (date en tête du hub, mais c'est l'heure du build ; pas de badge d'âge sur le hub ; build déjà automatique) : date de build absente ou en pied de page.
- **Reco.** En tête d'accueil, sur chaque page : **« Données au jeu. 18 sept., 07:42 · source Pennylane »**, avec un badge orange au-delà de 48 h et rouge au-delà de 5 jours. Et la conséquence logique : rendre le build automatique (launchd sur le Mac à 7 h, ou une Routine Claude qui lance « Mise à jour des pilotis » puis déploie via `wrangler pages deploy`), pour que le badge reste vert sans intervention.

### D. Ce qui a changé depuis la dernière visite

- **Pourquoi.** Le matin, tu ne veux pas relire des stocks, tu veux les mouvements : encaissement reçu, facture émise, échéance qui s'approche.
- **Hypothèse — partielle** (delta annuel daté sur le CA ; rien depuis la dernière visite) : les KPI sont affichés en valeur absolue, sans delta ni « depuis ».
- **Reco.** Sous chaque chiffre maître, un delta **daté** (« +4 200 € depuis mar. 16 », pas « +3 % »). Un bloc « 3 mouvements depuis ta dernière visite » alimenté par le diff entre deux builds (le générateur a déjà les deux jeux de données ; il suffit de garder le précédent).

### E. Échéances et actions

- **Pourquoi.** Les deux grosses sorties de fin d'année sont connues (acompte de TVA mi-décembre, régularisation IRCEC fin décembre ; montants dans `data/provisions-snapshot.json`). S'ils ne sont que dans l'onglet Fiscal, ils ne pèsent pas sur les décisions de trésorerie du quotidien.
- **Hypothèse — à moitié vraie** (retards + prochaine échéance seulement ; TVA de décembre et IRCEC absentes de l'accueil) : échéances présentes dans Fiscal, absentes de l'accueil.
- **Reco.** Un bandeau **« Prochaines sorties, 90 jours »** sur l'accueil, trié par date, alimenté par Fiscal et par les prévisions cash. Chaque ligne : date, montant, statut (provisionné / à provisionner), et le lien vers la méthodo.

### F. Qualité des données, remontée en un badge

- **Pourquoi.** Le bloc « qualité des données » de Pilote est une très bonne idée, mais s'il vit en bas d'une page, il ne déclenche rien. Tu as écrit au cabinet vouloir « rapprocher le plus d'opérations possible dans Pennylane » : c'est un travail de fond qui n'avance que si l'outil le rappelle chaque jour.
- **Hypothèse — partielle** (compteur présent dans Pilote, rien sur l'accueil) : bloc textuel, en bas de Pilote, sans compteur.
- **Reco.** Sur l'accueil, un seul badge **vert / orange / rouge** + compteur : « 14 opérations à rapprocher · 2 factures sans échéance ». Clic → liste, chaque ligne avec le lien Pennylane. Cinq minutes par jour sur cette liste valent plus qu'une session de rattrapage par trimestre.

### G. Navigation : regrouper par question, pas par module

- **Pourquoi.** Dix entrées de menu à plat, c'est dix décisions à chaque visite. Le cabinet, lui, n'a besoin que de trois.
- **Hypothèse — fausse** (dix liens déjà regroupés en Activité / Production / Perso) : menu linéaire, dans l'ordre de création des modules.
- **Reco.** Quatre groupes : **Argent** (Pilote, Prévisions, Simulateur, Fiscal, Frais fixes), **Maison** (Foyer, Patrimoine, Retraite), **Visibilité** (SEO, Revue de presse, LinkedIn), **Méthode** (Glossaire, Qualité des données). Sur téléphone, le groupe s'ouvre en accordéon ; le groupe le plus utilisé est ouvert par défaut.

### H. Lisibilité UI des chiffres

À vérifier sur capture, desktop et téléphone :

| Point | Pourquoi | Reco |
|---|---|---|
| Chiffres alignés (tabular-nums), séparateur de milliers, unité | Comparer d'un coup d'œil | `font-variant-numeric: tabular-nums`, « 12 450 € », arrondi au k€ dans les blocs, exact dans le détail |
| Couleur = état, jamais décoration | Le rouge doit vouloir dire « à traiter » | Trois couleurs sémantiques max, le reste en gris |
| Bulles « méthodo » | Le survol n'existe pas sur téléphone | Icône ⓘ qui ouvre un panneau au tap, avec fermeture évidente |
| Les 3 chiffres maîtres sur téléphone | Trois colonnes deviennent illisibles | Empilés, le premier en grand, les deux autres en ligne |
| Contraste et taille | Lecture en marchant, en plein soleil | Corps ≥ 16 px, contraste AA, mode sombre si tu consultes le soir |
| Longueur de page | Un accueil qui défile sur trois écrans n'est plus un accueil | Tout ce qui compte au-dessus du pli téléphone |

### I. Plusieurs publics, un seul accueil

- **Pourquoi.** L'accueil idéal pour toi (actions, foyer, patrimoine) n'est pas celui du cabinet (Pilote, Fiscal, méthodo). Et Foyer / Patrimoine n'ont rien à faire sous les yeux du cabinet.
- **Hypothèse — fausse d'après le dépôt** (hub réservé à Sébastien, page Conseil distincte ; à confirmer dans Zero Trust) : même page pour tout le monde ; la séparation se fait uniquement par les règles Access, page par page, ou pas du tout.
- **Reco.** Cloudflare Access transmet l'e-mail de la personne connectée dans un en-tête (`Cf-Access-Authenticated-User-Email`). Un petit script côté page (ou une Function Pages) suffit pour afficher un **accueil « cabinet »** épuré aux domaines externes et ton accueil complet à toi. À défaut, deux entrées : `/` pour toi, `/cabinet/` pour eux, avec des règles Access distinctes.

### J. Rituels soutenus par l'accueil

- **Pourquoi.** Un cockpit sert des rituels : le lundi (cash + relances), le 1er du mois (facturation, TVA), la veille d'un appel au cabinet. S'il ne les connaît pas, c'est toi qui portes le calendrier de tête.
- **Reco.** Un bloc discret « Cette semaine » qui change de contenu selon le jour : lundi → relances à faire ; premier jour ouvré du mois → factures à émettre ; J-7 avant une échéance fiscale → rappel de provision.

---

## 3. Impact productivité : où se cache le temps

Estimations à confirmer avec tes propres relevés (§ 1). Hypothèse : tu ouvres l'outil une à deux fois par jour ouvré.

| Friction | Coût unitaire | Fréquence | Par an (env.) | Levier |
|---|---|---|---|---|
| Code Cloudflare Access | 45 s | 1–2 / jour | 5–9 h | § 2-A |
| Trouver un chiffre en naviguant (hub → module → scroll) | 20 s | 3 / jour | 4 h | § 2-B |
| Doute sur la fraîcheur → recroiser dans Pennylane | 3–5 min | 2 / semaine | 5–8 h | § 2-C |
| Deux endroits pour la même question (Brief du matin + mespilotis) | 2 min | 1 / jour | 8 h | § 4 |
| Échéance oubliée ou découverte tard | ½ journée de réorganisation | 1–2 / an | 4–8 h + stress | § 2-E |
| Rapprochement Pennylane en rattrapage trimestriel plutôt qu'en continu | 2 h × 4 vs 5 min × 220 | — | ≈ équivalent en temps, mais dette et erreurs en moins | § 2-F |

Ordre de grandeur : **25 à 40 heures par an**, soit une semaine de travail, récupérables sur des changements qui tiennent chacun en une session Claude Code.

---

## 4. Relier l'accueil à la skill « concierge »

Je n'ai pas trouvé la skill (§ 0), je ne peux donc pas auditer son contenu. Mais ton écosystème de routines est lisible dans l'historique des sessions, et deux lectures du mot « concierge » sont possibles. **Le design ci-dessous marche pour les deux.**

- **Lecture A — le concierge orchestre les routines** : briefing quotidien, mise à jour des pilotis, monitoring SEO hebdo, revue de presse, routine LinkedIn nocturne. Il prépare la journée, comme un concierge d'hôtel prépare la chambre.
- **Lecture B — le concierge répond à la demande** : « qu'est-ce que je dois relancer ? », « où en est ma tréso à 90 jours ? », « prépare le point avec le cabinet ».

### Le principe : le concierge écrit dans l'accueil, l'accueil renvoie vers le concierge

Aujourd'hui (hypothèse), le brief du matin sort en artefact et les chiffres vivent sur mespilotis : deux fenêtres, deux moments, et rien ne relie « Devis A : onze jours sans nouvelles » au montant de l'encours. Le gain vient de la **fusion sur l'écran d'accueil**.

```
   Routines Claude (Mac, 7 h)                 mespilotis (Cloudflare Pages)
   ┌───────────────────────────┐              ┌──────────────────────────┐
   │ concierge                 │  écrit       │ build_dashboard.py       │
   │  ├ briefing quotidien     │ ───────────▶ │  lit data/concierge.json │
   │  ├ mise à jour pilotis    │ concierge.json│  + données Pennylane     │
   │  ├ monitoring SEO hebdo   │              │  → index.html            │
   │  └ revue de presse        │              └──────────┬───────────────┘
   └───────────▲───────────────┘                         │ wrangler pages deploy
               │ prompt prêt à coller                     ▼
               └──────────────────────────── accueil : « Demander au concierge »
```

### Le contrat : `data/concierge.json`

Le concierge produit un fichier, le générateur le rend. Ni l'un ni l'autre ne calcule un montant : **la source de vérité des chiffres reste le build depuis Pennylane**, le concierge n'apporte que le contexte et les actions.

```json
{
  "generated_at": "2026-09-19T07:02:00+02:00",
  "day_shape": "Deux rendez-vous le matin, une heure libre après déjeuner.",
  "needs_you": [
    {
      "title": "Devis A : onze jours sans nouvelles",
      "why": "Devis envoyé il y a onze jours, fil muet depuis. Événement dans quatre semaines.",
      "source_url": "https://mail.google.com/mail/u/0/#inbox/<thread_id>",
      "due": "2026-09-21",
      "kind": "relance",
      "amount_ref": "devis_2026_08_xxx"
    }
  ],
  "done": [
    { "title": "Devis B signé", "source_url": "https://mail.google.com/…" }
  ],
  "deadlines": [
    { "label": "Acompte TVA", "date": "2026-12-15", "amount": 0, "status": "à provisionner" },
    { "label": "IRCEC rattrapage", "date": "2026-12-31", "amount": 0, "status": "à provisionner" }
  ],
  "data_quality": {
    "status": "orange",
    "items": [
      { "label": "14 opérations à rapprocher", "url": "https://app.pennylane.com/…" }
    ]
  },
  "routines": [
    { "name": "Mise à jour des pilotis", "last_run": "2026-09-18T07:40:00+02:00", "status": "ok" },
    { "name": "Monitoring SEO hebdo", "last_run": "2026-09-15T22:10:00+02:00", "status": "ok" },
    { "name": "Routine LinkedIn nocturne", "last_run": "2026-09-17T23:05:00+02:00", "status": "manquée" }
  ]
}
```

Règles à inscrire dans la skill :

1. **Cinq items maximum** dans `needs_you`, triés par urgence puis par montant en jeu. Au-delà, c'est une liste de tâches, pas un brief.
2. **Chaque item a une source** (fil Gmail, page Pennylane, événement agenda). Pas de source, pas d'item.
3. **Faits et suggestions séparés** : « le fil est muet depuis 11 jours » est un fait ; « relance aujourd'hui » est une suggestion, affichée comme telle.
4. **Aucun montant inventé** : le concierge cite une référence (`amount_ref`), le générateur va chercher la valeur.
5. **« Déjà réglé » est obligatoire** : c'est ce qui t'évite de re-vérifier ce qui est clos.
6. **Le bloc `routines` est le tableau de bord du concierge lui-même** : une routine nocturne manquée se voit le matin, pas trois semaines plus tard.

### Le sens inverse : l'accueil parle au concierge

Sur l'accueil, à côté de chaque bloc, un bouton **« Demander au concierge »** qui copie un prompt prêt à coller (ou ouvre Claude si un lien profond est disponible sur ta config) :

- Sur les chiffres maîtres : « Explique-moi le passage de l'encours de X à Y depuis mardi. »
- Sur une échéance : « Prépare le virement de provision IRCEC et vérifie que le cash à 90 jours le supporte. »
- Sur la qualité des données : « Rapproche les 14 opérations en attente dans Pennylane, et liste celles où tu as un doute. »
- En pied de page : « Prépare le point avec le cabinet » → le concierge assemble Fiscal + questions ouvertes + derniers mails du cabinet.

Cinq prompts fixes suffisent. Ce sont ceux que tu tapes déjà à la main dans les sessions « Mise à jour des pilotis » et « Briefing quotidien ».

---

## 5. L'accueil cible, en cinq blocs

Une colonne, lisible sur téléphone sans zoom, le tout au-dessus du pli pour les blocs 1 à 3.

```
┌──────────────────────────────────────────────────────────┐
│ Ven. 19 sept. · Données au 19/09 07:42 · ● à jour          │  1. En-tête + fraîcheur
├──────────────────────────────────────────────────────────┤
│  CA encaissé 2026        Encours           Cash net 90 j  │  2. Trois chiffres maîtres
│  000 k€                  00 000 €          +00 000 €      │     + delta daté
│  +0 000 € dep. mar. 16   −0 000 € dep. mar. ● stable      │
├──────────────────────────────────────────────────────────┤
│ CE QUI A BESOIN DE TOI                                     │  3. Concierge (≤ 5)
│ 01 Devis A : onze jours sans nouvelles           → mail   │
│ 02 Un prestataire attend un horaire              → mail   │
│ 03 14 opérations à rapprocher dans Pennylane     → PL     │
├──────────────────────────────────────────────────────────┤
│ PROCHAINES SORTIES · 90 J                                  │  4. Échéances
│ 15 déc.  Acompte TVA    0 000 €   à provisionner           │
│ 31 déc.  IRCEC          00 000 €  à provisionner           │
├──────────────────────────────────────────────────────────┤
│ ARGENT     Pilote · Prévisions · Simulateur · Fiscal       │  5. Modules en une ligne
│ MAISON     Foyer · Patrimoine · Retraite                   │     d'état chacun
│ VISIBILITÉ SEO (lun.) · Revue de presse · LinkedIn         │
│ MÉTHODE    Glossaire · Qualité des données ● orange        │
│ ─ Déjà réglé (3) ─ Routines : 3 ok, 1 manquée ─            │
└──────────────────────────────────────────────────────────┘
```

Pour le cabinet (§ 2-I), la même page sans les blocs 3 et « Maison », avec la méthodo en évidence.

---

## 6. Plan d'action proposé

Par ordre de rapport gain / effort. Chaque ligne tient dans une session Claude Code locale, là où vit le code.

| Priorité | Action | Effort | Gain |
|---|---|---|---|
| **P0** | Durée de session Cloudflare Access → 1 mois ; Google comme IdP pour ton compte | 15 min, aucune ligne de code | Friction quotidienne supprimée |
| **P0** | Horodatage « Données au … » + badge de fraîcheur en tête de chaque page | 30 min dans `build_dashboard.py` | Fin des doutes, fin des recroisements |
| **P0** | Bandeau « Prochaines sorties, 90 jours » sur l'accueil | 1 h | Échéances visibles chaque jour |
| **P1** | Contrat `data/concierge.json` + bloc « Ce qui a besoin de toi » sur l'accueil ; la skill écrit le fichier à la fin du briefing quotidien | 2–3 h | Un seul endroit pour la journée |
| **P1** | Build + déploiement automatiques après le briefing (launchd ou Routine) | 1 h | Le badge reste vert sans toi |
| **P1** | Menu regroupé par question (Argent / Maison / Visibilité / Méthode) | 1 h | Dix décisions → quatre |
| **P1** | Passe mobile : chiffres empilés, ⓘ au tap, tabular-nums | 2 h | Lecture en marchant |
| **P2** | Deltas datés sous les chiffres maîtres (diff entre deux builds) | 2 h | Mouvements plutôt que stocks |
| **P2** | Badge qualité des données + compteur sur l'accueil | 1 h | Rapprochement en continu |
| **P2** | Accueil « cabinet » par en-tête Access | 2 h | Foyer et Patrimoine hors de vue du cabinet |
| **P2** | Boutons « Demander au concierge » (5 prompts fixes) | 1 h | Boucle fermée accueil ↔ concierge |
| **P3** | Manifeste PWA, mode sombre, bloc « Cette semaine » par jour | 2–3 h | Confort |

---

## 7. Ce qu'il me faut pour transformer cette grille en audit réel

Une seule des options suffit ; la première prend deux minutes.

1. **Deux captures** de l'accueil (téléphone + desktop), collées dans une session, ou déposées dans `notes/` de ce dépôt.
2. **Le HTML généré** de l'accueil (le `index.html` que produit `build_dashboard.py`), même sans les données.
3. **Le dépôt mespilotis poussé sur GitHub** avec l'app Claude activée dessus : une session cloud pourra alors lire le générateur, les templates et la skill, et proposer les changements en PR.
4. **Ou lancer cet audit depuis une session locale** sur le Mac, où vivent le code et la skill : c'est là que la grille de § 2 se coche le plus vite, et que le plan de § 6 s'exécute.

Et pour le § 4 : **le fichier `SKILL.md` de la skill concierge** (ou son emplacement), pour vérifier que le contrat proposé colle à ce qu'elle fait déjà.

---

## Sources

- Mail au cabinet comptable, 24 juillet 2026 (structure de la page Pilote, accès Cloudflare Access).
- Échanges avec le cabinet, 9–11 septembre 2026 (onglet Fiscal, échéances de fin d'année, rapprochement Pennylane, prise en main du tableau de bord par la comptable).
- Mails Cloudflare, 29 mai 2026 (domaine, `mespilotis.pages.dev`, codes Access).
- Artefact « Brief du matin », 31 août 2026 (format du briefing quotidien).
- Titres des sessions Claude Code du 24 août au 19 septembre 2026 (modules, routines, cadence des mises à jour).
