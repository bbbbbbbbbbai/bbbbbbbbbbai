from datetime import datetime
from pathlib import Path
from hashlib import sha256
import json
from PIL import Image, ImageChops, ImageStat

root = Path(__file__).parent
source = root.parent / "screens"


def mean_error(a, b, box):
    return round(sum(ImageStat.Stat(ImageChops.difference(a.crop(box), b.crop(box))).mean) / 3, 4)


def bounds(image, box, kind):
    area = image.crop(box).convert("RGB")
    values = list(area.getdata())
    if kind == "green":
        pixels = [255 if g-r > 35 and g-b > 8 and g < 190 else 0 for r, g, b in values]
    else:
        pixels = [255 if max(p) < 130 else 0 for p in values]
    mask = Image.new("L", area.size)
    mask.putdata(pixels)
    result = mask.getbbox()
    return [result[0]+box[0], result[1]+box[1], result[2]+box[0], result[3]+box[1]] if result else None


checks = [
    ("D01", "cat-rice", "I70:307;70:305;92:192", [74.5,338,44,40], [73,338,44,40], [68,331,123,384]),
    ("D01", "cat-meat", "I70:310;70:305;92:193", [232.5,336.5,48,43], [232,336,48,43], [225,330,286,385]),
    ("D01", "cat-fish", "I70:313;70:305;92:194", [389.5,337.5,52,41], [389,338,52,41], [383,331,447,385]),
    ("D01", "cat-veg", "I70:316;70:305;92:195", [74,447,45,44], [73,446,45,44], [68,440,124,496]),
    ("D01", "cat-fruit", "I70:319;70:305;92:196", [233,445.5,47,47], [231,444,47,47], [225,438,285,498]),
    ("D01", "cat-milk", "I70:322;70:305;92:197", [393.5,446,44,46], [394,445,44,46], [387,439,444,498]),
    ("D01", "rice", "I70:393;70:381;92:182", [26,610.5,72,62], [27,612,72,62], [20,605,105,680]),
    ("D01", "egg", "I70:406;70:381;92:183", [35.5,700,53,58], [35,699,53,58], [20,693,105,765]),
    ("D01", "breast-icon", "I70:419;70:381;92:184", [26.5,791.5,71,54], [25,791,71,54], [19,785,105,852]),
    ("D01", "banana", "I70:432;70:381;92:185", [28,880,68,58], [26,879,68,58], [19,873,104,945]),
    ("D02", "leg-icon-first", "I70:564;70:523;93:194", [32.5,482.5,59,55], [32,480,59,55], [22,474,103,543]),
    ("D02", "leg-icon-second", "I70:578;70:523;93:194", [32.5,588.5,59,55], None, [22,580,103,649]),
    ("D02", "kungpao", "I70:592;70:523;93:195", [25.5,690.5,73,69], [26,689,73,69], [19,682,106,767]),
    ("D02", "white-chicken", "I70:606;70:523;93:196", [22,804,80,63], [23,799,80,63], [16,792,110,875]),
]
report = {
    "schemaVersion": "1.0.0",
    "round": 2,
    "createdAt": datetime.now().astimezone().isoformat(),
    "fileKey": "ptA7IsUhV0rHsp8yRLFRVj",
    "pageId": "70:6",
    "scope": ["70:7", "70:9"],
    "figmaMutationPerformed": False,
    "conclusion": "Native image-size correction is persisted in screen instances and visibly improves prior enlargement. Pixel/position/typography parity is not yet accepted.",
    "screens": [],
    "nativeImageChecks": [],
}
images = {}
for code, node in [("D01", "70:7"), ("D02", "70:9")]:
    original = Image.open(source / f"{code}.png").convert("RGB")
    before = Image.open(root / f"{code}-qa-readonly.png").convert("RGB")
    after_path = root / f"{code}-qa-round2.png"
    after = Image.open(after_path).convert("RGB")
    assert original.size == before.size == after.size == (512, 1024)
    images[code] = original, before, after
    pair = Image.new("RGB", (1024, 1024), "white")
    pair.paste(original, (0, 0))
    pair.paste(after, (512, 0))
    pair_path = root / f"{code}-qa-round2-comparison.png"
    pair.save(pair_path)
    report["screens"].append({
        "screen": code, "nodeId": node, "screenshot": str(after_path),
        "screenshotSHA256": sha256(after_path.read_bytes()).hexdigest(),
        "comparison": str(pair_path),
        "size": [512, 1024],
        "wholeImageMAEBefore": mean_error(original, before, [0,0,512,1024]),
        "wholeImageMAEAfter": mean_error(original, after, [0,0,512,1024]),
        "metricsCaution": "Diagnostic only; whole-image score dominated by white-space and unrelated text/material differences.",
    })
