from pathlib import Path
from PIL import Image, ImageChops, ImageStat
import json

out = Path(__file__).parent
source = out.parent / "screens"
report = []
for code, node_id, text_count in [
    ("A02", "70:14", 17),
    ("A03", "70:16", 15),
    ("A04", "70:18", 11),
    ("A05", "70:20", 18),
]:
    original = Image.open(source / f"{code}.png").convert("RGB")
    editable = Image.open(out / f"{code}-editable.png").convert("RGB")
    assert original.size == editable.size == (512, 1024)
    comparison = Image.new("RGB", (1024, 1024), "white")
    comparison.paste(original, (0, 0))
    comparison.paste(editable, (512, 0))
    comparison.save(out / f"{code}-comparison.png")
    diff = ImageChops.difference(original, editable)
    mae = sum(ImageStat.Stat(diff).mean) / 3
    report.append({
        "screen": code,
        "nodeId": node_id,
        "pageId": "70:13",
        "dimensions": [512, 1024],
        "editableTextNodes": text_count,
        "wholeImageMeanAbsoluteChannelError": round(mae, 3),
        "pixelIdentical": False,
        "screenshot": str(out / f"{code}-editable.png"),
        "comparison": str(out / f"{code}-comparison.png"),
    })
(out / "verification.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(report, ensure_ascii=False, indent=2))
