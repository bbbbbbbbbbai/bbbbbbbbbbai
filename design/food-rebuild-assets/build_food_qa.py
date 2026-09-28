from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).parent
SOURCE = ROOT.parent / "screens"
NOW = datetime.now().astimezone().isoformat()
READ = "Read-only Figma use_figma inspection on 2026-09-28; file ptA7IsUhV0rHsp8yRLFRVj, page 70:6"


def e(value, status, source):
    return {"value": value, "status": status, "source": source}


def m(value, source=READ):
    return e(value, "measured", source)


def i(value, source="QA inference or proposed correction; original screenshot is authoritative"):
    return e(value, "inferred", source)


def u(source):
    return e(None, "unknown", source)


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def base(kind):
    return {
        "schemaVersion": "1.0.0",
        "artifactType": kind,
        "evidenceSchema": "Domain fields use value/status/source; measured, inferred and unknown are distinct. Metadata is authored.",
        "createdAt": m(NOW, "system clock"),
        "fileKey": m("ptA7IsUhV0rHsp8yRLFRVj"),
        "pageId": m("70:6"),
        "pageName": m("11 原图重建｜饮食"),
        "scope": m(["D01", "D02", "D03"], "assigned audit"),
        "sourceOfTruth": m("Original screens/D01.png, D02.png, D03.png", "parent instruction"),
        "writePolicy": m("Read-only Figma audit; local QA artifacts only", "tool log"),
        "deliveryState": i("IN_PROGRESS_NOT_ACCEPTED"),
    }


