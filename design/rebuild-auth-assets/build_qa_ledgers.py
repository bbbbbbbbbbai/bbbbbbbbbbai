from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).parent
SOURCE = ROOT.parent / "screens"
NOW = datetime.now().astimezone().isoformat()
FILE_KEY = "ptA7IsUhV0rHsp8yRLFRVj"
PAGE_ID = "70:13"
PAGE_NAME = "12 原图重建｜注册与密码"
READBACK = "2026-09-28 Figma use_figma read-only query, page 70:13"


def evidence(value, status, origin, **extra):
    assert status in {"measured", "inferred", "unknown"}
    return {"value": value, "status": status, "evidence": origin, **extra}


def m(value, origin=READBACK, **extra):
    return evidence(value, "measured", origin, **extra)


def i(value, origin="QA proposal; source screenshot remains authoritative", **extra):
    return evidence(value, "inferred", origin, **extra)


def u(reason):
    return evidence(None, "unknown", reason)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def base(kind):
    return {
        "schemaVersion": "1.0.0",
        "artifactType": kind,
        "evidenceSchema": {
            "description": "Every domain field uses value/status/evidence. Schema metadata is authored, not observed.",
            "statuses": ["measured", "inferred", "unknown"],
        },
        "createdAt": m(NOW, "local system clock"),
        "scope": m(["A02", "A03", "A04", "A05"], "assigned QA scope"),
        "sourceOfTruth": m("original screens/A02.png through A05.png", "parent instruction"),
        "deliveryState": i("in_progress_not_accepted"),
        "figmaIdentity": {
            "fileKey": m(FILE_KEY),
            "apiDocumentName": m("Document"),
            "pageId": m(PAGE_ID),
            "pageName": m(PAGE_NAME),
            "writePolicy": m("Read-only QA; no Figma writes performed in this audit", "task scope and tool log"),
        },
    }


SCREEN = {
    "A02": {
        "node": "70:14", "ref": "70:15", "texts": 17,
        "referenceHash": "43e750caba20cf18ed1f72f8605f6c7d2d59f235",
        "photo": ("70:36", [23, 161, 490, 309], "dfca73ed600083c5bbeb6a1076a34245af48f047"),
        "regions": [
            ("status", [0, 0, 512, 35], ["70:460", "70:486", "70:491"]),
            ("identity", [17, 43, 460, 149], ["70:461", "70:140", "70:141"]),
            ("photo", [23, 161, 490, 309], ["70:36"]),
            ("heading", [35, 330, 478, 411], ["70:142", "70:143"]),
            ("email", [35, 432, 478, 523], ["70:144", "70:205", "70:639"]),
            ("password", [35, 542, 478, 632], ["70:145", "70:207", "70:647", "70:671"]),
            ("confirmation", [35, 653, 478, 744], ["70:146", "70:209", "70:651", "70:675"]),
            ("password_help", [35, 750, 478, 780], ["70:147"]),
            ("submit", [34, 803, 479, 867], ["70:445", "70:446"]),
            ("login_footer", [35, 886, 478, 961], ["70:148", "70:149", "70:730", "70:731"]),
            ("gesture", [191, 1001, 322, 1008], ["70:732"]),
        ],
        "fields": [("70:205", [35, 465, 443, 58]), ("70:207", [35, 574, 443, 58]), ("70:209", [35, 686, 443, 58])],
        "button": ("70:445", [34, 803, 445, 64]),
    },
    "A03": {
        "node": "70:16", "ref": "70:17", "texts": 15,
        "referenceHash": "bf92f6adfd4662cb8f8331b2ffe0fefe9cb91792",
        "photo": None,
        "regions": [
            ("status", [0, 0, 512, 35], ["70:462", "70:492", "70:497"]),
            ("back", [32, 81, 54, 115], ["70:498"]),
            ("mail_art", [204, 174, 309, 285], ["70:719"]),
            ("verification_heading", [30, 315, 482, 443], ["70:150", "70:151", "70:152"]),
            ("otp", [38, 481, 474, 559], ["70:334"]),
            ("submit", [31, 601, 481, 668], ["70:447", "70:448"]),
            ("resend_countdown", [60, 687, 452, 719], ["70:153"]),
            ("change_email", [60, 765, 452, 797], ["70:154"]),
            ("gesture", [191, 1001, 322, 1008], ["70:733"]),
        ],
        "fields": [],
        "button": ("70:447", [31, 601, 450, 67]),
    },
    "A04": {
        "node": "70:18", "ref": "70:19", "texts": 11,
        "referenceHash": "f6ea01b3b061fee63c53f14808193518d1e0fa69",
        "photo": ("70:37", [29, 229, 484, 349], "ff85aefbf8e5bbb176f4318aead432467e1ec547"),
        "regions": [
            ("status_and_brand", [0, 0, 512, 73], ["70:155", "70:464", "70:465", "70:500"]),
            ("back", [31, 81, 50, 107], ["70:505"]),
            ("heading", [37, 129, 483, 213], ["70:156", "70:157"]),
            ("photo", [29, 229, 484, 349], ["70:37"]),
            ("email", [31, 396, 481, 496], ["70:158", "70:296", "70:643"]),
            ("submit", [31, 533, 481, 600], ["70:449", "70:450"]),
            ("return_login", [32, 626, 480, 658], ["70:159"]),
            ("mail_hint", [32, 719, 480, 824], ["70:725", "70:160", "70:161"]),
        ],
        "fields": [("70:296", [32, 431, 448, 64])],
        "button": ("70:449", [32, 533, 448, 66]),
    },
    "A05": {
        "node": "70:20", "ref": "70:21", "texts": 18,
        "referenceHash": "f7b6013480f240c9d6feba83b8844bbeb9abab6b",
        "photo": ("70:38", [29, 229, 484, 372], "3f5f38fd47fb8d1d06050cb62dfacf483ab80ce1"),
        "regions": [
            ("status_and_brand", [0, 0, 512, 73], ["70:162", "70:466", "70:467", "70:507"]),
            ("back", [31, 81, 50, 106], ["70:512"]),
            ("heading", [37, 129, 483, 213], ["70:163", "70:164"]),
            ("photo", [29, 229, 484, 372], ["70:38"]),
            ("destination_email", [37, 386, 470, 414], ["70:165", "70:166"]),
            ("otp_field", [32, 430, 481, 520], ["70:167", "70:298", "70:368", "70:687"]),
            ("new_password", [32, 539, 481, 655], ["70:168", "70:300", "70:169", "70:655", "70:679"]),
            ("confirmation", [32, 681, 481, 806], ["70:170", "70:302", "70:369", "70:659", "70:683", "70:691"]),
            ("submit", [32, 842, 481, 908], ["70:451", "70:452"]),
            ("return_login", [32, 934, 480, 966], ["70:171"]),
        ],
        "fields": [("70:298", [32, 462, 448, 57]), ("70:300", [32, 570, 448, 57]), ("70:302", [32, 715, 448, 57])],
        "button": ("70:451", [32, 843, 448, 64]),
    },
}

