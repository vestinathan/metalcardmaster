#!/usr/bin/env python3
"""
Audit du cadrage des photos de cartes (CARDS) dans index.html.

Vérifie, pour chaque carte avec une photo, si un visage détecté serait coupé
par le crop réel de la fenêtre mini-carte/reveal-card (.rc-photo, 44% de
hauteur de carte, ratio carte 5:7), en tenant compte de la valeur photoY de
la carte (ou 22% par défaut, cf. CSS .rc-photo img).

IMPORTANT — formule de crop (object-fit: cover + object-position):
  scale = max(box_w / img_w, box_h / img_h)   # PAS une comparaison de ratio
  scaled_w, scaled_h = img_w * scale, img_h * scale
  excess_x, excess_y = scaled_w - box_w, scaled_h - box_h
  crop_x = excess_x * 0.5          # object-position X = "center" (fixe)
  crop_y = excess_y * (pos_y_pct / 100)
  fenêtre visible dans l'image source = (crop_x/scale .. crop_x/scale+box_w/scale,
                                           crop_y/scale .. crop_y/scale+box_h/scale)

Une version antérieure de ce script utilisait une comparaison de ratio
(img_ratio > win_ratio ?) pour décider quel axe est "limitant" — c'était
FAUX et a produit de nombreux faux négatifs (cartes avec visage coupé
classées "ok"). Ne pas réintroduire ce bug : toujours utiliser la formule
scale = max(...) ci-dessus, qui est la seule qui corresponde au
comportement réel de object-fit: cover (vérifié par rendu Playwright réel,
voir docs/adr/ si présent).

Usage:
    python3 scripts/audit_photo_crop.py [--out audit_results.json]

Sortie: un JSON avec, pour chaque carte, le verdict (ok / face_cut /
no_face_detected / missing_file) et, en cas de face_cut, le % de la zone de
visage qui tombe hors de la fenêtre visible.
"""
import argparse
import json
import os
import re
import sys

try:
    import cv2
except ImportError:
    print("cv2 (opencv-python) requis. pip install --break-system-packages opencv-python", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.join(REPO_ROOT, "index.html")

CARD_W_RATIO = 5.0
CARD_H_RATIO = 7.0
RC_PHOTO_HEIGHT_FRAC = 0.44  # .rc-photo { height: 44% } (non-légendaire)
DEFAULT_POS_Y = 22.0  # object-position: center 22% par défaut

FACE_VISIBLE_THRESHOLD = 0.55  # même seuil que l'audit précédent (overlap mini pour "visible")


def extract_cards():
    """Extrait id/name/photo/photoY/rarity depuis le tableau CARDS de index.html."""
    html = open(INDEX_HTML, encoding="utf-8").read()
    start = html.index("CARDS = [")
    i = html.index("[", start)
    depth = 0
    end_bracket = None
    for j in range(i, len(html)):
        if html[j] == "[":
            depth += 1
        elif html[j] == "]":
            depth -= 1
            if depth == 0:
                end_bracket = j
                break
    cards_src = html[i:end_bracket + 1]

    starts = [m.start() for m in re.finditer(r'\{\s*id:\s*"', cards_src)]
    entries = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(cards_src)
        block = cards_src[s:e]
        idm = re.search(r'id:\s*"([^"]+)"', block)
        namem = re.search(r'name:\s*"([^"]+)"', block)
        photom = re.search(r'photo:\s*"([^"]+)"', block)
        photoym = re.search(r'photoY:\s*"([^"]+)"', block)
        rarom = re.search(r'rarity:\s*"([^"]+)"', block)
        if idm and photom:
            entries.append({
                "id": idm.group(1),
                "name": namem.group(1) if namem else "?",
                "photo": photom.group(1),
                "photoY": float(photoym.group(1).replace("%", "")) if photoym else DEFAULT_POS_Y,
                "rarity": rarom.group(1) if rarom else None,
            })
    return entries


def visible_window(img_w, img_h, box_w_ratio, box_h_ratio, pos_y_pct):
    """
    Fenêtre visible dans l'image source (coordonnées pixel), pour une boîte
    d'aspect box_w_ratio:box_h_ratio, avec object-fit:cover et
    object-position: center {pos_y_pct}%.

    Formule validée contre le rendu réel (Playwright) — voir docstring module.
    """
    scale = max(box_w_ratio / img_w, box_h_ratio / img_h)
    scaled_w, scaled_h = img_w * scale, img_h * scale
    excess_x = scaled_w - box_w_ratio
    excess_y = scaled_h - box_h_ratio
    crop_x = excess_x * 0.5
    crop_y = excess_y * (pos_y_pct / 100.0)
    x0 = crop_x / scale
    y0 = crop_y / scale
    x1 = (crop_x + box_w_ratio) / scale
    y1 = (crop_y + box_h_ratio) / scale
    return (max(0, x0), max(0, y0), min(img_w, x1), min(img_h, y1))


_face_cascade = None
_profile_cascade = None


def _get_cascades():
    global _face_cascade, _profile_cascade
    if _face_cascade is None:
        _face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        _profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    return _face_cascade, _profile_cascade


def detect_faces(gray):
    face_cascade, profile_cascade = _get_cascades()
    faces = list(face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, minSize=(25, 25)))
    prof = list(profile_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, minSize=(25, 25)))
    flipped = cv2.flip(gray, 1)
    prof2 = list(profile_cascade.detectMultiScale(flipped, scaleFactor=1.05, minNeighbors=4, minSize=(25, 25)))
    w = gray.shape[1]
    prof2_mapped = [(w - x - fw, y, fw, fh) for (x, y, fw, fh) in prof2]
    return faces + prof + prof2_mapped


