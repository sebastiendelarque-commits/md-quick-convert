---
name: photo-identite-fr
description: Fabrique une photo d'identité 35×45 mm aux normes françaises (ANTS/ICAO) et la planche à imprimer, à partir d'une photo ordinaire, et vérifie la conformité du portrait. À utiliser dès qu'on demande une photo d'identité, une planche de photos, un cadrage passeport / CNI / permis / titre de séjour, ou un contrôle de conformité ANTS d'un portrait.
---

# Photo d'identité française

Recadre un portrait au format officiel 35 × 45 mm, hauteur de visage 32–36 mm,
et compose la planche prête à imprimer. Le cadrage est calculé à partir de
quatre repères relevés à la main sur la photo source : c'est plus fiable qu'une
détection automatique, et cela rend chaque décision de cadrage vérifiable.

Le même outil produit aussi, en `--style portrait`, une planche **non
officielle** au cadrage soigné — celle que demandent l'école, la cantine ou la
famille. Toujours demander à quoi sert la planche : le cadrage réglementaire est
sévère (visage sur les trois quarts de la hauteur, épaules coupées) et fait
« photo anthropométrique » sur un enfant.

Deux chemins mènent au même résultat : les scripts, qui calculent le cadrage à
partir de repères et gardent la trace de chaque décision, et `outils/cadreur.html`,
qui laisse cadrer à la souris. Proposer l'outil dès que l'utilisateur veut
arbitrer lui-même le cadrage ou en essayer plusieurs — c'est plus rapide que de
lui envoyer des variantes une par une.

## L'outil interactif

`outils/cadreur.html` — une page autonome, à ouvrir directement dans un
navigateur (double-clic, aucune installation, aucun serveur). La photo est lue
localement : **rien n'est envoyé nulle part**, ce qui compte quand il s'agit de
la photo d'un enfant.

- rapport largeur/hauteur verrouillé sur le format choisi (35 × 45 et autres
  formats courants, ou dimensions libres) — on ne peut pas sortir des
  proportions réglementaires en cadrant ;
- glisser pour déplacer, molette ou curseur pour serrer/desserrer ;
- deux clics (menton, sommet du crâne) affichent la **hauteur de visage en mm**
  en direct, avec le verdict 32–36 mm et la bande de tolérance sur l'image ;
- export de la photo, de la planche (JPEG) et de la planche en **PDF à la taille
  physique exacte**, à 300 ou 600 dpi ;
- « Copier la commande équivalente » rend le cadrage reproductible en ligne de
  commande :

```bash
python3 scripts/make_id_photo.py photo.jpg -o sortie \
  --box 397 59 2373 2599 --photo-mm 35 45 --sheet 10x15
```

`--box` prend le cadre en pixels source et court-circuite le calcul : le script
vérifie seulement que le rapport correspond à `--photo-mm`, puis produit les
fichiers avec le même rendu (accentuation, planche, PDF) que les autres modes.
Utile pour rejouer un cadrage validé à l'œil, ou le décliner en plusieurs
formats de planche.

## Étape 0 — contrôle de recevabilité (avant tout traitement)

Regarder la photo et annoncer le verdict **avant** de produire quoi que ce soit.
Les critères et les tolérances sont dans `references/normes.md`.

Rédhibitoire (le dire et ne pas produire de planche sans accord explicite) :