# Current editable text geometry is read back from Figma, not used as a claim
# about original screenshot text boxes. Source glyph bounds are measured below.
TEXT = {
    "A02": [
        ("70:140", "老白の日记", [100, 77, 312, 48], 32, 48, "Bold", [165, 80, 348, 119]),
        ("70:141", "记录生活　细水长流", [90, 122, 332, 27], 18, 27, "Regular", [165, 123, 348, 149]),
        ("70:142", "注册账号", [35, 330, 440, 48], 32, 48, "Bold", [30, 333, 182, 376]),
        ("70:143", "开启你的记录之旅", [35, 379, 440, 31.5], 21, 31.5, "Medium", [30, 380, 260, 410]),
        ("70:144", "邮箱", [35, 432, 440, 27], 18, 27, "Regular", [31, 434, 88, 460]),
        ("70:145", "密码", [35, 542, 440, 27], 18, 27, "Regular", [31, 544, 89, 570]),
        ("70:146", "确认密码", [35, 653, 440, 27], 18, 27, "Regular", [31, 654, 126, 681]),
        ("70:147", "密码需至少 8 位，包含字母和数字", [35, 750, 440, 25.5], 17, 25.5, "Regular", [31, 752, 321, 777]),
        ("70:148", "已有账号？", [196, 886, 120, 27], 18, 27, "Medium", [200, 886, 310, 917]),
        ("70:149", "登录", [196, 925, 120, 31.5], 21, 31.5, "Medium", [222, 925, 290, 957]),
        ("70:206", "请输入邮箱地址", [101, 479, 140, 30], 20, 30, "Regular", [98, 480, 250, 511]),
        ("70:208", "• • • • • • • •", [101, 588, 102, 30], 22, 30, "Roboto/Bold", [98, 593, 207, 615]),
        ("70:210", "• • • • • • • •", [101, 700, 102, 30], 22, 30, "Roboto/Bold", [98, 705, 207, 727]),
        ("70:446", "注册", [231.5, 818, 50, 34], 25, 34, "Medium", [220, 815, 294, 855]),
        ("70:460", "9:41", [17, 6, 35, 27], 18, 27, "Regular", [12, 5, 60, 32]),
        ("70:461", "A02", [17, 41, 31, 27], 18, 27, "Regular", [12, 40, 58, 68]),
        ("70:491", "100%", [430, 6, 47, 27], 18, 27, "Regular", [426, 5, 487, 32]),
    ],
    "A03": [
        ("70:150", "验证邮箱", [60, 315, 392, 45], 32, 45, "Bold", [182, 318, 334, 362]),
        ("70:151", "我们已向以下邮箱发送了验证码", [30, 370, 452, 31.5], 20, 31.5, "Medium", [100, 372, 414, 403]),
        ("70:152", "b***@example.com", [30, 409, 452, 33], 21, 33, "Medium", [140, 410, 375, 444]),
        ("70:153", "48秒后重新发送", [60, 687, 392, 30], 20, 30, "Medium", [171, 688, 344, 720]),
        ("70:154", "更换邮箱", [60, 765, 392, 30], 20, 30, "Medium", [207, 766, 307, 800]),
        ("70:448", "验证并继续", [198.5, 617.5, 115, 34], 23, 34, "Medium", [184, 614, 329, 657]),
        ("70:462", "9:41", [17, 6, 35, 27], 18, 27, "Regular", [12, 5, 60, 32]),
        ("70:463", "A03", [17, 41, 31, 27], 18, 27, "Regular", [12, 40, 58, 68]),
        ("70:497", "100%", [430, 6, 47, 27], 18, 27, "Regular", [426, 5, 487, 32]),
    ],
    "A04": [
        ("70:155", "老白の日记", [120, 36, 272, 36], 23, 36, "Bold", [183, 36, 330, 72]),
        ("70:156", "找回密码", [37, 129, 440, 54], 38, 54, "Bold", [31, 132, 210, 179]),
        ("70:157", "输入注册邮箱，系统将发送验证码至你的邮箱。", [37, 183, 445, 28.5], 19, 28.5, "Regular", [31, 183, 472, 214]),
        ("70:158", "邮箱地址", [37, 396, 440, 27], 18, 27, "Medium", [31, 396, 126, 425]),
        ("70:159", "返回登录", [32, 626, 448, 30], 20, 30, "Medium", [205, 626, 311, 662]),
        ("70:160", "验证码将发送至你的注册邮箱", [32, 767, 448, 27], 17, 27, "Regular", [128, 767, 388, 796]),
        ("70:161", "请检查垃圾邮件文件夹，以免遗漏。", [32, 797, 448, 24], 16, 24, "Regular", [120, 798, 399, 824]),
        ("70:297", "请输入注册邮箱", [98, 448.5, 133, 29], 19, 29, "Regular", [89, 449, 257, 482]),
        ("70:450", "发送验证码", [201, 549, 110, 34], 22, 34, "Bold", [188, 548, 329, 590]),
        ("70:464", "9:41", [27, 6, 32, 27], 16, 27, "Regular", [21, 5, 65, 31]),
        ("70:465", "A04", [27, 41, 28, 27], 16, 27, "Regular", [21, 40, 64, 68]),
    ],
    "A05": [
        ("70:162", "老白の日记", [120, 36, 272, 36], 23, 36, "Bold", [183, 36, 330, 72]),
        ("70:163", "设置新密码", [37, 129, 440, 54], 38, 54, "Bold", [31, 132, 247, 179]),
        ("70:164", "请输入邮箱验证码，并设置新的登录密码。", [37, 183, 445, 28.5], 19, 28.5, "Regular", [31, 183, 472, 214]),
        ("70:165", "验证码将发送至", [37, 386, 116, 24], 16, 24, "Regular", [32, 386, 148, 416]),
        ("70:166", "b***@example.com", [152, 386, 310, 27], 17, 27, "Medium", [151, 386, 330, 416]),
        ("70:167", "邮箱验证码", [35, 430, 440, 27], 18, 27, "Medium", [30, 430, 144, 460]),
        ("70:168", "新密码", [35, 539, 440, 27], 18, 27, "Medium", [30, 539, 107, 568]),
        ("70:169", "至少8位，建议包含字母、数字和符号", [35, 631, 440, 24], 16, 24, "Regular", [30, 631, 338, 658]),
        ("70:170", "确认新密码", [35, 681, 440, 27], 18, 27, "Medium", [30, 681, 151, 711]),
        ("70:171", "返回登录", [32, 934, 448, 30], 20, 30, "Medium", [205, 934, 311, 968]),
        ("70:299", "请输入6位验证码", [91, 476, 144, 29], 19, 29, "Regular", [86, 476, 250, 509]),
        ("70:301", "请输入新密码", [91, 584, 114, 29], 19, 29, "Regular", [86, 584, 223, 617]),
        ("70:303", "请再次输入新密码", [91, 729, 152, 29], 19, 29, "Regular", [86, 729, 258, 764]),
        ("70:368", "重新发送", [394, 477, 72, 27], 18, 27, "Regular", [387, 476, 472, 510]),
        ("70:369", "两次密码一致", [69, 778, 102, 27], 17, 27, "Regular", [64, 778, 184, 808]),
        ("70:452", "确认修改密码", [190, 858, 132, 34], 22, 34, "Bold", [177, 854, 337, 897]),
        ("70:466", "9:41", [27, 6, 32, 27], 16, 27, "Regular", [21, 5, 65, 31]),
        ("70:467", "A05", [27, 41, 28, 27], 16, 27, "Regular", [21, 40, 64, 68]),
    ],
}

