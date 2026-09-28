from pathlib import Path
from hashlib import sha256
from datetime import datetime
import json
from PIL import Image, ImageStat

ROOT = Path(__file__).parent
SOURCE = ROOT.parent.parent / "screens"
MANIFEST = ROOT.parent.parent / "manifest.json"
ROOT.mkdir(parents=True, exist_ok=True)


def ev(value, status, source):
    return {"value": value, "status": status, "source": source}


def measured(value, source="Original PNG at 1:1; manual visible-edge measurement, tolerance 1-2px"):
    return ev(value, "measured", source)


def inferred(value, source="Layout/typography candidate inferred from original raster"):
    return ev(value, "inferred", source)


def unknown(reason):
    return ev(None, "unknown", reason)


# Text boxes below are editing-layout candidates. Pixel ink boxes are measured
# independently inside these local inspection windows, not claimed source frames.
# id, content, candidate x/y/w/h, candidate font size, weight, light text
TEXT = {
    "E01": [
        ("time", "9:41", [25,7,60,27],18,400,False),
        ("battery", "100%", [427,7,65,27],17,400,False),
        ("title", "健康记录", [170,48,174,39],26,700,False),
        ("history", "历史", [447,54,49,33],23,400,False),
        ("exercise-heading", "运动", [24,130,110,36],26,700,False),
        ("exercise-1-title", "跑步30分钟", [88,195,330,32],21,400,False),
        ("exercise-1-date", "2024年3月10日 07:20", [88,230,331,29],18,400,False),
        ("exercise-2-title", "步行25分钟", [88,290,330,32],21,400,False),
        ("exercise-2-date", "2024年3月9日 18:40", [88,325,331,29],18,400,False),
        ("weight-heading", "体重", [24,411,110,38],26,700,False),
        ("weight-1-value", "69.5kg", [88,477,330,33],22,400,False),
        ("weight-1-date", "2024年3月10日 08:00", [88,512,331,29],18,400,False),
        ("weight-2-value", "69.7kg", [88,573,330,33],22,400,False),
        ("weight-2-date", "2024年3月9日 08:10", [88,608,331,29],18,400,False),
        ("mood-heading", "心情", [24,697,110,38],26,700,False),
        ("mood-1-value", "轻松", [88,765,330,31],21,400,False),
        ("mood-1-date", "2024年3月10日 21:30", [88,799,331,29],18,400,False),
        ("mood-2-value", "还行", [88,861,330,31],21,400,False),
        ("mood-2-date", "2024年3月9日 20:15", [88,895,331,29],18,400,False),
    ],
    "E02": [
        ("time","9:41",[23,3,61,27],17,400,False),
        ("battery","100%",[435,3,65,27],17,400,False),
        ("title","E02 运动记录",[153,43,206,34],24,700,False),
        ("type-label","运动类型",[23,198,160,28],18,400,False),
        ("type-run","跑步",[20,274,87,28],18,500,True),
        ("type-cycle","骑行",[116,274,88,28],18,400,False),
        ("type-gym","健身",[213,274,87,28],18,400,False),
        ("type-walk","步行",[309,274,87,28],18,400,False),
        ("type-custom","自定义",[404,274,88,28],18,400,False),
        ("intensity-label","运动强度",[23,316,160,28],18,400,False),
        ("intensity-low","低",[23,353,152,29],18,500,True),
        ("intensity-medium","中",[176,353,157,29],18,400,False),
        ("intensity-high","高",[334,353,154,29],18,400,False),
        ("duration-label","运动时长",[23,405,220,28],18,400,False),
        ("distance-label","运动距离",[268,405,220,28],18,400,False),
        ("duration-value","30分钟",[77,439,158,31],20,400,False),
        ("distance-value","5公里",[320,439,157,31],20,400,False),
        ("steps-label","步数（可选）",[23,486,220,29],18,400,False),
        ("weight-label","体重（用于估算）",[268,486,224,29],18,400,False),
        ("steps-value","6000",[77,521,158,31],20,400,False),
        ("weight-value","69.5 kg",[320,521,157,31],20,400,False),
        ("energy-label","预计消耗",[23,568,161,27],18,400,False),
        ("energy-value","320千卡",[67,594,196,36],24,700,False),
        ("energy-source","估算来源",[394,589,71,27],16,500,False),
        ("formula","基于公式：MET × 体重 × 时间 × 1.05 = 8.0 × 69.5 × 0.5 × 1.05 ≈ 320",[36,641,443,27],13,400,False),
        ("photo-label","照片（最多3张）",[23,684,256,29],18,400,False),
        ("date-label","日期",[23,825,57,30],18,400,False),
        ("date-value","2026年9月26日",[136,825,294,30],18,400,False),
        ("note-label","备注",[23,871,57,30],18,400,False),
        ("note-placeholder","简单记录一下这次运动吧…",[136,873,316,27],17,400,False),
        ("save","保存",[199,925,114,35],23,700,True),
    ],
    "E03": [
        ("time","9:41",[23,3,61,27],17,400,False),
        ("battery","100%",[435,3,65,27],17,400,False),
        ("title","E03 体重记录",[153,43,206,34],24,700,False),
        ("weight-label","体重（kg）",[23,234,245,32],20,400,False),
        ("weight-value","69.5",[175,285,150,48],34,700,False),
        ("ruler-67","67",[32,413,26,28],17,400,False),
        ("ruler-68","68",[117,413,26,28],17,400,False),
        ("ruler-69","69",[202,413,26,28],17,400,False),
        ("ruler-70","70",[288,413,26,28],17,400,False),
        ("ruler-71","71",[374,413,26,28],17,400,False),
        ("ruler-72","72",[459,413,26,28],17,400,False),
        ("ruler-current","69.5",[231,437,89,36],24,700,False),
        ("sleep-label","睡眠时长（小时）",[23,512,318,34],19,400,False),
        ("sleep-value","7.5",[101,558,265,36],25,500,False),
        ("date-label","日期",[23,630,128,32],20,400,False),
        ("date-value","2026年9月26日",[84,674,328,36],21,400,False),
        ("note-label","备注",[23,736,128,33],20,400,False),
        ("note-placeholder","记录一下今天的身体状态吧…",[88,782,366,33],19,400,False),
        ("save","保存",[199,924,114,37],23,700,True),
    ],
    "E04": [
        ("time","9:41",[23,3,61,27],17,400,False),
        ("battery","100%",[435,3,65,27],17,400,False),
        ("title","E04 心情记录",[153,43,206,34],24,700,False),
        ("mood-label","当前心情",[23,102,245,31],18,400,False),
        ("mood-relaxed","轻松",[21,205,111,34],21,400,False),
        ("mood-okay","还行",[141,205,111,34],21,400,False),
        ("mood-irritable","烦躁",[261,205,111,34],21,400,False),
        ("mood-tired","疲惫",[382,205,110,34],21,400,False),
        ("stress-label","压力（1–5）",[23,280,263,34],20,400,False),
        ("stress-1","1",[23,357,28,29],18,400,False),
        ("stress-2","2",[130,357,28,29],18,400,False),
        ("stress-3","3",[246,357,28,29],18,400,False),
        ("stress-4","4",[362,357,28,29],18,400,False),
        ("stress-5","5",[472,357,28,29],18,400,False),
        ("sleep-label","睡眠时长（小时）",[23,417,318,34],19,400,False),
        ("sleep-value","7.5",[101,462,265,36],25,500,False),
        ("date-label","日期",[23,528,128,33],20,400,False),
        ("date-value","2026年9月26日",[84,573,328,35],21,400,False),
        ("note-label","备注",[23,643,128,33],20,400,False),
        ("note-placeholder","记录一下今天的心情吧…",[86,692,368,35],19,400,False),
        ("save","保存",[199,923,114,37],23,700,True),
    ],
}