for code, name, node, current, expected, roi in checks:
    original, before, after = images[code]
    natural_size = [59,55] if expected is None else expected[2:]
    report["nativeImageChecks"].append({
        "screen": code, "asset": name, "nodeId": node,
        "currentBoxXYWH": {"status": "measured", "value": current, "source": "fresh read-only Figma rectangle boundary"},
        "originalCropBoxXYWH": {"status": "measured" if expected else "unknown", "value": expected, "source": "assets.json first-occurrence crop; second leg occurrence not independently cropped"},
        "nativeDimensionsRestored": current[2:] == natural_size,
        "offsetXY": [round(current[n]-expected[n],2) for n in (0,1)] if expected else None,
        "comparisonRoiLTRB": roi,
        "roiMAEBefore": mean_error(original, before, roi),
        "roiMAEAfter": mean_error(original, after, roi),
    })
measurements = {}
for code, selected_roi, all_roi in [
    ("D01", [20,176,150,239], [49,255,109,290]),
    ("D02", [20,113,150,176], [49,188,109,223]),
]:
    a, _, b = images[code]
    measurements[code] = {
        "breakfastGreenOriginalLTRB": bounds(a, selected_roi, "green"),
        "breakfastGreenCurrentLTRB": bounds(b, selected_roi, "green"),
        "allTabOriginalLTRB": bounds(a, all_roi, "green"),
        "allTabCurrentLTRB": bounds(b, all_roi, "green"),
    }
a, _, b = images["D02"]
measurements["D02"]["firstNameOriginalLTRB"] = bounds(a, [116,258,320,289], "dark")
measurements["D02"]["firstNameCurrentLTRB"] = bounds(b, [116,258,320,289], "dark")
report["measuredInkAndControlBounds"] = measurements
report["topThreeRemainingVisibleDifferences"] = [
    {
        "rank": 1, "status": "measured",
        "issue": "Asset dimensions are restored but some placement offsets and half-pixel positions remain.",
        "nodes": ["I70:606;70:523;93:196", "I70:564;70:523;93:194", "I70:319;70:305;92:196"],
        "examples": "White chicken remains y804 vs source799 (+5px); first leg y482.5 vs480 (+2.5px); fruit x233/y445.5 vs231/444 (+2/+1.5px).",
        "action": "Retain corrected fixed shells; align internal native-pixel rectangles to measured source location. Prioritize white-chicken y-5 and first-leg y-2.5. Avoid changing shared master to fix one occurrence without checking other instances.",
    },
    {
        "rank": 2, "status": "measured",
        "issue": "Selected breakfast capsule geometry and the 全部 label alignment still differ; source meal divider strokes are not visible in current output.",
        "nodes": ["70:185", "70:194", "70:236", "70:267", "I70:245;70:196", "I70:276;70:196"],
        "action": "Use measuredInkAndControlBounds for capsule edges/tab ink alignment. Calibrate the selected pill and reintroduce source separator strokes; do not resize all slots.",
    },
    {
        "rank": 3, "status": "measured",
        "issue": "Typography remains a fallback: D02 result names and numeric labels have different glyph widths/weights; original green mottling/light surface variation is replaced with flat fills.",
        "nodes": ["70:521", "70:379", "I70:536;70:525", "I70:536;70:530", "70:185"],
        "action": "Match text ink extents/baselines and weight against original. Preserve editable text; treat source texture as isolated material, not UI screenshot overlay.",
    },
]
report["acceptance"] = {
    "nativeSizeFix": "PASS",
    "sourcePositionParity": "PARTIAL",
    "overallVisualParity": "NOT_ACCEPTED",
    "bitmapDisclosure": "All corrected source icons remain independent bitmap rectangles inside shared component masters, not vector artwork.",
}
(root / "qa-round2.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"screens": report["screens"], "measurements": measurements, "nativeSizePass": all(x["nativeDimensionsRestored"] for x in report["nativeImageChecks"])}, ensure_ascii=False, indent=2))