for index, node in enumerate(["70:336", "70:338", "70:340", "70:342", "70:365", "70:367"]):
    x = 39 + 74 * index
    TEXT["A03"].append((node, "—", [x + 21, 504, 21, 32], 23, 32, "Regular", [x + 15, 510, x + 48, 533]))


def ink_bbox(image, roi, light=False):
    part = image.crop(roi).convert("RGB")
    values = list(part.getdata())
    if light:
        binary = [255 if min(p) > 210 else 0 for p in values]
    else:
        binary = [255 if max(p) < 200 else 0 for p in values]
    mask = Image.new("L", part.size)
    mask.putdata(binary)
    box = mask.getbbox()
    return [box[0] + roi[0], box[1] + roi[1], box[2] + roi[0], box[3] + roi[1]] if box else None


layout = base("layout")
layout["coordinateSystem"] = m(
    {"origin": "screen top-left", "unit": "source pixel", "scale": 1, "rectFormat": "xywh unless name ends LTRB"},
    "PNG header and declared audit convention",
)
layout["uncertainties"] = [
    u("Original raster generator font family, font file and typography metadata are not supplied."),
    u("Real Android density, navigation inset, keyboard behavior and touch target bounds cannot be recovered from concept PNG."),
    u("Original editable text frame geometry, ascent/descent and baseline are not present in raster."),
    i("Manual region ROIs are semantic inspection windows, not exact original layer bounds; tolerance typically 1-3 px."),
]
layout["screens"] = []
assets = base("asset-manifest")
assets["assets"] = []
qa = base("qa-diff")
qa["round"] = m("Read-only post-build audit of existing local exports", "task scope")
qa["metricsWarning"] = i("Whole-image MAE is dominated by blank backgrounds and cannot establish visual acceptance.")
qa["screens"] = []

