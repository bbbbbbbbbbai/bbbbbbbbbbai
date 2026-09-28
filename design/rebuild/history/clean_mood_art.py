"""Extract source F07 symbols and remove edge-connected pale source matte."""

from collections import deque
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "screens/F07.png"
OUTPUT = Path(__file__).resolve().parent / "assets"
CROPS = {
    "status": (359, 32, 435, 62),
    "back": (25, 99, 61, 136),
    "edit": (344, 87, 381, 125),
    "delete": (432, 87, 466, 126),
    "sleep": (27, 579, 79, 620),
    "date": (30, 724, 75, 774),
    "note": (31, 879, 74, 929),
}


def clean(image):
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    removed = set()
    queue = deque(
        [(x, y) for x in range(width) for y in (0, height - 1)]
        + [(x, y) for y in range(height) for x in (0, width - 1)]
    )
    while queue:
        x, y = queue.popleft()
        if (x, y) in removed:
            continue
        color = pixels[x, y]
        # Pale neutral pixels are background only when connected to an edge.
        if min(color) < 210 or max(color) - min(color) > 23:
            continue
        removed.add((x, y))
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                queue.append((nx, ny))
    result = rgb.convert("RGBA")
    for x, y in removed:
        result.putpixel((x, y), (*pixels[x, y], 0))
    return result, len(removed)


def main():
    OUTPUT.mkdir(exist_ok=True)
    source = Image.open(SOURCE)
    records = []
    for name, box in CROPS.items():
        result, removed = clean(source.crop(box))
        path = OUTPUT / f"F07-{name}-clean.png"
        result.save(path)
        records.append({
            "name": name,
            "cropLTRB": box,
            "path": str(path),
            "dimensions": result.size,
            "removedBackgroundPixels": removed,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "alpha": True,
            "method": "edge-connected pale-neutral matte removal",
            "status": "derived source asset; requires visual verification",
        })
    (OUTPUT / "F07-clean-manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(records, ensure_ascii=False))


if __name__ == "__main__":
    main()