- visage de trois quarts, tête penchée, yeux fermés ou regard hors objectif ;
- tête coupée par le cadre, ou trop peu de marge au-dessus des cheveux pour
  tenir 32 mm de visage dans 45 mm (le script le détecte et s'arrête) ;
- flou, sous-exposition, ombre portée sur le visage ou le fond, reflets ;
- fond non uni, sombre, ou blanc pur ; visage moins de ~900 px de haut ;
- couvre-chef, lunettes à verres teintés, mains ou objets dans le champ.

À signaler comme **risque** sans bloquer (l'agent qui instruit le dossier
tranche) : sourire dents apparentes, bouche ouverte, fond de couleur autre que
gris/bleu clair, mèches rebelles qui touchent le bord, photo de plus de 6 mois.

Pour un enfant de moins de 6 ans, l'expression neutre et le regard vers
l'objectif sont tolérés de façon souple, mais un sourire franc dents découvertes
reste un motif de refus fréquent : le dire.

## Étape 1 — relever les repères

```bash
python3 scripts/grille.py photo.jpg -o grille.png                     # vue d'ensemble
python3 scripts/grille.py photo.jpg --box 700 1900 1700 2500 -o z.png # zoom menton
python3 scripts/grille.py photo.jpg --box 500 100 2100 1100 -o t.png  # zoom cheveux
```

Lire les images produites et relever, en pixels source :

| repère | ce qu'on vise |
|---|---|
| `--chin` | bas du menton (la limite menton/cou, pas le pli sous la lèvre) |
| `--crown` | sommet du **crâne, cheveux exclus** — invisible sous les cheveux, donc estimé |
| `--hair-top` | sommet de la **chevelure**, mèches isolées comprises |
| `--eyes` | ligne des yeux (milieu des pupilles) — style portrait uniquement |
| `--axis` | axe vertical du visage : milieu des pupilles, confirmé par le milieu de la bouche |

`--crown` est le repère délicat. Deux estimations à croiser :

- naissance des cheveux : `crown = chin - (chin - hairline) / 0.80` — c'est ce
  que fait `--hairline` si `--crown` est omis ;
- ligne des yeux : elle tombe vers 45–48 % de la hauteur de tête chez le jeune
  enfant, 50 % chez l'adulte, donc `crown ≈ chin - (chin - yeux) / 0.47`.

Si les deux divergent, prendre le milieu ; l'écart se traduit en ~1 mm de
hauteur de visage, absorbé par la tolérance 32–36 mm.

## Étape 2 — produire

```bash
python3 scripts/make_id_photo.py photo.jpg -o sortie \
  --chin 2430 --crown 540 --hair-top 200 --axis 1385 --sheet 10x15
```

Le script choisit la plus grande hauteur de visage possible dans 32–36 mm
(cible 34) qui laisse encore la chevelure entière avec 2,5 mm de marge au-dessus
et 3 mm sous le menton, puis sort la photo seule (PNG + JPEG, 300 dpi), la
planche (PNG + JPEG + **PDF** à la taille physique exacte) et une image de
contrôle. Options utiles : `--sheet 10x15|13x18|a4|a5|aucune`, `--face-mm` pour
forcer une hauteur, `--dpi 600`, `--roll` pour redresser une tête penchée.

## Étape 3 — vérifier avant de livrer

Toujours ouvrir `*_controle.png` et contrôler que la ligne verte basse est bien
au menton, la ligne verte haute au sommet du crâne, la chevelure entière sous la
ligne bleue, et l'axe bleu au milieu du visage. Si un repère est faux, le
corriger et relancer : ne jamais livrer une planche non relue.

Annoncer les mesures obtenues (hauteur de visage, marges) et rappeler les
risques de l'étape 0.

## Style portrait (école, cantine, famille)

```bash
python3 scripts/make_id_photo.py photo.jpg -o ecole --style portrait \
  --eyes 1559 --hair-top 200 --axis 1385 --photo-mm 30 45 --eye-pct 54 --sheet 10x15
```

Ce style ignore le gabarit officiel : il place la ligne des yeux et laisse de
l'air au-dessus des cheveux, garde les épaules, et accepte n'importe quel format
via `--photo-mm`. Il ne demande que trois repères — `--eyes`, `--hair-top`,
`--axis`.

`--eye-pct` règle à la fois la position des yeux et le serrage, puisque les deux
contraintes déterminent le cadre :

| valeur | effet |
|---|---|
| 44 | le plus aéré que la source permette — pour un tirage 10 × 15 ou 13 × 18 |
| 50 | équilibré (défaut) |
| 54 | visage bien lisible en petit format, buste juste sous les épaules |

En petit format (30 × 45 mm), viser 52–54 : en dessous, le visage devient trop
petit sur le tirage et le vêtement occupe la moitié de la vignette. Regarder
`*_controle.png` (règle des tiers + ligne des yeux) et trancher à l'œil, pas au
chiffre.

Le dire clairement en livrant : **ces tirages ne sont pas valables à un
guichet**.

## Fond

`--bg gris-clair|gris|bleu` décale la teinte du fond vers un fond conforme sans
détourage. Cela marche sur un fond uni et un sujet aux contours nets ; sur une
chevelure volumineuse ou frisée, le mur vu à travers les cheveux les éclaircit
et **modifie l'apparence du sujet**, ce que la norme interdit. Vérifier à l'œil,
et livrer par défaut la version fidèle : un fond uni et clair, même beige, passe
mieux qu'une retouche visible.

## Limites

- Ne produit pas de **code e-photo ANTS** (photo numérique transmise
  directement à l'administration) : réservé aux photographes et cabines agréés.
  La planche imprimée est acceptée par tous les guichets.
- Aucune retouche du visage, de la peau ou des cheveux — c'est interdit.
- Ne jamais versionner la photo source ni les planches dans un dépôt : ce sont
  des données personnelles, souvent celles d'un mineur. Les livrer en fichiers.

## Dépendances

`pip install pillow` (`numpy` en plus pour `--bg`). L'outil `outils/cadreur.html`
ne dépend de rien : un navigateur suffit.
