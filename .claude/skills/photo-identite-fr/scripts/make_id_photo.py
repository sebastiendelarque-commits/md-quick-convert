#!/usr/bin/env python3
"""Recadre un portrait et compose la planche a imprimer, dans deux styles.

  --style identite (defaut)
      Photo d'identite aux normes francaises : cadre 35 x 45 mm, hauteur de
      visage (menton -> sommet du crane, hors chevelure) de 32 a 36 mm. Le
      script prend la plus grande hauteur tenable dans cette plage tout en
      gardant la chevelure entiere avec une marge au-dessus de la tete.

  --style portrait
      Cadrage libre, pour une planche d'ecole ou de famille : le visage est
      plus petit dans le cadre, les epaules restent visibles, la ligne des
      yeux se place aux deux cinquiemes de la hauteur. Aucun gabarit officiel
      n'est respecte : ne pas presenter ces tirages a un guichet.

Reperes attendus (en pixels de l'image source) :
  --chin      y du bas du menton                        (style identite)
  --crown     y du sommet du crane, CHEVEUX EXCLUS      (style identite,
              estimable via --hairline)
  --hair-top  y du sommet de la chevelure               (les deux styles)
  --eyes      y de la ligne des yeux                    (style portrait)
  --axis      x de l'axe vertical du visage             (les deux styles)

Dependances : Pillow (obligatoire), numpy (uniquement pour --bg).
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ID_W, ID_H = 35.0, 45.0          # format de la photo d'identite
FACE_MIN, FACE_MAX = 32.0, 36.0  # hauteur du visage autorisee (mm)
FACE_TARGET = 34.0               # cible confortable au milieu de la plage

PORTRAIT_W, PORTRAIT_H = 30.0, 45.0   # petit format scolaire par defaut
EYE_PCT = 0.50                   # hauteur de la ligne des yeux dans le cadre
HEADROOM_PCT = 0.05              # air minimum au-dessus de la chevelure

SHEETS = {                       # format planche : (largeur mm, hauteur mm)
    "10x15": (100.0, 150.0),
    "13x18": (130.0, 180.0),
    "a4": (210.0, 297.0),
    "a5": (148.0, 210.0),
}

BG_TARGETS = {                   # fonds conformes (uni et clair, jamais blanc)
    "gris": (222, 222, 222),
    "gris-clair": (232, 232, 232),
    "bleu": (214, 224, 235),
}


# --------------------------------------------------------------------------
# geometrie
# --------------------------------------------------------------------------
def solve_identite(chin, crown, hair_top, face_mm=None,
                   top_gap_mm=2.5, below_chin_min_mm=3.0):
    """Retourne (mm_par_px, face_mm, top_gap_mm, below_chin_mm).

    Le cadre fait toujours 35 x 45 mm. On cherche l'echelle telle que :
      - hauteur du visage dans [32, 36] mm, au plus pres de 34 mm ;
      - chevelure entiere avec >= top_gap_mm au-dessus ;
      - >= below_chin_min_mm sous le menton.
    """
    face_px = chin - crown
    head_px = chin - hair_top          # menton -> sommet des cheveux
    if face_px <= 0 or head_px <= 0:
        raise SystemExit("Reperes incoherents : --crown et --hair-top doivent "
                         "etre au-dessus de --chin (y plus petit).")

    if face_mm is None:
        # hauteur de visage maximale qui laisse rentrer cheveux + marges
        budget = ID_H - top_gap_mm - below_chin_min_mm
        face_max_fit = budget * face_px / head_px
        face_mm = min(FACE_TARGET, face_max_fit)
        face_mm = max(FACE_MIN, min(FACE_MAX, face_mm))

    mm_per_px = face_mm / face_px
    head_mm = head_px * mm_per_px
    slack = ID_H - head_mm - top_gap_mm - below_chin_min_mm
    if slack < -0.05:
        raise SystemExit(
            f"Impossible de tenir dans 45 mm : visage {face_mm:.1f} mm + "
            f"chevelure {head_mm - face_mm:.1f} mm + marges. "
            f"Baissez --face-mm (min {FACE_MIN}) ou recadrez la source.")
    below_chin_mm = below_chin_min_mm + max(0.0, slack)  # le jeu va sous le menton
    return mm_per_px, face_mm, top_gap_mm, below_chin_mm


def box_identite(chin, axis, mm_per_px, below_chin_mm):
    """Cadre de decoupe (x0, y0, x1, y1) en pixels source."""
    w_px = ID_W / mm_per_px
    h_px = ID_H / mm_per_px
    y1 = chin + below_chin_mm / mm_per_px
    y0 = y1 - h_px
    x0 = axis - w_px / 2.0
    return [x0, y0, x0 + w_px, y1]


def box_portrait(eyes, hair_top, axis, src_size, w_mm, h_mm,
                 eye_pct=EYE_PCT, headroom_pct=HEADROOM_PCT):
    """Cadre de decoupe d'un portrait libre.

    On vise la ligne des yeux a eye_pct de la hauteur et headroom_pct d'air
    au-dessus de la chevelure : ces deux contraintes fixent entierement le
    cadre, donc monter eye_pct resserre le cadrage (le visage grandit, les
    epaules se rapprochent du bord bas). Si la source ne donne pas assez de
    matiere, on prend le plus grand cadre du bon rapport qu'elle contient.
    """
    src_w, src_h = src_size
    aspect = w_mm / h_mm

    denom = eye_pct - headroom_pct
    if denom <= 0:
        raise SystemExit("--eye-pct doit etre superieur a --headroom-pct.")
    h_px = (eyes - hair_top) / denom          # cadrage ideal
    h_px = min(h_px, src_h, src_w / aspect)   # borne par la source
    w_px = h_px * aspect

    y0 = eyes - eye_pct * h_px
    y0 = min(y0, hair_top - headroom_pct * h_px)   # ne jamais raser les cheveux
    y0 = max(0.0, min(y0, src_h - h_px))
    x0 = max(0.0, min(axis - w_px / 2.0, src_w - w_px))
    return [x0, y0, x0 + w_px, y0 + h_px]


# --------------------------------------------------------------------------
# fond
# --------------------------------------------------------------------------
def neutralize_background(img, target_rgb, tol=46.0, feather_mm=0.15, dpi=300):
    """Deplace la teinte du fond vers target_rgb sans detourer le sujet.

    On ne remplace pas les pixels : on leur applique un decalage colorimetrique
    pondere par une alpha douce (distance a la couleur du fond, propagee depuis
    les bords). La texture du mur et les meches de cheveux sont preservees, sans
    halo de detourage. A appliquer AVANT la reduction, pour que les cheveux fins
    soient encore resolus et ne soient pas pris pour du fond.
    """
    import numpy as np

    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    h, w, _ = a.shape

    # couleur de fond estimee sur les bandes laterales du haut de l'image
    band = max(4, w // 12)
    edges = np.concatenate([a[:h // 3, :band].reshape(-1, 3),
                            a[:h // 3, -band:].reshape(-1, 3)], axis=0)
    bg = np.median(edges, axis=0)

    dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
    alpha = np.clip(1.0 - (dist - tol) / tol, 0.0, 1.0)   # 1 = fond, 0 = sujet
    alpha = alpha ** 1.5                                   # attenue les zones douteuses

    # ne garder que le fond relie aux bords : la propagation se fait sur une
    # version reduite (rapide) puis est reprojetee en pleine resolution
    sw = 400
    sh = max(1, int(round(h * sw / w)))
    solid_small = np.asarray(
        Image.fromarray(((alpha > 0.5) * 255).astype("uint8")).resize((sw, sh), Image.BILINEAR),
        dtype=np.uint8) > 127
    reach = np.zeros_like(solid_small)
    reach[0, :] = solid_small[0, :]
    reach[-1, :] = solid_small[-1, :]
    reach[:, 0] = solid_small[:, 0]
    reach[:, -1] = solid_small[:, -1]
    for _ in range(sw + sh):
        prev = int(reach.sum())
        grown = reach.copy()
        grown[1:, :] |= reach[:-1, :]
        grown[:-1, :] |= reach[1:, :]
        grown[:, 1:] |= reach[:, :-1]
        grown[:, :-1] |= reach[:, 1:]
        reach = grown & solid_small
        if int(reach.sum()) == prev:
            break

    mask = Image.fromarray((reach * 255).astype("uint8")).resize((w, h), Image.BILINEAR)
    mask = mask.filter(ImageFilter.GaussianBlur(max(1.0, feather_mm / 25.4 * dpi)))
    alpha = alpha * (np.asarray(mask, dtype=np.float32) / 255.0)

    shift = (np.asarray(target_rgb, dtype=np.float32) - bg)
    out = a + shift * alpha[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype("uint8"))


# --------------------------------------------------------------------------
# rendu
# --------------------------------------------------------------------------
def px(mm, dpi):
    return int(round(mm / 25.4 * dpi))


def render_photo(src, box, w_mm, h_mm, dpi, sharpen=True, bg=None, roll=0.0):
    img = src
    if roll:
        img = img.rotate(roll, resample=Image.BICUBIC,
                         center=((box[0] + box[2]) / 2, (box[1] + box[3]) / 2))
    crop = img.crop((int(round(box[0])), int(round(box[1])),
                     int(round(box[2])), int(round(box[3]))))
    if bg:
        crop = neutralize_background(crop, BG_TARGETS[bg], dpi=dpi)
    out = crop.resize((px(w_mm, dpi), px(h_mm, dpi)), Image.LANCZOS)
    if sharpen:
        out = out.filter(ImageFilter.UnsharpMask(radius=1.0, percent=60, threshold=3))
    return out


def render_sheet(photo, sheet, dpi, gutter_mm=2.0, marks=True):
    sw_mm, sh_mm = SHEETS[sheet]
    W, H = px(sw_mm, dpi), px(sh_mm, dpi)
    pw, ph = photo.size
    g = px(gutter_mm, dpi)

    cols = max(1, int((W + g) // (pw + g)))
    rows = max(1, int((H + g) // (ph + g)))
    grid_w = cols * pw + (cols - 1) * g
    grid_h = rows * ph + (rows - 1) * g
    ox, oy = (W - grid_w) // 2, (H - grid_h) // 2

    sheet_img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(sheet_img)
    tick = px(3.0, dpi)
    for r in range(rows):
        for c in range(cols):
            x = ox + c * (pw + g)
            y = oy + r * (ph + g)
            sheet_img.paste(photo, (x, y))
            if marks:  # traits de coupe hors image
                for (cx, cy) in ((x, y), (x + pw, y), (x, y + ph), (x + pw, y + ph)):
                    sx = -1 if cx == x else 1
                    sy = -1 if cy == y else 1
                    d.line([(cx + sx * 2, cy), (cx + sx * tick, cy)], fill=(160, 160, 160), width=1)
                    d.line([(cx, cy + sy * 2), (cx, cy + sy * tick)], fill=(160, 160, 160), width=1)
    return sheet_img, cols * rows


def render_control_identite(photo, face_mm, top_gap_mm, below_chin_mm, dpi):
    """Photo + gabarit de controle (bande 32-36 mm, menton, sommet du crane)."""
    ctl = photo.convert("RGB").resize((px(ID_W, dpi) * 2, px(ID_H, dpi) * 2), Image.LANCZOS)
    W, H = ctl.size
    d = ImageDraw.Draw(ctl)
    ppm = H / ID_H  # pixels par mm dans l'apercu

    def hline(mm_from_top, color, label, width=2):
        y = mm_from_top * ppm
        d.line([(0, y), (W, y)], fill=color, width=width)
        d.text((6, y + 4), label, fill=color)

    chin_mm = ID_H - below_chin_mm
    hline(chin_mm, (0, 190, 90), f"menton  ({below_chin_mm:.1f} mm sous le menton)")
    hline(chin_mm - face_mm, (0, 190, 90), f"sommet du crane  visage = {face_mm:.1f} mm")
    for lo in (FACE_MIN, FACE_MAX):    # bande de tolerance rapportee au menton
        hline(chin_mm - lo, (255, 140, 0), f"tolerance {lo:.0f} mm", width=1)
    hline(top_gap_mm, (0, 140, 255), f"marge haute {top_gap_mm:.1f} mm", width=1)
    d.line([(W / 2, 0), (W / 2, H)], fill=(0, 140, 255), width=1)
    d.rectangle([0, 0, W - 1, H - 1], outline=(200, 0, 0), width=3)
    return ctl


def render_control_portrait(photo, eye_pct, headroom, dpi):
    """Photo + reperes de composition (ligne des yeux, tiers, air au-dessus)."""
    ctl = photo.convert("RGB")
    ctl = ctl.resize((ctl.width * 2, ctl.height * 2), Image.LANCZOS)
    W, H = ctl.size
    d = ImageDraw.Draw(ctl)
    for t in (1 / 3, 2 / 3):           # regle des tiers
        d.line([(0, H * t), (W, H * t)], fill=(255, 255, 255), width=1)
        d.line([(W * t, 0), (W * t, H)], fill=(255, 255, 255), width=1)
    y = H * eye_pct
    d.line([(0, y), (W, y)], fill=(0, 190, 90), width=2)
    d.text((6, y + 4), f"ligne des yeux  {eye_pct * 100:.0f} % de la hauteur", fill=(0, 190, 90))
    y = H * headroom
    d.line([(0, y), (W, y)], fill=(0, 140, 255), width=1)
    d.text((6, y + 4), f"air au-dessus des cheveux  {headroom * 100:.1f} %", fill=(0, 140, 255))
    d.line([(W / 2, 0), (W / 2, H)], fill=(0, 140, 255), width=1)
    d.rectangle([0, 0, W - 1, H - 1], outline=(200, 0, 0), width=3)
    return ctl


# --------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--outdir", type=Path, default=Path("planche"))
    p.add_argument("--style", default="identite", choices=("identite", "portrait"))
    p.add_argument("--chin", type=float, help="y du bas du menton (px)")
    p.add_argument("--crown", type=float, help="y du sommet du crane hors cheveux (px)")
    p.add_argument("--hairline", type=float,
                   help="y de la naissance des cheveux ; estime --crown si absent")
    p.add_argument("--hair-top", type=float, required=True, help="y du sommet de la chevelure (px)")
    p.add_argument("--eyes", type=float, help="y de la ligne des yeux (px, style portrait)")
    p.add_argument("--axis", type=float, required=True, help="x de l'axe du visage (px)")
    p.add_argument("--photo-mm", type=float, nargs=2, metavar=("L", "H"),
                   help="format de la photo ; defaut 35x45 (identite) ou 30x40 (portrait)")
    p.add_argument("--face-mm", type=float, default=None,
                   help="hauteur du visage imposee (32-36) ; auto par defaut")
    p.add_argument("--top-gap-mm", type=float, default=2.5)
    p.add_argument("--below-chin-mm", type=float, default=3.0, help="minimum sous le menton")
    p.add_argument("--eye-pct", type=float, default=EYE_PCT * 100,
                   help="hauteur de la ligne des yeux en %% du cadre (style portrait). "
                        "Regle aussi le serrage : 44 = le plus aere que la source "
                        "permette, 50 equilibre, 54 = visage bien lisible en petit "
                        "format")
    p.add_argument("--headroom-pct", type=float, default=HEADROOM_PCT * 100,
                   help="air au-dessus des cheveux en %% du cadre (style portrait)")
    p.add_argument("--roll", type=float, default=0.0, help="rotation de redressement (degres)")
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--sheet", default="10x15", choices=list(SHEETS) + ["aucune"])
    p.add_argument("--gutter-mm", type=float, default=2.0)
    p.add_argument("--bg", choices=list(BG_TARGETS), default=None,
                   help="neutralise le fond vers un gris/bleu clair conforme")
    p.add_argument("--no-sharpen", action="store_true")
    p.add_argument("--prefix", default=None)
    args = p.parse_args()

    src = Image.open(args.input).convert("RGB")
    W, H = src.size
    prefix = args.prefix or ("photo_identite" if args.style == "identite" else "portrait")

    if args.style == "identite":
        if args.chin is None:
            raise SystemExit("--chin est requis en style identite.")
        crown = args.crown
        if crown is None:
            if args.hairline is None:
                raise SystemExit("Fournir --crown ou --hairline.")
            # le sommet du crane est ~20 % de la hauteur de tete au-dessus de la
            # naissance des cheveux (menton->naissance = 80 % du visage)
            crown = args.chin - (args.chin - args.hairline) / 0.80
        w_mm, h_mm = args.photo_mm or (ID_W, ID_H)
        if (w_mm, h_mm) != (ID_W, ID_H):
            raise SystemExit("Le style identite impose 35 x 45 mm ; utilisez "
                             "--style portrait pour un autre format.")
        mm_per_px, face_mm, top_gap, below_chin = solve_identite(
            args.chin, crown, args.hair_top, args.face_mm,
            args.top_gap_mm, args.below_chin_mm)
        box = box_identite(args.chin, args.axis, mm_per_px, below_chin)
    else:
        if args.eyes is None:
            raise SystemExit("--eyes est requis en style portrait.")
        w_mm, h_mm = args.photo_mm or (PORTRAIT_W, PORTRAIT_H)
        eye_pct, headroom_pct = args.eye_pct / 100.0, args.headroom_pct / 100.0
        box = box_portrait(args.eyes, args.hair_top, args.axis, (W, H),
                           w_mm, h_mm, eye_pct, headroom_pct)

    out_of_frame = [n for n, v in (("gauche", box[0]), ("haut", box[1]),
                                   ("droite", W - box[2]), ("bas", H - box[3])) if v < -0.5]
    if out_of_frame:
        raise SystemExit(f"Le cadre {w_mm:g}x{h_mm:g} sort de l'image (" +
                         ", ".join(out_of_frame) + "). Photo source trop serree.")

    args.outdir.mkdir(parents=True, exist_ok=True)
    photo = render_photo(src, box, w_mm, h_mm, args.dpi,
                         not args.no_sharpen, args.bg, args.roll)

    single = args.outdir / f"{prefix}_{w_mm:g}x{h_mm:g}.png"
    photo.save(single, dpi=(args.dpi, args.dpi))
    photo.save(single.with_suffix(".jpg"), quality=95, subsampling=0, dpi=(args.dpi, args.dpi))
    made = [single, single.with_suffix(".jpg")]

    if args.style == "identite":
        ctl = render_control_identite(photo, face_mm, top_gap, below_chin, args.dpi)
    else:
        ctl = render_control_portrait(
            photo, (args.eyes - box[1]) / (box[3] - box[1]),
            (args.hair_top - box[1]) / (box[3] - box[1]), args.dpi)
    ctl.save(args.outdir / f"{prefix}_controle.png")

    n = 0
    if args.sheet != "aucune":
        sheet_img, n = render_sheet(photo, args.sheet, args.dpi, args.gutter_mm)
        sp = args.outdir / f"{prefix}_planche_{args.sheet}.png"
        sheet_img.save(sp, dpi=(args.dpi, args.dpi))
        sheet_img.save(sp.with_suffix(".jpg"), quality=95, subsampling=0, dpi=(args.dpi, args.dpi))
        sheet_img.save(sp.with_suffix(".pdf"), resolution=args.dpi)
        made += [sp, sp.with_suffix(".jpg"), sp.with_suffix(".pdf")]

    print("Cadrage calcule")
    print(f"  style            : {args.style}  ({w_mm:g} x {h_mm:g} mm)")
    print(f"  cadre source     : x {box[0]:.0f} -> {box[2]:.0f}, y {box[1]:.0f} -> {box[3]:.0f}")
    print(f"                     ({box[2]-box[0]:.0f} x {box[3]-box[1]:.0f} px, "
          f"reduction x{(box[3]-box[1])/px(h_mm, args.dpi):.1f})")
    if args.style == "identite":
        print(f"  hauteur visage   : {face_mm:.1f} mm      (norme 32-36)")
        print(f"  marge au-dessus  : {top_gap:.1f} mm      (cheveux compris)")
        print(f"  sous le menton   : {below_chin:.1f} mm")
    else:
        h_box = box[3] - box[1]
        print(f"  ligne des yeux   : {(args.eyes - box[1]) / h_box * 100:.0f} % de la hauteur")
        print(f"  air au-dessus    : {(args.hair_top - box[1]) / h_box * 100:.1f} %")
    print(f"  sortie           : {px(w_mm, args.dpi)} x {px(h_mm, args.dpi)} px a {args.dpi} dpi")
    if n:
        print(f"  planche          : {args.sheet} -> {n} photos")
    print("Fichiers :")
    for f in made:
        print(f"  {f}")


if __name__ == "__main__":
    sys.exit(main())