DATA = {
    "cat-rice": ("70:97", "1321112cfcf230a9723ae79ec1650350be8bbbf2", [("D01", "I70:307;70:305", [74.5, 338, 44, 40])]),
    "cat-meat": ("70:98", "7333cfad653404839f783135732d569e6887a4f8", [("D01", "I70:310;70:305", [234.5, 338, 44, 40])]),
    "cat-fish": ("70:99", "101665fb4cc7410b630b50d082b9238d8a222f4d", [("D01", "I70:313;70:305", [393.5, 338, 44, 40])]),
    "cat-veg": ("70:100", "56a0b60de7b6a60f4a9d2c380e387db509d1ea23", [("D01", "I70:316;70:305", [74.5, 449, 44, 40])]),
    "cat-fruit": ("70:101", "51eec47257db5b39624f1011468d4a768d073b60", [("D01", "I70:319;70:305", [234.5, 449, 44, 40])]),
    "cat-milk": ("70:102", "ec3edb601f2deae53267088be6ac33f577c9e389", [("D01", "I70:322;70:305", [393.5, 449, 44, 40])]),
    "rice": ("70:103", "adc6bde8da5e20c40eaa2a8faf4e9d1e5056e136", [("D01", "I70:393;70:381", [26, 610.5, 72, 62])]),
    "egg": ("70:104", "959df375f7a8d3374f0ec9e38b15e255bdc5ecb4", [("D01", "I70:406;70:381", [26, 698, 72, 62])]),
    "breast-icon": ("70:105", "649d585cb6f900a09ce0a92f59b5cb77184ba894", [("D01", "I70:419;70:381", [26, 787.5, 72, 62])]),
    "banana": ("70:106", "4fc6bc9c9b4d37cc5c7fe80fc3daf2eb0335d5b6", [("D01", "I70:432;70:381", [26, 878, 72, 62])]),
    "raw-breast": ("70:107", "e67ef79e661f272f9c3866acb191b437b09ac24b", [("D02", "I70:536;70:523", [26, 263, 72, 70])]),
    "cooked-breast": ("70:108", "62779d636d7877ba0444910d72279d0076943e8e", [("D02", "I70:550;70:523", [26, 369, 72, 70])]),
    "leg-icon": ("70:109", "962954ded5ca9ac07fee32f2813d0bfe0f9925e1", [("D02", "I70:564;70:523", [26, 475, 72, 70]), ("D02", "I70:578;70:523", [26, 581, 72, 70])]),
    "kungpao": ("70:110", "de690b52280d13490dac3d9088a621faa81a3670", [("D02", "I70:592;70:523", [26, 690, 72, 70])]),
    "white-chicken": ("70:111", "60419dd7f8f1f6e05b6ca66a1fb7062eb5cb466d", [("D02", "I70:606;70:523", [26, 800.5, 72, 70])]),
    "detail-chicken": ("70:112", "668fd44639e9217d0af074a4d4f3ff89a3c068ee", [("D03", "70:771", [22, 109, 182, 196])]),
    "status-ios": ("70:113", "4ad3ec4900edec158714524ad6119a8f03ac2ffa", [("D01", "70:228", [386, 14, 101, 19]), ("D02", "70:258", [386, 14, 101, 19])]),
    "status-android": ("70:114", "8c4149d2a3b2b2c60d56a6b90e67b91fb36e7cc3", [("D03", "70:763", [344, 7, 70, 23])]),
}
REGIONS = {
    "D01": [
        ("toolbar", [24, 51, 488, 95], ["70:229", "70:231"]),
        ("search", [25, 111, 488, 166], ["70:232", "70:233", "70:235"]),
        ("meal", [25, 181, 488, 236], ["70:236"]),
        ("tabs", [25, 253, 488, 303], ["70:245"]),
        ("categories", [25, 321, 488, 532], ["70:307", "70:310", "70:313", "70:316", "70:319", "70:322"]),
        ("heading", [25, 555, 488, 599], ["70:325", "70:882"]),
        ("list", [25, 599, 488, 955], ["70:392", "70:393", "70:406", "70:419", "70:432"]),
        ("gesture", [177, 1001, 336, 1009], ["70:256"]),
    ],
    "D02": [
        ("search", [27, 48, 489, 102], ["70:259", "70:261", "70:262", "70:264", "70:265"]),
        ("meal", [25, 118, 488, 173], ["70:267"]),
        ("tabs", [25, 188, 488, 238], ["70:276"]),
        ("results", [25, 250, 489, 890], ["70:535", "70:536", "70:550", "70:564", "70:578", "70:592", "70:606"]),
        ("pagination", [182, 925, 331, 957], ["70:620", "70:621", "70:623"]),
        ("gesture", [177, 1001, 336, 1009], ["70:287"]),
    ],
    "D03": [
        ("toolbar", [23, 47, 488, 86], ["70:764", "70:766", "70:767"]),
        ("food", [22, 109, 489, 306], ["70:771", "70:772", "70:773", "70:774", "70:775", "70:776", "70:778"]),
        ("portion_mode", [23, 328, 489, 372], ["70:781", "70:782", "70:783", "70:784"]),
        ("portion", [49, 382, 464, 486], ["70:785", "70:786", "70:787", "70:788", "70:789", "70:792"]),
        ("nutrition", [23, 505, 489, 679], ["70:827", "70:828", "70:829", "70:830", "70:831", "70:832"]),
        ("date", [26, 701, 489, 751], ["70:844", "70:846", "70:847", "70:848", "70:850"]),
        ("meal", [26, 764, 489, 814], ["70:851", "70:853", "70:854", "70:855", "70:857"]),
        ("notes", [26, 823, 489, 880], ["70:858", "70:860", "70:861", "70:862"]),
        ("save", [23, 903, 489, 970], ["70:863", "70:864"]),
        ("gesture", [184, 1004, 327, 1011], ["70:865"]),
    ],
}
TEXT = {
    "D01": [
        ("70:231", "记录饮食", [75, 57, 96, 34], 24, "Bold"),
        ("70:235", "搜索食物名称", [82, 124, 126, 30], 21, "Regular"),
        ("70:325", "常见食物", [26, 553, 92, 32], 23, "Bold"),
        ("I70:245;70:196", "全部", [63.75, 256, 40, 28], 20, "Bold"),
        ("I70:406;70:383", "鸡蛋", [118, 701, 40, 28], 20, "Medium"),
        ("I70:406;70:387", "143千卡", [341, 727.5, 75, 28], 20, "Medium"),
    ],
    "D02": [
        ("70:264", "鸡肉", [131, 60, 42, 30], 21, "Regular"),
        ("I70:536;70:525", "鸡胸肉（生）", [121, 259, 120, 28], 20, "Medium"),
        ("I70:536;70:526", "别名：鸡小胸、鸡里脊", [121, 287, 170, 25], 17, "Regular"),
        ("I70:536;70:527", "数据来源：示例", [121, 312, 119, 25], 17, "Regular"),
        ("I70:536;70:530", "120千卡", [349, 293, 75, 28], 20, "Medium"),
        ("I70:606;70:525", "白切鸡", [121, 796.5, 60, 28], 20, "Medium"),
        ("70:620", "1 / 1", [235, 924, 41, 28], 21, "Regular"),
    ],
    "D03": [
        ("70:766", "食物详情与份量", [76, 47, 182, 37], 26, "Bold"),
        ("70:772", "鸡胸肉（熟）", [225, 116, 168, 40], 28, "Bold"),
        ("70:773", "高蛋白 · 低脂肪 · 适合增肌减脂", [225, 165, 269, 26], 18, "Regular"),
        ("70:774", "鸡胸肉是优质蛋白质来源，\n脂肪含量低，适合日常健康饮食。", [225, 205, 270, 51], 18, "Regular"),
        ("70:775", "数据来源：示例营养数据", [225, 271, 187, 24], 17, "Regular"),
        ("70:785", "1份 = 100克", [206, 380, 105, 28], 20, "Regular"),
        ("70:787", "100", [205, 432, 50, 40], 28, "Bold"),
        ("70:828", "热量及营养换算（100克）", [40, 520, 259, 31], 22, "Bold"),
        ("70:847", "2025年4月24日（今天）", [241, 704, 218, 28], 20, "Regular"),
        ("70:862", "添加备注（可选）", [146, 829, 160, 28], 20, "Regular"),
        ("70:864", "保存记录", [207, 916, 100, 35], 25, "Bold"),
    ],
}