for code, record in SCREEN.items():
    original_path = SOURCE / f"{code}.png"
    current_path = ROOT / f"{code}-editable.png"
    original = Image.open(original_path).convert("RGB")
    current = Image.open(current_path).convert("RGB")
    assert original.size == current.size == (512, 1024)
    text_records = []
    text_diffs = []
    for node, text, box, size, line, style, roi in TEXT[code]:
        light = node in {"70:446", "70:448", "70:450", "70:452"}
        source_ink = ink_bbox(original, roi, light)
        current_ink = ink_bbox(current, roi, light)
        family = "Roboto" if style.startswith("Roboto/") else "Noto Sans SC"
        actual_style = style.split("/")[-1]
        text_records.append({
            "nodeId": m(node), "content": m(text, "Figma readback; visually compared to original"),
            "currentTextBoxXYWH": m(box, READBACK + "; child coordinates converted to screen-local"),
            "sourceInspectionRoiLTRB": i(roi, "manual same-size image inspection"),
            "sourceVisibleInkBBoxLTRB": m(source_ink, "original PNG threshold within ROI; not a text-frame or baseline", threshold="minRGB>210 for button text; maxRGB<200 otherwise"),
            "originalFont": u("No reliable source font metadata"),
            "currentFont": m({"family": family, "style": actual_style, "size": size, "lineHeightPx": line}),
            "fallbackStatus": m("explicit approximation, not verified original font", "construction log"),
            "originalTextFrame": u("Raster only; retain current box as implementation data, not source evidence"),
            "originalBaseline": u("Visible glyph bottom is not a font baseline"),
            "wrapping": m("single line", "source and current image visual inspection"),
            "direction": m("LTR with Chinese horizontal text", "visible text"),
        })
        if source_ink and current_ink:
            delta = [current_ink[n] - source_ink[n] for n in range(4)]
            text_diffs.append({
                "nodeId": m(node), "content": m(text, "visible text"),
                "originalInkBBoxLTRB": m(source_ink, "original PNG ROI threshold"),
                "currentInkBBoxLTRB": m(current_ink, "current PNG ROI threshold"),
                "edgeDeltaLTRB": m(delta, "current minus original; sensitive to antialiasing"),
            })
    colors = {}
    for name, roi in {
        "background_top": [90, 5, 300, 30],
        "background_bottom": [40, 970, 160, 994],
        "primary_button_interior": [
            record["button"][1][0] + 12, record["button"][1][1] + 12,
            record["button"][1][0] + 140, record["button"][1][1] + record["button"][1][3] - 12,
        ],
    }.items():
        stat = ImageStat.Stat(original.crop(roi))
        newstat = ImageStat.Stat(current.crop(roi))
        colors[name] = {
            "sourceRoiLTRB": m(roi, "pixel sampling coordinates"),
            "sourceMeanRGB": m([round(v, 3) for v in stat.mean], "Pillow ImageStat over source ROI"),
            "sourceStddevRGB": m([round(v, 3) for v in stat.stddev], "Pillow ImageStat over source ROI"),
            "currentMeanRGB": m([round(v, 3) for v in newstat.mean], "Pillow ImageStat over current ROI"),
            "currentStddevRGB": m([round(v, 3) for v in newstat.stddev], "Pillow ImageStat over current ROI"),
            "interpretation": i("Source variation may mix generated texture, antialiasing and compression; no assumed physical material."),
        }
    layout["screens"].append({
        "screen": m(code, "manifest.json"), "nodeId": m(record["node"]),
        "source": m(str(original_path), "filesystem"),
        "sourceSHA256": m(digest(original_path), "SHA-256 of original file bytes"),
        "viewport": m([512, 1024], "PNG IHDR"),
        "visibleTopStatusBandLTRB": i([0, 0, 512, 35], "visible status symbols"),
        "bottomSafeArea": i([0, 982, 512, 1024] if code in {"A02", "A03"} else None, "Gesture bar visible only in A02/A03; absence in A04/A05 is not zero device inset"),
        "scrollBehavior": u("Single screenshot cannot establish scrolling or fixed positioning"),
        "regions": [{
            "name": i(name), "sourceInspectionRoiLTRB": i(bounds, "manual semantic ROI from source"),
            "currentNodeIds": m(ids),
            "sourceLayerBounds": u("Semantic ROI differs from unavailable original editable layer bounds"),
        } for name, bounds, ids in record["regions"]],
        "currentFieldGeometry": [{
            "nodeId": m(node), "boundsXYWH": m(box), "cornerRadius": m(8, "construction log"),
            "strokeWidth": m(1, "construction log"), "layout": m("HORIZONTAL"),
            "sourceRadiusPx": i(8, "source visual estimate", tolerancePx=2),
            "sourceStrokePx": i(1, "source edge inspection", tolerancePx=1),
        } for node, box in record["fields"]],
        "currentPrimaryButton": {"nodeId": m(record["button"][0]), "boundsXYWH": m(record["button"][1])},
        "text": text_records,
        "colors": colors,
        "materials": [
            m("Source background is not perfectly uniform", "sample standard deviation and visual comparison"),
            m("Source primary button has visible low-frequency mottling; current is flat", "source/current button ROI comparison"),
            u("Exact source gradient/noise/effect parameters"),
        ],
        "states": i(
            {"A02": "email empty; password and confirmation masked",
             "A03": "six empty OTP cells; resend countdown 48 seconds",
             "A04": "email empty; send-code default action",
             "A05": "empty OTP/password fields but success consistency hint visible"}[code],
            "visible source screenshot; not implementation behavior",
        ),
    })
    diff = ImageChops.difference(original, current)
    mae = sum(ImageStat.Stat(diff).mean) / 3
    qa["screens"].append({
        "screen": m(code, "manifest"), "nodeId": m(record["node"]),
        "referenceId": m(record["ref"]),
        "screenshot": m(str(current_path), "filesystem"),
        "screenshotSHA256": m(digest(current_path), "file bytes SHA-256"),
        "sourceSHA256": m(digest(original_path), "file bytes SHA-256"),
        "comparison": m(str(ROOT / f"{code}-comparison.png"), "filesystem; left original/right current"),
        "sameSize": m(True, "Pillow size check 512x1024"),
        "wholeImageMAE": m(round(mae, 4), "mean absolute RGB channel error on all pixels, 0-255"),
        "components": m(0), "instances": m(0), "editableTextNodes": m(record["texts"]),
        "textInkComparisons": text_diffs,
        "acceptance": i("FAIL: structural and visual gates remain open"),
    })
    assets["assets"].append({
        "assetId": i(f"{code}-reference"),
        "kind": m("full_reference_only", "actual locked rectangle"),
        "sourceFile": m(str(original_path), "filesystem"),
        "sourceSHA256": m(digest(original_path), "file bytes SHA-256"),
        "pixelSize": m([512, 1024], "PNG IHDR"),
        "nodeId": m(record["ref"]),
        "imageHash": m(record["referenceHash"], "upload_assets POST response and Figma fill readback"),
        "scope": m("outside editable screen, locked reference", READBACK),
        "deliveryScreenUsage": m(False, "screen subtree image-fill readback"),
        "mayBeUsedAsUIBackground": i(False, "anti-raster-disguise rule"),
    })
    if record["photo"]:
        node, crop, image_hash = record["photo"]
        path = ROOT / f"{code}-photo.png"
        photo = Image.open(path)
        exact_crop = ImageChops.difference(original.crop(crop), photo.convert("RGB")).getbbox() is None
        assets["assets"].append({
            "assetId": i(f"{code}-photo"),
            "kind": m("raster_photo_cropped_from_original", "crop_auth_references.py"),
            "sourceFile": m(str(original_path), "filesystem"),
            "sourceSHA256": m(digest(original_path), "file bytes SHA-256"),
            "assetFile": m(str(path), "filesystem"),
            "assetSHA256": m(digest(path), "file bytes SHA-256"),
            "cropLTRB": m(crop, "executed Pillow crop script; exclusive right/bottom"),
            "pixelSize": m(list(photo.size), "PNG IHDR"),
            "mode": m(photo.mode, "Pillow"),
            "hasAlpha": m("A" in photo.getbands(), "Pillow image bands"),
            "pixelExactToDeclaredSourceCrop": m(exact_crop, "Pillow ImageChops comparison"),
            "nodeId": m(node), "imageHash": m(image_hash, "official upload_assets POST response and Figma IMAGE fill readback"),
            "fillMode": m("FILL"), "imageTransform": m([[1, 0, 0], [0, 1, 0]]),
            "componentMaster": u("Absent: standalone rectangle with image fill"),
            "instanceId": u("Absent: no material component instance"),
            "imageTwoPipeline": m("clean extraction via Pillow; no image model called", "execution log"),
            "edgeRisk": i("Cropped rounded photo contains original background pixels in corners; preserve matching clipping and do not add opaque corner artifact."),
            "printedTextPolicy": i("Notebook/cup lettering is part of the photographic source, not editable interface copy."),
        })