def audit_card(card, images_dir):
    path = os.path.join(images_dir, card["photo"])
    if not os.path.exists(path):
        return {**card, "verdict": "missing_file"}

    img = cv2.imread(path)
    if img is None:
        return {**card, "verdict": "missing_file"}

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(gray)

    entry = {**card, "img_w": w, "img_h": h, "num_faces_detected": len(faces)}

    if not faces:
        entry["verdict"] = "no_face_detected"
        return entry

    # fenêtre mini_reveal (contexte le plus contraignant, utilisé partout sauf légendaire plein cadre)
    win_h_units = RC_PHOTO_HEIGHT_FRAC * CARD_H_RATIO
    x0, y0, x1, y1 = visible_window(w, h, CARD_W_RATIO, win_h_units, card["photoY"])

    worst_visible_frac = 1.0
    for (fx, fy, fw, fh) in faces:
        fx1, fy1 = fx + fw, fy + fh
        inter_x0, inter_y0 = max(fx, x0), max(fy, y0)
        inter_x1, inter_y1 = min(fx1, x1), min(fy1, y1)
        inter_w, inter_h = max(0, inter_x1 - inter_x0), max(0, inter_y1 - inter_y0)
        inter_area = inter_w * inter_h
        face_area = fw * fh
        visible_frac = inter_area / face_area if face_area > 0 else 0
        worst_visible_frac = min(worst_visible_frac, visible_frac)

    entry["worst_face_visible_frac"] = round(worst_visible_frac, 3)
    entry["verdict"] = "face_cut" if worst_visible_frac < FACE_VISIBLE_THRESHOLD else "ok"
    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=os.path.join(REPO_ROOT, "scripts", "audit_results.json"))
    parser.add_argument("--images-dir", default=REPO_ROOT)
    args = parser.parse_args()

    cards = extract_cards()
    print(f"{len(cards)} cartes avec photo trouvées dans CARDS")

    results = []
    for i, card in enumerate(cards):
        results.append(audit_card(card, args.images_dir))
        if (i + 1) % 100 == 0:
            print(f"...{i + 1}/{len(cards)}")

    by_verdict = {}
    for r in results:
        by_verdict.setdefault(r["verdict"], []).append(r["id"])

    print("\n--- Résumé ---")
    for verdict, ids in sorted(by_verdict.items()):
        print(f"{verdict}: {len(ids)}")

    json.dump(results, open(args.out, "w"), indent=1, ensure_ascii=False)
    print(f"\nRésultats détaillés : {args.out}")

    face_cut = [r for r in results if r["verdict"] == "face_cut"]
    if face_cut:
        print("\nCartes avec visage potentiellement coupé (à vérifier visuellement) :")
        for r in sorted(face_cut, key=lambda r: r["worst_face_visible_frac"]):
            print(f"  {r['id']:30s} {r['name']:25s} visible={r['worst_face_visible_frac']:.0%}")


if __name__ == "__main__":
    main()