layout = base("layout")
layout["coordinateSystem"] = m("source pixels; viewport origin top-left; 512x1024; crop and ROI are LTRB exclusive right/bottom; Figma geometry is XYWH", "declared convention and PNG headers")
layout["screens"] = []
qa = base("qa-diff")
qa["screens"] = []
for code, node, instances in [("D01", "70:7", 23), ("D02", "70:9", 15), ("D03", "70:11", 2)]:
    source_path = SOURCE / f"{code}.png"
    current_path = ROOT / f"{code}-qa-readonly.png"
    original = Image.open(source_path).convert("RGB")
    current = Image.open(current_path).convert("RGB")
    assert original.size == current.size == (512, 1024)
    pair = Image.new("RGB", (1024, 1024), "white")
    pair.paste(original, (0, 0))
    pair.paste(current, (512, 0))
    pair_path = ROOT / f"{code}-qa-comparison.png"
    pair.save(pair_path)
    regions = []
    for name, roi, ids in REGIONS[code]:
        mae = sum(ImageStat.Stat(ImageChops.difference(original.crop(roi), current.crop(roi))).mean) / 3
        regions.append({
            "name": i(name), "sourceInspectionRoiLTRB": i(roi, "same-size manual visual region boundary; not original editable layer bounds"),
            "currentNodeIds": m(ids), "meanAbsoluteChannelError": m(round(mae, 4), "Pillow RGB difference in ROI; 0-255, not acceptance score"),
        })
    colors = []
    patches = [[220, 8, 290, 30], [350, 966, 470, 990]]
    if code == "D03":
        patches.append([36, 918, 170, 955])
    else:
        y = 181 if code == "D01" else 118
        patches.append([37, y + 10, 57, y + 42])
    for roi in patches:
        a, b = ImageStat.Stat(original.crop(roi)), ImageStat.Stat(current.crop(roi))
        colors.append({
            "roiLTRB": m(roi, "sampling coordinates"),
            "sourceMeanRGB": m([round(v, 3) for v in a.mean], "original pixel sample"),
            "sourceStddevRGB": m([round(v, 3) for v in a.stddev], "original pixel sample"),
            "currentMeanRGB": m([round(v, 3) for v in b.mean], "current pixel sample"),
            "currentStddevRGB": m([round(v, 3) for v in b.stddev], "current pixel sample"),
        })
    layout["screens"].append({
        "screen": m(code, "manifest"), "nodeId": m(node),
        "originalFile": m(str(source_path), "filesystem"), "originalSHA256": m(sha(source_path), "file bytes SHA256"),
        "sizePx": m([512, 1024], "PNG IHDR and Figma readback"),
        "topStatusBand": i([0, 0, 512, 38], "visible icons/time"),
        "gestureBand": i([0, 987, 512, 1024], "visible bar; not verified Android safe inset"),
        "trueDeviceDensity": u("Concept PNG has no dp/density metadata"),
        "scrollAndFixedBehavior": u("Single screenshot does not prove runtime scroll behavior"),
        "regions": regions,
        "keyTextGeometry": [{
            "nodeId": m(n), "content": m(text), "currentBoxXYWH": m(box),
            "currentFont": m({"family": "Noto Sans SC", "style": style, "sizePx": size}),
            "originalFont": u("Original generator font identity unavailable"),
            "fontPolicy": i("Explicit fallback; calibrate original glyph extent and baseline, do not use current box as original evidence"),
            "originalEditableBox": u("Raster has no original text-box metadata"),
        } for n, text, box, size, style in TEXT[code]],
        "colorSamples": colors,
        "visibleState": i({"D01": "早餐和全部选中；空搜索；常见食物", "D02": "鸡肉搜索；早餐和全部选中；6条结果；1/1分页", "D03": "收藏选中；克数选中；100克；午餐；空备注"}[code], "source screenshot"),
        "sourceMaterial": i("Subtle nonuniform light background and mottled green emphasis; current flat fills do not reproduce it"),
        "sourceRadiusAndStroke": u("Exact editable radii/stroke parameters cannot be proven from raster; measure edge contours before normalization"),
    })
    qa["screens"].append({
        "screen": m(code, "manifest"), "nodeId": m(node), "instances": m(instances),
        "currentScreenshot": m(str(current_path), "fresh download_assets render"),
        "currentScreenshotSHA256": m(sha(current_path), "SHA256"),
        "comparison": m(str(pair_path), "generated left original/right current"),
        "wholeImageMAE": m(round(sum(ImageStat.Stat(ImageChops.difference(original, current)).mean) / 3, 4), "Pillow"),
        "regionErrors": sorted(regions, key=lambda v: v["meanAbsoluteChannelError"]["value"], reverse=True),
        "acceptance": i("NOT_ACCEPTED"),
    })

