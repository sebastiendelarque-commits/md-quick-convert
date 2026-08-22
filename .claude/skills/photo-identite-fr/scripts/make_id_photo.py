#!/usr/bin/env python3
"""Fabrique une photo d'identite 35x45 mm aux normes francaises (ANTS/ICAO)
et la planche a imprimer, a partir d'une photo source et de 4 reperes.

Reperes attendus (en pixels de l'image source) :
  --chin      y du bas du menton
  --crown     y du sommet du crane, CHEVEUX EXCLUS (estimable via --hairline)
  --hair-top  y du sommet de la chevelure
  --axis      x de l'axe vertical du visage (milieu des yeux / du nez)

La norme impose une hauteur de visage (menton -> sommet du crane, hors
chevelure) de 32 a 36 mm dans un cadre de 35 x 45 mm. Le script choisit
automatiquement la plus grande hauteur possible dans cette plage tout en
gardant la chevelure entiere avec une marge au-dessus de la tete.

Dependances : Pillow (obligatoire), numpy (uniquement pour --bg).
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

MM_W, MM_H = 35.0, 45.0          # format de la photo
FACE_MIN, FACE_MAX = 32.0, 36.0  # hauteur du visage autorisee (mm)
FACE_TARGET = 34.0               # cible confortable au milieu de la plage

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
def solve_layout(chin, crown, hair_top, face_mm=None,
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
        budget = MM_H - top_gap_mm - below_chin_min_mm
        face_max_fit = budget * face_px / head_px
        face_mm = min(FACE_TARGET, face_max_fit)
        face_mm = max(FACE_MIN, min(FACE_MAX, face_mm))

    mm_per_px = face_mm / face_px
    head_mm = head_px * mm_per_px
    slack = MM_H - head_mm - top_gap_mm - below_chin_min_mm
    if slack < -0.05:
        raise SystemExit(
            f"Impossible de tenir dans 45 mm : visage {face_mm:.1f} mm + "
            f"chevelure {head_mm - face_mm:.1f} mm + marges. "
            f"Baissez --face-mm (min {FACE_MIN}) ou recadrez la source.")
    below_chin_mm = below_chin_min_mm + max(0.0, slack)  # le jeu va sous le menton
    return mm_per_px, face_mm, top_gap_mm, below_chin_mm


def crop_box(chin, axis, mm_per_px, below_chin_mm):
    """Cadre de decoupe (x0, y0, x1, y1) en pixels source."""
    w_px = MM_W / mm_per_px
    h_px = MM_H / mm_per_px
    y1 = chin + below_chin_mm / mm_per_px
    y0 = y1 - h_px
    x0 = axis - w_px / 2.0
    return [x0, y0, x0 + w_px, y1]


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


def render_photo(src, box, dpi, sharpen=True, bg=None, roll=0.0):
    img = src
    if roll:
        img = img.rotate(roll, resample=Image.BICUBIC, center=(box[0] + (box[2] - box[0]) / 2,
                                                               box[1] + (box[3] - box[1]) / 2))
    crop = img.crop((int(round(box[0])), int(round(box[1])),
                     int(round(box[2])), int(round(box[3]))))
    if bg:
        crop = neutralize_background(crop, BG_TARGETS[bg], dpi=dpi)
    out = crop.resize((px(MM_W, dpi), px(MM_H, dpi)), Image.LANCZOS)
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


def render_control(photo, mm_per_px, face_mm, top_gap_mm, below_chin_mm, dpi):
    """Photo + gabarit de controle (bande 32-36 mm, menton, sommet du crane)."""
    ctl = photo.convert("RGB").resize((px(MM_W, dpi) * 2, px(MM_H, dpi) * 2), Image.LANCZOS)
    W, H = ctl.size
    d = ImageDraw.Draw(ctl)
    ppm = H / MM_H  # pixels par mm dans l'apercu

    def hline(mm_from_top, color, label, width=2):
        y = mm_from_top * ppm
        d.line([(0, y), (W, y)], fill=color, width=width)
        d.text((6, y + 4), label, fill=color)

    chin_mm = MM_H - below_chin_mm
    crown_mm = chin_mm - face_mm
    hline(chin_mm, (0, 190, 90), f"menton  ({below_chin_mm:.1f} mm sous le menton)")
    hline(crown_mm, (0, 190, 90), f"sommet du crane  visage = {face_mm:.1f} mm")
    # bande de tolerance 32-36 mm rapportee au menton
    for lo in (FACE_MIN, FACE_MAX):
        hline(chin_mm - lo, (255, 140, 0), f"tolerance {lo:.0f} mm", width=1)
    hline(top_gap_mm, (0, 140, 255), f"marge haute {top_gap_mm:.1f} mm", width=1)
    d.line([(W / 2, 0), (W / 2, H)], fill=(0, 140, 255), width=1)
    d.rectangle([0, 0, W - 1, H - 1], outline=(200, 0, 0), width=3)
    return ctl


# --------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--outdir", type=Path, default=Path("planche"))
    p.add_argument("--chin", type=float, required=True, help="y du bas du menton (px)")
    p.add_argument("--crown", type=float, help="y du sommet du crane hors cheveux (px)")
    p.add_argument("--hairline", type=float,
                   help="y de la naissance des cheveux ; estime --crown si absent")
    p.add_argument("--hair-top", type=float, required=True, help="y du sommet de la chevelure (px)")
    p.add_argument("--axis", type=float, required=True, help="x de l'axe du visage (px)")
    p.add_argument("--face-mm", type=float, default=None,
                   help="hauteur du visage imposee (32-36) ; auto par defaut")
    p.add_argument("--top-gap-mm", type=float, default=2.5)
    p.add_argument("--below-chin-mm", type=float, default=3.0, help="minimum sous le menton")
    p.add_argument("--roll", type=float, default=0.0, help="rotation de redressement (degres)")
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--sheet", default="10x15", choices=list(SHEETS) + ["aucune"])
    p.add_argument("--gutter-mm", type=float, default=2.0)
    p.add_argument("--bg", choices=list(BG_TARGETS), default=None,
                   help="neutralise le fond vers un gris/bleu clair conforme")
    p.add_argument("--no-sharpen", action="store_true")
    p.add_argument("--prefix", default="photo_identite")
    args = p.parse_args()

    crown = args.crown
    if crown is None:
        if args.hairline is None:
            raise SystemExit("Fournir --crown ou --hairline.")
        # le sommet du crane est ~20 % de la hauteur de tete au-dessus de la
        # naissance des cheveux (menton->naissance = 80 % du visage)
        crown = args.chin - (args.chin - args.hairline) / 0.80

    src = Image.open(args.input)
    src = src.convert("RGB")

    mm_per_px, face_mm, top_gap, below_chin = solve_layout(
        args.chin, crown, args.hair_top, args.face_mm, args.top_gap_mm, args.below_chin_mm)
    box = crop_box(args.chin, args.axis, mm_per_px, below_chin)

    W, H = src.size
    out_of_frame = [n for n, v, lim in
                    (("gauche", box[0], 0), ("haut", box[1], 0),
                     ("droite", W - box[2], 0), ("bas", H - box[3], 0)) if v < lim]
    if out_of_frame:
        raise SystemExit("Le cadre 35x45 sort de l'image (" + ", ".join(out_of_frame) +
                         "). Photo source trop serree : reculez ou baissez --face-mm.")

    args.outdir.mkdir(parents=True, exist_ok=True)
    photo = render_photo(src, box, args.dpi, not args.no_sharpen, args.bg, args.roll)

    single_png = args.outdir / f"{args.prefix}_35x45.png"
    single_jpg = args.outdir / f"{args.prefix}_35x45.jpg"
    photo.save(single_png, dpi=(args.dpi, args.dpi))
    photo.save(single_jpg, quality=95, subsampling=0, dpi=(args.dpi, args.dpi))

    ctl = render_control(photo, mm_per_px, face_mm, top_gap, below_chin, args.dpi)
    ctl.save(args.outdir / f"{args.prefix}_controle.png")

    made = [single_png, single_jpg]
    n = 0
    if args.sheet != "aucune":
        sheet_img, n = render_sheet(photo, args.sheet, args.dpi, args.gutter_mm)
        sp = args.outdir / f"{args.prefix}_planche_{args.sheet}.png"
        sheet_img.save(sp, dpi=(args.dpi, args.dpi))
        sheet_img.save(sp.with_suffix(".jpg"), quality=95, subsampling=0, dpi=(args.dpi, args.dpi))
        sheet_img.save(sp.with_suffix(".pdf"), resolution=args.dpi)
        made += [sp, sp.with_suffix(".jpg"), sp.with_suffix(".pdf")]

    scale = 1.0 / mm_per_px  # px source par mm
    print(f"""Cadrage calcule
  echelle          : {scale:.1f} px source / mm
  cadre source     : x {box[0]:.0f} -> {box[2]:.0f}, y {box[1]:.0f} -> {box[3]:.0f}
                     ({box[2]-box[0]:.0f} x {box[3]-box[1]:.0f} px, reduction x{(box[3]-box[1])/px(MM_H, args.dpi):.1f})
  hauteur visage   : {face_mm:.1f} mm      (norme 32-36)
  marge au-dessus  : {top_gap:.1f} mm      (cheveux compris)
  sous le menton   : {below_chin:.1f} mm
  sortie           : {px(MM_W, args.dpi)} x {px(MM_H, args.dpi)} px a {args.dpi} dpi""")
    if n:
        print(f"  planche          : {args.sheet} -> {n} photos")
    print("Fichiers :")
    for f in made:
        print(f"  {f}")


if __name__ == "__main__":
    sys.exit(main())