ART = [
    ("A03-mail-art", "A03", [204, 174, 309, 285], ["70:719"], "mail illustration"),
    ("A04-mail-hint-art", "A04", [229, 719, 286, 750], ["70:725"], "mail illustration with motion marks"),
    ("status-icons-A02-A03", None, None, ["70:486", "70:492"], "status icon artwork"),
    ("status-icons-A04-A05", None, None, ["70:500", "70:507"], "status icon artwork"),
    ("back-icons", None, None, ["70:498", "70:505", "70:512"], "precise UI navigation vector"),
    ("mail-icons", None, None, ["70:639", "70:643"], "mail field icon"),
    ("lock-icons", None, None, ["70:647", "70:651", "70:655", "70:659"], "password lock icon"),
    ("eye-icons", None, None, ["70:671", "70:675", "70:679", "70:683"], "password visibility icon"),
    ("A05-shield", "A05", [50, 480, 73, 503], ["70:687"], "verification shield icon"),
    ("A05-match-check", "A05", [35, 781, 56, 802], ["70:691"], "consistency check icon"),
]
for name, screen, crop, nodes, kind in ART:
    assets["assets"].append({
        "assetId": i(name), "kind": m(kind, "visible original and current layers"),
        "sourceScreen": m(screen, "assigned source") if screen else i("multiple listed screens"),
        "sourceInspectionRoiLTRB": i(crop, "manual source ROI") if crop else u("Per-variant source bounding boxes require extraction pass"),
        "currentNodeIds": m(nodes),
        "currentRepresentation": m("manually authored SVG imported as editable vector subtree", "construction log"),
        "nativeSourceAsset": u("Original SVG/source illustration file not supplied"),
        "assetSHA256": u("No local SVG asset was saved"),
        "imageHash": m(None, "vector node, not raster fill"),
        "imageTwoPipeline": m("not performed", "execution log"),
        "pipelineException": u("No explicit image-model-unavailable or failed-generation exception recorded"),
        "componentMaster": u("No master/instance relationship"),
        "remediation": i("Artwork: clean extraction/Image Two asset with provenance, then asset component. Precise control geometry may remain editable vector after explicit classification."),
    })