asset_manifest = base("asset-manifest")
asset_manifest["mergedFrom"] = m(str(ROOT / "assets.json"), "input file kept unchanged")
asset_manifest["mergedFromSHA256"] = m(sha(ROOT / "assets.json"), "SHA256")
asset_manifest["assets"] = []
for source_record in json.loads((ROOT / "assets.json").read_text(encoding="utf-8-sig")):
    name = source_record["name"]
    master, image_hash, placements = DATA[name]
    path = Path(source_record["path"])
    crop = source_record["crop"]
    image = Image.open(path)
    source_path = SOURCE / f"{source_record['source']}.png"
    original = Image.open(source_path).convert("RGB")
    exact = image.size == (crop[2] - crop[0], crop[3] - crop[1]) and ImageChops.difference(original.crop(crop), image.convert("RGB")).getbbox() is None
    icon = name.startswith("cat-") or name in {"egg", "breast-icon", "banana", "leg-icon", "status-ios", "status-android"}
    positions = []
    for code, node, box in placements:
        source_box = [crop[0], crop[1], crop[2] - crop[0], crop[3] - crop[1]]
        positions.append({
            "screen": m(code), "nodeId": m(node), "currentBoxXYWH": m(box),
            "declaredSourceCropBoxXYWH": m(source_box, "assets.json declared original crop; first occurrence only"),
            "sourceBoxScope": i("For repeated occurrence, declared crop is extraction source, not automatically the occurrence position"),
            "sizeDeltaWH": m([box[2] - image.width, box[3] - image.height], "current instance size minus native asset size"),
            "scaleMode": m("FILL"),
            "correction": i("Keep the original native asset size inside a stable outer slot; swapping asset must not crop/scale every icon to the same rectangle."),
        })
    asset_manifest["assets"].append({
        "name": m(name, "assets.json"), "sourceScreen": m(source_record["source"], "assets.json"),
        "sourceFile": m(str(source_path), "assets.json source mapping"), "sourceSHA256": m(sha(source_path), "SHA256"),
        "cropLTRB": m(crop, "existing assets.json; exclusive right/bottom"),
        "file": m(str(path), "assets.json"), "fileSHA256": m(sha(path), "SHA256"),
        "sizePx": m(list(image.size), "Pillow PNG header"), "mode": m(image.mode, "Pillow"),
        "hasAlpha": m("A" in image.getbands(), "Pillow bands"), "exactDeclaredCrop": m(exact, "Pillow pixel comparison"),
        "imageHash": m(image_hash, "current Figma IMAGE fill readback; opaque Figma hash, not SHA256"),
        "masterId": m(master), "placements": positions,
        "representation": m("bitmap icon/artwork" if icon else "bitmap food photograph", "original PNG crop and IMAGE fill"),
        "vectorClaim": m(False, "Not vectorized; native pixels inside a component"),
        "sourcePipeline": m("clean source extraction", "assets.json plus exact pixel comparison"),
        "generationModel": m(None, "no new generation in this audit"),
        "editability": i("Independent replaceable asset component; internal raster strokes/pixels are not editable vectors"),
        "edgeRisk": i("Opaque source-matte pixels may remain around icon. Keep source crop or use approved clean extraction; never pretend raster icons are vector paths."),
    })

