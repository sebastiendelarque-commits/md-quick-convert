#!/usr/bin/env python3
"""Superpose une grille de coordonnees sur une photo pour relever les reperes
(menton, sommet du crane, sommet de la chevelure, axe du visage) en pixels.

  python3 grille.py photo.jpg -o grille.png            # vue d'ensemble
  python3 grille.py photo.jpg --box 700 1900 1700 2500 # zoom sur le menton

Les nombres imprimes sont les coordonnees dans l'image SOURCE : ils se passent
tels quels a make_id_photo.py.
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--output", type=Path, default=Path("grille.png"))
    p.add_argument("--box", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"),
                   help="zone a agrandir (px source)")
    p.add_argument("--step", type=int, default=None, help="pas de la grille (px source)")
    p.add_argument("--width", type=int, default=900, help="largeur de l'apercu")
    p.add_argument("--brightness", type=float, default=1.0,
                   help=">1 pour eclaircir les zones sombres (menton, cheveux)")
    args = p.parse_args()

    im = Image.open(args.input).convert("RGB")
    x0, y0, x1, y1 = args.box if args.box else (0, 0, *im.size)
    crop = im.crop((x0, y0, x1, y1))
    if args.brightness != 1.0:
        crop = ImageEnhance.Brightness(crop).enhance(args.brightness)

    step = args.step or max(10, round((x1 - x0) / 16 / 10) * 10)
    major = step * 4
    scale = args.width / (x1 - x0)
    view = crop.resize((args.width, int((y1 - y0) * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(view)

    for y in range(y0 - y0 % step, y1, step):
        yy = (y - y0) * scale
        is_major = y % major == 0
        d.line([(0, yy), (view.width, yy)],
               fill=(255, 0, 0) if is_major else (0, 235, 235), width=2 if is_major else 1)
        d.text((4, yy + 2), str(y), fill=(255, 0, 0) if is_major else (0, 120, 150))
    for x in range(x0 - x0 % step, x1, step):
        xx = (x - x0) * scale
        is_major = x % major == 0
        d.line([(xx, 0), (xx, view.height)],
               fill=(255, 0, 0) if is_major else (0, 235, 235), width=2 if is_major else 1)
        d.text((xx + 2, 4), str(x), fill=(255, 0, 0) if is_major else (0, 120, 150))

    view.save(args.output)
    print(f"{args.output}  ({view.width}x{view.height}, pas {step} px, "
          f"zone {x0},{y0} -> {x1},{y1})")


if __name__ == "__main__":
    main()