assets["missingMaterials"] = [{
    "material": i("background subtle texture / primary button mottling"),
    "screens": m(list(SCREEN), "visual comparison"),
    "current": m("flat solid fills", "construction log and screenshot variance"),
    "sourceParameters": u("Original material generator parameters are unavailable"),
    "nextStep": i("Measure variation in empty source patches, then extract or generate only material layer without text or control edges; parent orchestrator decides acceptance."),
}]

components = base("component-plan")
components["currentState"] = {
    "componentsOnTargetPage": m(0), "instancesInScreens": m(0),
    "masterPageId": u("No source-rebuild component library created"),
    "requiredLibraryLocation": i("02｜组件库与素材", "skill recommendation; parent orchestrator must resolve coexistence with existing pages"),
    "screenLocation": m(PAGE_NAME), "migrationPolicy": i("Preserve these screens; do not create duplicate accepted screens or alter originals without parent decision"),
}
components["dependencyOrder"] = i(["tokens", "asset masters", "atomic controls", "region masters", "screen region instances", "QA replacement test"])
plans = [
    ("控件 / 主操作按钮", ["70:445", "70:447", "70:449", "70:451"], "Label:TEXT; source-family:VARIANT", ["A02/A03 soft grey", "A04/A05 near-black typography"], "Keep measured widths/heights and text styles; don't normalize all to one size."),
    ("控件 / 表单输入", ["70:205", "70:207", "70:209", "70:296", "70:298", "70:300", "70:302"], "Value:TEXT; leading:INSTANCE_SWAP; trailing:INSTANCE_SWAP; showTrailing:BOOLEAN", ["empty", "masked"], "Reparent each external leading/trailing icon into corresponding input instance; preserve screen-local placement."),
    ("控件 / 验证码单格", ["70:335", "70:337", "70:339", "70:341", "70:364", "70:366"], "Value:TEXT", ["empty only"], "Six master-linked cells in auto-layout; measure original per-cell widths, not assumed equal rounding."),
    ("区域 / 六位验证码", ["70:334"], "six Value:TEXT", ["empty only"], "Current width433 vs source visible block near436: remeasure gaps/edge stroke before replacing."),
    ("区域 / 注册表单", ["70:144", "70:205", "70:145", "70:207", "70:146", "70:209", "70:147"], "labels/value TEXT; field instance properties", [], "Label, field, help relationships must be auto-layout; preserve three original y groups."),
    ("区域 / 邮箱验证说明", ["70:719", "70:150", "70:151", "70:152"], "Title:TEXT; Description:TEXT; Email:TEXT; Artwork:INSTANCE_SWAP", [], "Center-aligned art plus text stack; no full screenshot layer."),
    ("区域 / 找回密码表单", ["70:158", "70:296", "70:449"], "Email:TEXT; ActionLabel:TEXT", [], "Add known photo/heading as separate region instances."),
    ("区域 / 重置密码表单", ["70:167", "70:298", "70:168", "70:300", "70:169", "70:170", "70:302", "70:369"], "Value TEXT; showConsistencyHint:BOOLEAN", ["source contradictory state"], "Document original inconsistency. Do not invent validated/invalid source variants; implementation state is separate."),
    ("区域 / 顶部系统与品牌", ["70:460", "70:486", "70:491", "70:462", "70:492", "70:497", "70:155", "70:500", "70:162", "70:507"], "Time:TEXT; code:TEXT; showPercentage:BOOLEAN; family:VARIANT", ["A02/A03", "A04/A05"], "Preserve screenshot differences, do not impose an OS design-system status bar."),
    ("素材 / 生活静物照片", ["70:36", "70:37", "70:38"], "Photo:INSTANCE_SWAP", ["A02", "A04", "A05"], "Build three measured asset masters with exact crop dimensions; no resizing to shared aspect ratio."),
    ("素材 / 图标与邮件插画", [node for _, _, _, nodes, _ in ART for node in nodes], "Artwork:INSTANCE_SWAP", [], "Resolve Image Two/source extraction provenance first; maintain source-specific artwork."),
    ("区域 / 返回与辅助操作", ["70:149", "70:154", "70:159", "70:171", "70:153"], "Label:TEXT", ["active link", "countdown visible"], "Use measured typography and locations; don't add interactions unsupported by screenshot."),
]
components["components"] = [{
    "name": i(name), "existingNodeIds": m(nodes), "masterId": u("not created"),
    "instanceIds": m([], "readback confirms zero instances"),
    "proposedProperties": i(properties), "sourceObservedStates": i(states),
    "replacementInstructions": i(instructions),
    "risk": i("Record parent-relative coordinates and z-order before replacement; verify only one visible copy remains."),
} for name, nodes, properties, states, instructions in plans]
components["tokens"] = {
    "proposedColorTokens": i(["surface/source-family", "text/primary", "text/secondary", "text/helper", "action/green", "border/input"]),
    "valueAuthority": i("Use layout.json sampled original colors, not current flat fills; separate A02/A03 and A04/A05 where source differs"),
    "spacingTokens": i("Only introduce shared tokens after measured repetition is established; preserve source-specific dimensions"),
    "fontTokens": i("Explicitly named fallback tokens until original font identity is known"),
}