components = base("component-plan")
components["existingLibrary"] = {
    "location": m("same page 70:6, below screens; positioned master grid"),
    "masterCount": m(23),
    "overlap": m("masters have explicit distributed x/y, not all at origin", "readback positions x200..2482, y1400..1990"),
    "mustPreserve": i(True),
    "assetMasters": m([value[0] for value in DATA.values()]),
}
PLAN = [
    ("区域 / 餐次选择", "70:185", ["70:236", "70:267"], "Preserve master. Measure selected capsule x/width and source separators; expose selectedMeal variant without inventing unobserved style.", ["SelectedMeal:VARIANT"]),
    ("区域 / 食物来源筛选", "70:194", ["70:245", "70:276"], "Keep master but calibrate labels; current 全部 x63.75 versus source visible left near58. Source underlines stay measured.", ["SelectedTab:VARIANT"]),
    ("控件 / 食物分类", "70:304", ["70:307", "70:310", "70:313", "70:316", "70:319", "70:322"], "Stop forcing every raster artwork into44x40. Fixed outer slot may contain native-size centered inner asset.", ["名称:TEXT", "Artwork:INSTANCE_SWAP"]),
    ("列表项 / 常见食物", "70:379", ["70:393", "70:406", "70:419", "70:432"], "Retain row/master, fix per-asset natural image size inside stable slot; do not enlarge egg to72x62.", ["食物名称:TEXT", "热量:TEXT", "来源:TEXT", "Artwork:INSTANCE_SWAP", "Add:INSTANCE_SWAP"]),
    ("列表项 / 食物搜索结果", "70:521", ["70:536", "70:550", "70:564", "70:578", "70:592", "70:606"], "Retain row/master. Leg icon native59x55 vs current72x70. Preserve source occurrence y positions and row separators.", ["名称:TEXT", "别名:TEXT", "来源:TEXT", "热量:TEXT", "Artwork:INSTANCE_SWAP", "Add:INSTANCE_SWAP"]),
    ("控件 / 添加食物", None, ["70:379", "70:521"], "Extract existing add circle into one explicit master used inside both row masters; source control artwork is not automatically vector truth.", ["Icon:INSTANCE_SWAP"]),
    ("区域 / 食物详情", None, ["70:771", "70:772", "70:773", "70:774", "70:775", "70:776", "70:778"], "D03 currently has only two asset instances and flat sibling UI. Assemble measured image/info region without covering existing text.", ["Photo:INSTANCE_SWAP", "Name:TEXT", "Description:TEXT", "Favorite:BOOLEAN"]),
    ("区域 / 份量选择", None, ["70:781", "70:782", "70:783", "70:784", "70:785", "70:786", "70:787", "70:788", "70:789", "70:792"], "Build mode/stepper masters with fixed measured geometry and editable value/unit. Do not normalize original different circle locations.", ["Mode:VARIANT", "Value:TEXT", "Unit:TEXT"]),
    ("区域 / 营养换算", None, ["70:827", "70:828", "70:829", "70:830", "70:831", "70:832", "70:833", "70:835", "70:838", "70:841"], "Build repeated nutrient cell master; preserve source typography, units and divider positions.", ["Value:TEXT", "Unit:TEXT", "Label:TEXT"]),
    ("列表项 / 记录属性", None, ["70:844", "70:846", "70:847", "70:848", "70:851", "70:853", "70:854", "70:855", "70:858", "70:860", "70:861", "70:862"], "Date/meal/notes structured rows, icon asset instance. Date and meal chevrons share one master.", ["Label:TEXT", "Value:TEXT", "Icon:INSTANCE_SWAP", "ShowChevron:BOOLEAN"]),
    ("控件 / 保存记录", None, ["70:863", "70:864"], "Combine background/label into button master and instance; source weight and mottled material differ.", ["Label:TEXT"]),
    ("图标 / 导航与操作", None, ["70:229", "70:233", "70:259", "70:262", "70:265", "70:621", "70:623", "70:764", "70:767", "70:776", "70:778", "70:848", "70:855"], "Repeated search/back/chevrons should use masters; inspect or extract original icon pixels first. Existing recreated vector is an approximation, not original vector.", ["Artwork:INSTANCE_SWAP"]),
]
components["plan"] = [{
    "name": i(name), "existingMasterId": m(master) if master else u("Not found in inspected current component graph"),
    "currentInstancesOrNodes": m(nodes), "action": i(action), "properties": i(props),
    "writer": i("Single parent orchestrator only"),
} for name, master, nodes, action, props in PLAN]
components["replacementSafety"] = i("Save old node, parent, coordinates, z-order and overrides; remove only replaced own visuals. Verify one visible instance, no duplicate or opaque overlay.")


