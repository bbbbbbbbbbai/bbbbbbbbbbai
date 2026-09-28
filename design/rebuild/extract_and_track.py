"""Extract source artwork and maintain evidence for the Figma reconstruction."""

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
ASSETS = OUT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

CROPS = {
    "A01": {
        "brand-photo": (23, 162, 489, 309),
        "mail": (54, 481, 82, 509),
        "lock": (54, 589, 82, 620),
        "eye": (430, 590, 462, 620),
    },
    "C01": {
        "food-action": (37, 408, 115, 485),
        "exercise-action": (156, 408, 235, 485),
        "weight-action": (277, 408, 355, 485),
        "mood-action": (398, 408, 477, 485),
        "breakfast": (28, 608, 111, 682),
        "walk-record": (34, 705, 106, 777),
        "weight-record": (34, 802, 106, 873),
        "nav-home": (48, 908, 87, 945),
        "nav-records": (176, 908, 210, 945),
        "nav-aspiration": (300, 908, 341, 945),
        "nav-profile": (430, 908, 465, 945),
    },
    "C02": {
        "status": (382, 12, 484, 36),
        "food-action": (57, 480, 94, 521),
        "exercise-action": (174, 480, 216, 522),
        "weight-action": (295, 480, 336, 522),
        "mood-action": (415, 480, 456, 522),
        "empty-notebook": (220, 697, 290, 772),
        "nav-home": (52, 910, 91, 947),
        "nav-records": (178, 911, 213, 947),
        "nav-aspiration": (300, 911, 337, 947),
        "nav-profile": (425, 912, 458, 947),
    },
}

assets = []
for code, crops in CROPS.items():
    source_path = ROOT / "screens" / f"{code}.png"
    source = Image.open(source_path)
    for name, bounds in crops.items():
        path = ASSETS / f"{code}-{name}.png"
        source.crop(bounds).save(path)
        assets.append({
            "id": f"{code}-{name}",
            "source": str(source_path),
            "sourceCanvas": list(source.size),
            "crop": {"value": list(bounds), "evidence": "measured"},
            "path": str(path),
            "size": [bounds[2] - bounds[0], bounds[3] - bounds[1]],
            "sourceType": "extracted from approved Sunburst concept image",
            "alpha": False,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "containsEditableText": False,
            "figmaComponentId": None,
            "review": "crop requires visual inspection before binding",
        })

(OUT / "asset-manifest.json").write_text(
    json.dumps({"version": 1, "assets": assets}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
status_path = OUT / "rebuild-status.json"
if not status_path.exists():
    status = {
        "version": 1,
        "fileKey": "ptA7IsUhV0rHsp8yRLFRVj",
        "tool": "official Figma MCP; Figwright is not exposed in this environment",
        "phase": "reconstruction-and-qa",
        "currentBatch": ["A01", "A02", "A03", "A04", "A05", "C01", "C02",
                         "D01", "D02", "D03", "I01", "I02", "I03"],
        "accepted": [],
        "blocked": [],
        "nextAction": "Bind exact extracted artwork, componentize, and run two QA rounds",
        "lastEvidence": "A01 actual inline Figma render; auth and food local comparison renders",
        "pages": [
            {"id": p["id"], "name": p["name"], "source": p["image"],
             "status": "not-accepted",
             "requiredVariants": [v["id"] for v in p.get("variants", [])]}
            for p in manifest["pages"]
        ],
        "gate": {
            "sourceHiddenExport": False,
            "twoVisualRepairRounds": False,
            "componentInstances": False,
            "editableTextAndControls": False,
            "assetSwapTest": False,
            "noOverlapsOrClipping": False,
        },
        "font": {
            "sourceFamily": "unknown: raster-generated reference",
            "fallback": "Noto Sans SC",
            "status": "requires text-metric comparison per page",
        },
    }
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2),
                           encoding="utf-8")

print(json.dumps({"assetCount": len(assets), "output": str(OUT)}))
