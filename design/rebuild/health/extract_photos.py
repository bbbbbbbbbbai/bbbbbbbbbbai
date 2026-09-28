"""Separate concept-image attachment photos from their overlaid close controls."""

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / "assets"
OUT.mkdir(exist_ok=True)
source = Image.open(ROOT / "screens" / "E02.png").convert("RGB")
records = []

for name, box, center in [
    ("exercise-photo-1-clean", (24, 715, 161, 804), (120, 17)),
    ("exercise-photo-2-clean", (178, 715, 315, 804), (119, 17)),
]:
    crop = np.array(source.crop(box))
    mask = np.zeros(crop.shape[:2], dtype=np.uint8)
    cv2.circle(mask, center, 13, 255, -1)
    repaired = cv2.inpaint(crop, mask, 3, cv2.INPAINT_TELEA)
    path = OUT / f"{name}.png"
    Image.fromarray(repaired).save(path)
    records.append({
        "id": name,
        "source": "screens/E02.png",
        "cropLTRB": box,
        "path": str(path),
        "sourceType": "original Sunburst photo crop",
        "processing": "Local inpainting only under the close-control circle",
        "inferredArea": {"center": center, "radius": 13},
        "limitation": "Occluded original photo pixels are unknown; this area is reconstructed.",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    })

close = source.crop((132, 719, 158, 745)).convert("RGBA")
alpha = Image.new("L", close.size)
ImageDraw.Draw(alpha).ellipse((1, 1, 25, 25), fill=255)
close.putalpha(alpha)
close_path = OUT / "photo-close.png"
close.save(close_path)
records.append({
    "id": "photo-close",
    "source": "screens/E02.png",
    "cropLTRB": [132, 719, 158, 745],
    "path": str(close_path),
    "processing": "Independent source close-control artwork; elliptical alpha mask",
    "geometryStatus": "inferred",
    "sha256": hashlib.sha256(close_path.read_bytes()).hexdigest(),
})

(BASE / "photo-processing.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps({"created": [r["path"] for r in records]}))