# id, kind, x/y/w/h, radius estimate, stroke estimate, state
RECTS = {
    "E01": [
        ("exercise-divider-1","line",[24,179,465,1],0,0,""),
        ("exercise-divider-2","line",[24,273,465,1],0,0,""),
        ("exercise-divider-3","line",[24,367,465,1],0,0,""),
        ("weight-divider-1","line",[24,460,465,1],0,0,""),
        ("weight-divider-2","line",[24,556,465,1],0,0,""),
        ("weight-divider-3","line",[24,653,465,1],0,0,""),
        ("mood-divider-1","line",[24,748,465,1],0,0,""),
        ("mood-divider-2","line",[24,843,465,1],0,0,""),
        ("mood-divider-3","line",[24,940,465,1],0,0,""),
        ("gesture","rect",[189,1002,136,6],3,0,""),
    ],
    "E02": [
        ("header-separator","line",[0,85,512,1],0,0,""),
        ("run-card","rect",[20,230,87,74],8,0,"selected"),
        ("cycle-card","rect",[116,230,88,74],8,0,"default"),
        ("gym-card","rect",[213,230,87,74],8,0,"default"),
        ("walk-card","rect",[309,230,87,74],8,0,"default"),
        ("custom-card","rect",[404,230,88,74],8,0,"default"),
        ("intensity-shell","rect",[23,346,465,44],6,1,""),
        ("intensity-selected","rect",[23,346,152,44],6,0,"low"),
        ("intensity-divider","line",[333,346,1,44],0,0,""),
        ("duration-input","rect",[24,434,220,41],6,1,"filled"),
        ("distance-input","rect",[268,434,220,41],6,1,"filled"),
        ("steps-input","rect",[24,516,220,41],6,1,"filled"),
        ("weight-input","rect",[268,516,220,41],6,1,"filled"),
        ("formula-surface","rect",[23,634,465,38],8,0,""),
        ("photo1-frame","rect",[24,715,137,89],7,0,""),
        ("photo2-frame","rect",[178,715,137,89],7,0,""),
        ("photo-add","rect",[332,715,123,89],6,1,"dashed"),
        ("date-input","rect",[82,818,406,41],6,1,"filled"),
        ("note-input","rect",[82,867,406,41],6,1,"empty"),
        ("save","rect",[23,917,465,56],8,0,""),
        ("gesture","rect",[197,1000,118,5],3,0,""),
    ],
    "E03": [
        ("header-separator","line",[0,86,512,1],0,0,""),
        ("weight-input","rect",[24,274,382,69],8,1,"filled"),
        ("keyboard-button","rect",[416,274,73,69],8,1,""),
        ("ruler-active","rect",[254,363,4,71],2,0,"69.5"),
        ("sleep-input","rect",[24,551,465,48],7,1,"filled"),
        ("sleep-icon-cell","rect",[24,551,61,48],7,1,""),
        ("date-input","rect",[24,664,465,49],7,1,"filled"),
        ("note-input","rect",[24,773,465,80],8,1,"empty"),
        ("save","rect",[24,915,465,56],8,0,""),
        ("gesture","rect",[197,1000,119,5],3,0,""),
    ],
    "E04": [
        ("header-separator","line",[0,86,512,1],0,0,""),
        ("relaxed-card","rect",[21,140,111,107],8,1,"selected"),
        ("okay-card","rect",[141,140,111,108],8,1,"default"),
        ("irritable-card","rect",[261,140,111,108],8,1,"default"),
        ("tired-card","rect",[382,140,110,108],8,1,"default"),
        ("stress-track","rect",[28,328,457,10],5,0,""),
        ("stress-selected","rect",[28,328,110,10],5,0,"2"),
        ("stress-thumb","ellipse",[122,317,32,32],16,2,"2"),
        ("sleep-input","rect",[24,455,465,48],7,1,"filled"),
        ("sleep-icon-cell","rect",[24,455,61,48],7,1,""),
        ("date-input","rect",[24,564,465,49],7,1,"filled"),
        ("note-input","rect",[24,681,465,79],8,1,"empty"),
        ("save","rect",[24,914,465,56],8,0,""),
        ("gesture","rect",[197,1000,120,5],3,0,""),
    ],
}