def issue(key, priority, nodes, observed, cause, action, basis="same-size screenshot plus Figma readback"):
    return {
        "id": key, "priority": i(priority), "nodeIds": m(nodes),
        "observed": m(observed, basis), "cause": i(cause),
        "action": i(action), "state": i("OPEN"),
    }


qa["issues"] = [
    issue("FOOD-01", "P1", ["I70:406;70:381", "70:104", "70:379"],
          "D01 egg source crop53x58 at35,699 is shown in72x62 at26,698; visible egg is enlarged.",
          "Food-row image swap resizes natural-size source into common slot with FILL.",
          "Keep outer72x62 slot if needed; set inner egg to53x58 and source-relative x35/y699. Re-export without changing row text."),
    issue("FOOD-02", "P1", ["I70:564;70:523", "I70:578;70:523", "70:109", "70:521"],
          "D02 leg-icon source59x55 is rendered72x70 in both occurrences; icon strokes and silhouette visibly enlarge.",
          "Common result photo slot drives the line-art instance dimensions.",
          "Reuse70:109 twice at native59x55; first source crop32,480; measure second occurrence independently, do not apply photo FILL geometry."),
    issue("FOOD-03", "P1", ["70:304", "I70:310;70:305", "I70:313;70:305", "I70:316;70:305", "I70:319;70:305", "I70:322;70:305"],
          "Five category asset native sizes differ, but every current placement is44x40; positions also shift.",
          "Swap updates identity but not source-specific size/crop.",
          "Use exact assets.json crop sizes and positions; inner natural-sized asset in stable card. Retain category master and expose INSTANCE_SWAP."),
    issue("FOOD-04", "P1", ["70:11", "70:781", "70:786", "70:827", "70:863"],
          "D03 has only two instances, both asset components; controls and meaningful regions are flat siblings.",
          "D03 source reproduction stopped before region/control componentization.",
          "Execute D03 region plans incrementally; preserve current measured geometry and text and return all replacement IDs."),
    issue("FOOD-05", "P2", ["70:194", "I70:245;70:196", "I70:276;70:196", "70:185"],
          "全部 labels and breakfast capsule width/center differ visibly from source; current 全部 x63.75 is right of source ink near58.",
          "Equal-width slot centering replaces measured source typography/spacing.",
          "Calibrate label ink extent and capsule edges against source, not a generic four-equal-column assumption. Preserve source divider strokes."),
    issue("FOOD-06", "P2", ["70:379", "70:521", "70:773", "70:775", "70:828", "70:864"],
          "Fallback Noto Sans SC glyph widths/weights differ; D03 source-information text sits very close to info icon and save label is heavier.",
          "Original font is unknown; current fallback is not source typography evidence.",
          "Record font fallback; measure text ink width and baseline per ROI, especially D03 source line/icon gap, nutrition heading and save label. Do not reflow unrelated content."),
    issue("FOOD-07", "P2", ["70:185", "70:782", "70:789", "70:792", "70:863"],
          "Original green controls contain tonal variation; current green fills are uniform.",
          "Source material not recreated.",
          "Extract or generate only button/control material, retaining text/geometry native and preserving independent source asset provenance."),
    issue("FOOD-08", "P2", ["70:379", "70:521", "70:229", "70:259", "70:848", "70:855"],
          "Repeated row add controls and navigation icons do not appear as dedicated icon/control masters in23-master readback.",
          "Vectors are embedded in larger structures or standalone frames.",
          "Create shared masters for repeated interaction icons, reuse inside row masters, and retain original bitmap artwork as bitmap rather than claiming source vectors."),
    issue("FOOD-09", "P1_behavior_P3_visual", ["70:773", "70:774", "70:833", "70:847"],
          "Source shows nutritional example values, health-related descriptive copy and2025年4月24日（今天）. These are screenshot examples, not current personal facts.",
          "Generated concept text and known reviewNotes.",
          "Keep traceable visual reference variant; production must use actual data and date, remove unverified nutrition/fitness assertions according to manifest."),
]
qa["evidenceNotes"] = [
    m("D01/D02 qa1 exports were provided; fresh read-only exports were taken because live node70:882 adds a divider not visible in earlier D01 qa1.", "local files and live readback"),
    i("A screenshot difference is not proof of wrong file; file/page/node identity was explicitly verified."),
    i("Whole-image MAE and per-region MAE are diagnostics, not completion scores."),
]
qa["gates"] = {
    "sameSize": m("PASS", "Pillow512x1024 source/current checks"),
    "identity": m("PASS", READ),
    "bitmapIconsCorrectlyClassified": m("PASS", "IMAGE fills, hashes and pixel source crops"),
    "masterGridNotAtOrigin": m("PASS", READ),
    "allRegionsComponentized": m("FAIL", "D03 only2 asset instances"),
    "assetNativeGeometry": m("FAIL", "source/current image dimensions above"),
    "fontExactness": u("Original font unavailable"),
    "twoRepairLoops": u("Not established by this read-only audit"),
    "disposableEditSwapTest": m("NOT_RUN", "QA-only scope"),
    "finalAcceptance": i("NOT_ACCEPTED; parent writer must fix and re-export"),
}
for filename, payload in [
    ("layout.json", layout), ("asset-manifest.json", asset_manifest),
    ("component-plan.json", components), ("qa-diff.json", qa),
]:
    destination = ROOT / filename
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    json.loads(destination.read_text(encoding="utf-8"))
    print(filename, destination.stat().st_size)
print("assets.json preserved SHA256", sha(ROOT / "assets.json"))
print("exact crops", sum(a["exactDeclaredCrop"]["value"] for a in asset_manifest["assets"]), "/", len(asset_manifest["assets"]))