qa["issues"] = [
    {
        "id": "AUTH-QA-01", "priority": i("P1"), "category": i("component_structure"),
        "nodeIds": m([s["node"] for s in SCREEN.values()]),
        "observation": m("All four screens contain zero components and zero instances; target page has no masters", READBACK),
        "cause": m("Primitive/vector/frame construction, no master-instance conversion", "construction log"),
        "fix": i("Execute component-plan in one writer; prove each repeated visual has master and instance before acceptance"),
    },
    {
        "id": "AUTH-QA-02", "priority": i("P1"), "category": i("font_identity_and_metrics"),
        "nodeIds": m([row[0] for rows in TEXT.values() for row in rows]),
        "observation": m("Current Noto Sans SC with Roboto masked bullets is an explicit fallback; original font identity is unknown", "readback and source metadata audit"),
        "cause": i("Fallback glyph outlines and widths differ from generated original typography"),
        "fix": i("Use per-text visible-ink delta records for measurement. Calibrate original line extent/baselines after font decision; do not treat current text boxes as original geometry"),
    },
    {
        "id": "AUTH-QA-03", "priority": i("P1"), "category": i("artwork_provenance"),
        "nodeIds": m([node for _, _, _, nodes, _ in ART for node in nodes]),
        "observation": m("Illustrations/icons were hand-authored SVG approximations, without Image Two/extraction asset provenance or fallback exception", "construction log"),
        "cause": m("Original bitmaps were interpreted geometrically before new skill was applied", "construction log"),
        "fix": i("Prioritize A03 mail illustration and A04 mail-hint artwork; extract from original or use approved Image Two workflow. Classify precise UI icons separately before retaining native vectors"),
    },
    {
        "id": "AUTH-QA-04", "priority": i("P2"), "category": i("material_and_color"),
        "nodeIds": m(["70:14", "70:16", "70:18", "70:20", "70:445", "70:447", "70:449", "70:451"]),
        "observation": m("Original has subtle surface/button variation; rebuild replaces it with uniform RGB fills", "sampled image statistics and paired images"),
        "cause": m("Flat SOLID paints used", "construction log"),
        "fix": i("Reconstruct only isolated material layer and measured mean colors, leaving button label and geometry native"),
    },
    {
        "id": "AUTH-QA-05", "priority": i("P2"), "category": i("otp_geometry"),
        "nodeIds": m(["70:334", "70:335", "70:337", "70:339", "70:341", "70:364", "70:366"]),
        "observation": m("Current OTP row is x39,y482,w433,h76; original visible outlined block is approximately x38..474,y481..559", "Figma readback plus source inspection"),
        "cause": i("Assumed six 63px cells and uniform 11px gap did not exactly preserve outer source edges"),
        "fix": i("Measure all six outlines and hyphen stroke lengths before cell-master creation; source outlines include antialiasing tolerance"),
    },
    {
        "id": "AUTH-QA-06", "priority": i("P2"), "category": i("detached_semantic_layers"),
        "nodeIds": m(["70:298", "70:368", "70:687", "70:300", "70:655", "70:679"]),
        "observation": m("Field rectangles/text use auto-layout but their icons and resend action are screen-level siblings", READBACK),
        "cause": m("Original build appended icons/actions directly to screen", "construction log"),
        "fix": i("Group under control masters while converting screen-local coordinates; verify icons remain aligned and no duplicate original survives"),
    },
    {
        "id": "AUTH-QA-07", "priority": i("P1_behavior_P3_visual"), "category": i("source_state_contradiction"),
        "nodeIds": m(["70:369", "70:691", "70:759"]),
        "observation": m("A05 original shows empty new-password placeholders while stating two passwords match; rebuild preserves it", "source PNG, manifest reviewNotes, current screenshot"),
        "cause": m("Known generated-concept issue recorded by manifest", "manifest.json pages.A05.reviewNotes"),
        "fix": i("Preserve source-traceable QA variant and explicit note; production behavior must conditionally show consistency only after nonempty valid comparison"),
    },
]
qa["gates"] = {
    "filePageIdentity": m("PASS", READBACK),
    "originalCanvasDimensions": m("PASS", "PNG and Figma width/height"),
    "noFullScreenshotInsideScreens": m("PASS", "image fill readback: A02/A04/A05 only photo, A03 no image"),
    "referenceLockedOutsideScreens": m("PASS", "reference sibling nodes readback"),
    "nativeVisibleText": m("PASS", "readback 61 TEXT nodes plus screenshots"),
    "componentMastersAndInstances": m("FAIL", "zero component/instance counts"),
    "assetComponents": m("FAIL", "photo rectangles and vector frames are not instances"),
    "fontExactness": m("FAIL", "fallback; original unknown"),
    "imageTwoArtworkProvenance": m("FAIL", "no compliant provenance/exceptions for interpreted artwork"),
    "twoDocumentedRepairRounds": u("Previous build has initial export then font/bullet correction and final comparison; two complete logged fix cycles not established"),
    "referenceLayersHiddenExport": u("No explicit hide-all-reference operation was performed; no screenshot dependency shown by subtree readback"),
    "disposableCopyTextAndAssetSwap": m("NOT_RUN", "read-only audit; must be performed by orchestrator"),
    "finalAcceptance": i("NOT_ACCEPTED; continue componentization and visual repairs"),
}
qa["nextWriterInstructions"] = i([
    "Use original PNGs as source of truth; do not restyle the current approximation as authoritative.",
    "Preserve locked references and originals; use current verified IDs, then re-read after any replacement.",
    "Componentize measured source regions, not scaled copies of earlier 390x844 designs.",
    "Keep one Figma writer; verify geometry and visual evidence after each replacement batch.",
    "Export after hiding references, conduct disposable-copy edit/swap test, and perform two recorded repair loops.",
])

for filename, content in [
    ("layout.json", layout),
    ("asset-manifest.json", assets),
    ("component-plan.json", components),
    ("qa-diff.json", qa),
]:
    destination = ROOT / filename
    destination.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    json.loads(destination.read_text(encoding="utf-8"))
    print(f"{filename}: {destination.stat().st_size} bytes")

print("verification.json preserved:", digest(ROOT / "verification.json"))