# Crops retain bitmap identity. Artwork/picture pixels are not native vector UI.
# name, source, LTRB, kind, notes
ASSETS = [
    ("back-E01","E01",[25,56,53,87],"icon",""),
    ("status-E01","E01",[351,8,422,31],"icon",""),
    ("history","E01",[400,55,435,89],"icon",""),
    ("add-green","E01",[454,131,486,165],"icon","Reuse for section add controls only after occurrence alignment."),
    ("run-blue","E01",[29,198,64,242],"icon",""),
    ("walk-blue","E01",[29,291,64,337],"icon",""),
    ("weight-scale-green","E01",[27,484,64,524],"icon","Second original occurrence around27,581..620; same master is candidate, not proof pixels identical."),
    ("mood-relaxed-red","E01",[25,772,65,814],"icon",""),
    ("mood-okay-red","E01",[25,868,65,910],"icon",""),
    ("edit-pencil","E01",[459,210,487,239],"icon","Reusable with measured row placement."),
    ("back-editor","E02",[22,46,51,74],"icon",""),
    ("status-editor","E02",[362,4,430,29],"icon","E03/E04 visually similar; compare before master reuse."),
    ("exercise-hero","E02",[0,87,512,194],"photo","Full-width header picture; no interface text inside crop."),
    ("type-run-white","E02",[44,237,85,272],"icon","Selected green matte remains; not transparent."),
    ("type-cycle","E02",[141,238,179,272],"icon",""),
    ("type-gym","E02",[234,242,278,269],"icon",""),
    ("type-walk","E02",[336,238,369,274],"icon",""),
    ("type-custom","E02",[437,247,460,264],"icon",""),
    ("duration-clock","E02",[36,441,63,467],"icon",""),
    ("distance-pin","E02",[281,441,304,468],"icon",""),
    ("steps","E02",[35,524,64,550],"icon",""),
    ("estimate-weight","E02",[279,522,307,551],"icon",""),
    ("energy-flame","E02",[29,598,55,625],"icon",""),
    ("source-chevron","E02",[468,594,487,611],"icon",""),
    ("exercise-photo-1","E02",[24,715,161,804],"photo_with_overlay","Contains close button at136,720..156,742. Needs clean extraction/inpainting before independent editable close control."),
    ("exercise-photo-2","E02",[178,715,315,804],"photo_with_overlay","Contains close button at284,720..308,744. Needs clean extraction/inpainting before independent editable close control."),
    ("photo-remove","E02",[136,720,157,742],"icon","Circle overlays photo; exterior corners require alpha or clean extraction."),
    ("photo-add-plus","E02",[382,747,406,773],"icon","Could be precise native interaction geometry only with explicit source classification."),
    ("calendar-compact","E02",[96,827,118,851],"icon",""),
    ("note-compact","E02",[96,875,118,900],"icon",""),
    ("dropdown-compact","E02",[458,831,475,846],"icon",""),
    ("scale-hero","E03",[0,87,512,197],"photo","Full-width photograph; clean, no UI overlay."),
    ("keyboard","E03",[437,294,472,323],"icon","Native input-button container remains separate."),
    ("sleep-moon","E03",[40,560,70,592],"icon","E04 occurrence at40,464..496; candidate for shared bitmap master."),
    ("calendar","E03",[39,676,65,702],"icon",""),
    ("note","E03",[40,785,66,815],"icon",""),
    ("dropdown","E03",[457,680,475,698],"icon",""),
    ("mood-relaxed-green","E04",[51,152,101,202],"icon","Selected-card pale-green matte; preserve or clean alpha."),
    ("mood-okay-black","E04",[171,152,221,202],"icon",""),
    ("mood-irritable-black","E04",[291,152,341,202],"icon",""),
    ("mood-tired-black","E04",[411,152,462,202],"icon",""),
]


def ink_measure(image, box, light):
    x, y, w, h = box
    area = image.crop((x, y, x+w, y+h)).convert("RGB")
    pixels = list(area.getdata())
    # Preserve pale placeholder glyphs while rejecting white backgrounds.
    mask = Image.new("L", area.size)
    mask.putdata([255 if (min(p)>215 if light else max(p)<200) else 0 for p in pixels])
    bound = mask.getbbox()
    if not bound:
        return None
    return [x+bound[0], y+bound[1], bound[2]-bound[0], bound[3]-bound[1]]


manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
reviews = {p["id"]: p for p in manifest["pages"] if p["id"] in TEXT}
spec = {
    "schemaVersion":"1.0.0",
    "createdAt":datetime.now().astimezone().isoformat(),
    "scope":"source analysis only; no Figma created or modified",
    "coordinateSystem":"Original screen-local pixels,512x1024. Boxes XYWH; crops LTRB exclusive end.",
    "geometryMeaning":"Text x/y/w/h are thresholded visible-ink bounds. textBoxCandidate is inferred editing layout, never an original Figma frame.",
    "fontPolicy":{"actualFamily":unknown("Raster generator did not provide source font metadata"),"candidateFamily":inferred("Noto Sans SC; verify glyph width/weight before accepting")},
    "screens":[],
}
asset_manifest = {"schemaVersion":"1.0.0","scope":"source asset planning only; crop files not generated","assets":[]}
for code, text_rows in TEXT.items():
    source_path = SOURCE / f"{code}.png"
    image = Image.open(source_path).convert("RGB")
    assert image.size == (512,1024)
    entries = []
    for key, content, box, size, weight, light in text_rows:
        ink = ink_measure(image, box, light)
        bx,by,bw,bh=box
        ink_pixels=[p for p in image.crop((bx,by,bx+bw,by+bh)).getdata()
                    if (min(p)>215 if light else max(p)<200)]
        ink_color=[sorted(p[c] for p in ink_pixels)[len(ink_pixels)//2] for c in range(3)] if ink_pixels else None
        align="CENTER" if key in {"title","save"} or key.startswith(("type-","intensity-","mood-")) and not key.endswith(("label","value","date")) else "LEFT"
        if key in {"intensity-label","type-label","mood-label","mood-heading"}:
            align="LEFT"
        entries.append({
            "id":key,"text":measured(content,"Original screenshot manual transcription"),
            "x":ink[0] if ink else None,"y":ink[1] if ink else None,
            "w":ink[2] if ink else None,"h":ink[3] if ink else None,
            "geometryStatus":"measured" if ink else "unknown",
            "inkMedianRGB":ink_color,
            "geometrySource":"Pixel threshold within stated candidate box; border contamination possible; visible glyph extent not font baseline.",
            "textBoxCandidate":inferred(box),
            "fontSizeCandidate":inferred(size),
            "fontWeightCandidate":inferred(weight),
            "lineHeightCandidate":inferred(round(size*1.4,1)),
            "letterSpacingCandidate":inferred(0),
            "textAlignCandidate":inferred(align),
            "colorRole":inferred("white" if light else ("secondary" if any(part in key for part in ["date","placeholder","formula","ruler-"]) else "primary")),
        })
    color_rois = {
        "background":[310,950,345,980] if code=="E01" else [320,983,360,996],
        "primary_ink":[205,59,227,79] if code=="E01" else [194,52,210,68],
        "field_border":[26,551,60,553] if code=="E03" else ([26,455,60,457] if code=="E04" else [25,435,65,437]),
        "accent":[460,144,480,151] if code=="E01" else ([35,924,110,955] if code=="E02" else [35,923,110,950]),
    }
    colors = {}
    for role, roi in color_rois.items():
        if code=="E01" and role=="field_border":
            continue
        s=ImageStat.Stat(image.crop(roi))
        colors[role]={"roiLTRB":measured(roi,"sampling coordinates"),"meanRGB":measured([round(v,2) for v in s.mean],"Pillow source ROI mean, mixed edge pixels may occur"),"stddevRGB":measured([round(v,2) for v in s.stddev],"Pillow source ROI stddev")}
        pixels=list(image.crop(roi).getdata())
        if role=="accent":
            pixels=[p for p in pixels if p[1]-p[0]>35 and p[1]-p[2]>8]
        elif role=="primary_ink":
            pixels=[p for p in pixels if max(p)<130]
        if pixels:
            colors[role]["filteredMedianRGB"]=measured(
                [sorted(p[channel] for p in pixels)[len(pixels)//2] for channel in range(3)],
                "Per-channel source median; accent filters green, primary filters dark ink; other roles unfiltered")
    screen={
        "id":code,"title":measured({"E01":"健康记录","E02":"E02 运动记录","E03":"E03 体重记录","E04":"E04 心情记录"}[code],"original text"),
        "sourceFile":str(source_path),"sourceSHA256":sha256(source_path.read_bytes()).hexdigest(),
        "width":512,"height":1024,"dimensionStatus":"measured",
        "background":colors["background"],"colors":colors,
        "text":entries,
        "controls":[{"id":name,"type":kind,"x":box[0],"y":box[1],"w":box[2],"h":box[3],"geometryStatus":"measured","geometrySource":"Manual source-pixel visible-edge measurement ±2px","radiusCandidate":inferred(radius),"strokeCandidate":inferred(stroke),"visibleState":inferred(state)} for name,kind,box,radius,stroke,state in RECTS[code]],
        "assets":[name for name,src,*_ in ASSETS if src==code],
        "reviewNotes":measured(reviews[code]["reviewNotes"],"manifest.json"),
        "dataBoundary":measured(reviews[code]["dataBoundary"],"manifest.json"),
        "trueDeviceSafeInset":unknown("These are concept images, not device metadata."),
    }
    if code=="E01":
        screen["listRows"]=measured([
            {"section":"运动","rows":[[24,180,465,93],[24,274,465,93]],"iconX":29,"textX":88,"editX":459},
            {"section":"体重","rows":[[24,461,465,95],[24,557,465,96]],"iconX":27,"textX":88,"editX":459},
            {"section":"心情","rows":[[24,749,465,94],[24,844,465,96]],"iconX":25,"textX":88,"editX":459},
        ])
        screen["repeatedControls"]=inferred({"addXY":[[454,131],[454,412],[454,700]],"editXY":[[459,210],[459,306],[459,492],[459,588],[459,779],[459,875]],"reuse":"one add master and one edit master; icon artwork remains bitmap"})
    if code=="E02":
        screen["formulaPolicy"]=measured("原图文字只用于视觉溯源；manifest明确指出公式与320示例不一致，实装须由现有计算逻辑驱动。","manifest reviewNotes")
        screen["photoLayering"]=inferred("Two photos include baked close circles. Clean image content first, then separate close control; do not claim independent photo/control if overlay remains inside image.")
    if code=="E03":
        screen["ruler"]= {
            "majorTickX":measured([42,127,212,300,385,471]),
            "majorTickYH":measured([370,37]),
            "minorTickYH":measured([370,13]),
            "mediumTickYH":measured([370,21]),
            "minorSpacingCandidate":inferred(8.55),
            "rangeLabels":measured([67,68,69,70,71,72],"source text"),
            "selected":measured(69.5,"source text"),
            "selectedLineXYWH":measured([254,363,4,71]),
            "type":inferred("native editable tick marks and value text; keyboard entry must remain"),
        }
    if code=="E04":
        screen["stressSlider"]={
            "tickX":measured([32,138,255,371,481]),
            "tickYH":measured([343,10]),
            "selectedValue":measured(2,"source thumb aligned to2"),
            "trackXYWH":measured([28,328,457,10]),
            "thumbXYWH":measured([122,317,32,32]),
            "nativeStructure":inferred(True),
        }
    spec["screens"].append(screen)

for name, code, crop, kind, note in ASSETS:
    file=SOURCE/f"{code}.png"
    image=Image.open(file).convert("RGB").crop(crop)
    asset_manifest["assets"].append({
        "id":name,"sourceScreen":code,"sourceFile":str(file),
        "sourceSHA256":sha256(file.read_bytes()).hexdigest(),
        "cropLTRB":measured(crop,"Native source-pixel crop plan; endpoints exclusive, margin tolerance±2px"),
        "pixelSize":measured([crop[2]-crop[0],crop[3]-crop[1]],"crop arithmetic"),
        "plannedFile":str(ROOT/"assets"/f"{name}.png"),
        "fileCreated":False,
        "classification":measured(kind,"visible original pixels"),
        "sourcePixelSHA256":measured(sha256(image.tobytes()).hexdigest(),"RGB decoded pixels of proposed crop, not encoded-PNG file hash"),
        "vector":False,
        "alpha":unknown("Source is flattened; clean transparency must be extracted, not assumed."),
        "status":inferred("needs_clean_extraction" if kind=="photo_with_overlay" or "alpha" in note or "matte" in note else "ready_for_exact_crop"),
        "notes":note,
        "componentRule":inferred("Independent bitmap asset master; reuse instances at native pixel size inside fixed shell. Do not scale all icons to one filled slot."),
    })
asset_manifest["sharedMasterCandidates"]=inferred({
    "all":["back-editor","status-editor","sleep-moon","calendar","note","dropdown"],
    "E01":["add-green","edit-pencil","weight-scale-green"],
    "notInterchangeable":["mood-relaxed-red vs mood-relaxed-green","type-run-white vs run-blue"],
})
# Keep the delivery compact: shared provenance rules replace repeated prose.
spec["fieldStatusRules"]={
    "text":{"measured":["text","x","y","w","h","inkMedianRGB"],"inferred":["textBoxCandidate","fontSizeCandidate","fontWeightCandidate","lineHeightCandidate","letterSpacingCandidate","textAlignCandidate","colorRole"]},
    "controls":{"measured":["x","y","w","h"],"inferred":["radiusCandidate","strokeCandidate","visibleState"]},
    "source":"All measured values come from the source screen named by page. Text ink uses threshold in candidate box; geometry tolerance1-2px. Unknown metadata stays explicitly unknown.",
}
for screen in spec["screens"]:
    for text in screen["text"]:
        text["text"]=text["text"]["value"]
        for key in ["textBoxCandidate","fontSizeCandidate","fontWeightCandidate","lineHeightCandidate","letterSpacingCandidate","textAlignCandidate","colorRole"]:
            text[key]=text[key]["value"]
        text.pop("geometrySource")
    for control in screen["controls"]:
        control.pop("geometrySource")
        for key in ["radiusCandidate","strokeCandidate","visibleState"]:
            control[key]=control[key]["value"]
asset_manifest["sources"]={
    s["id"]:{"path":s["sourceFile"],"sha256":s["sourceSHA256"],"status":"measured"}
    for s in spec["screens"]
}
asset_manifest["fieldStatusRules"]={
    "measured":["sourceScreen","cropLTRB","pixelSize","classification","sourcePixelSHA256","vector","fileCreated"],
    "inferred":["plannedFile","status","componentRule"],
    "unknown":["alpha"],
    "source":"sourceScreen resolves through sources; crop edges are source-native pixels with margin tolerance2px.",
}
asset_manifest["componentRule"]=inferred("Independent bitmap asset master; reuse instances at native pixel size inside fixed shell. Do not scale all icons to one filled slot.")
for asset in asset_manifest["assets"]:
    for key in ["sourceFile","sourceSHA256","componentRule"]:
        asset.pop(key)
    for key in ["cropLTRB","pixelSize","classification","sourcePixelSHA256","status"]:
        asset[key]=asset[key]["value"]
for name,payload in [("source-spec.json",spec),("asset-manifest.json",asset_manifest)]:
    destination=ROOT/name
    destination.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    json.loads(destination.read_text(encoding="utf-8"))
    print(name,destination.stat().st_size)
print("screens",len(spec["screens"]),"text",sum(len(s["text"]) for s in spec["screens"]),"assets",len(asset_manifest["assets"]))
