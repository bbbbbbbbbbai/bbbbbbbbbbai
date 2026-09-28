"""Generate additive source measurements and clean artwork crops, never Figma."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parent
BOARDS = ROOT.parent.parent / "boards"
OUT = ROOT / "geometry-S01-S03.json"
ASSETS = ROOT / "assets" / "geometry-S01-S03"


def evidence(value, status="measured", method="Native 1536x1024 raster visual measurement; tolerance +/-2 px"):
    return {"value": value, "status": status, "method": method}


def text(content, x, y, w, h, size, weight="Regular", color="ink"):
    return {
        "kind": "TEXT",
        "content": evidence(content, method="Direct source transcription"),
        "boundsXYWH": evidence([x, y, w, h], "inferred", "Visible ink envelope plus minimal logical frame; tolerance +/-3 px; not source text-frame metadata"),
        "fontSize": evidence(size, "inferred", "Visible glyph-height estimate; calibrate with screenshot"),
        "fontWeight": evidence(weight, "inferred"),
        "colorToken": evidence(color, "inferred"),
    }


def rect(name, box, style="outlined", radius=6):
    return {"kind": "RECTANGLE", "name": name, "boundsXYWH": evidence(box), "style": evidence(style, "inferred"), "cornerRadius": evidence(radius, "inferred")}


assets = []


def art(board, name, box):
    img = Image.open(BOARDS / f"{board}.png")
    x, y, w, h = box
    path = ASSETS / board / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.crop((x, y, x + w, y + h)).save(path)
    a = {
        "id": f"{board}/{name}",
        "sourceBoard": board,
        "cropXYWH": evidence(box),
        "path": str(path),
        "dimensions": evidence([w, h]),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "alpha": evidence(False, method="RGB source and crop inspection"),
        "editable": False,
        "role": "independent replaceable artwork, never whole-screen background",
        "edgeTreatment": evidence("Retains original flattened light matte; no synthetic alpha removal", "measured"),
        "containsText": evidence(False, method="Visual crop review; pictorial symbols only"),
    }
    assets.append(a)
    return {"kind": "ASSET_INSTANCE", "assetId": a["id"], "boundsXYWH": evidence(box)}


states = []


def state(id_, viewport, elements, notes=None, screen_confidence="inferred"):
    states.append({
        "id": id_,
        "sourceBoard": id_.split("-")[0],
        "viewportXYWH": evidence(viewport, screen_confidence, "Visible UI boundary excluding board/state headings; unframed edges have +/-4px uncertainty"),
        "coordinateSpace": "All element bounds are board-absolute XYWH. For frame-local: subtract viewport.x/y; do not rescale.",
        "layerOrder": evidence(["background", "native containers", "artwork instances", "editable text", "focus/caret"], "inferred"),
        "overlayMask": evidence(None, method="No modal or scrim visible in this source state"),
        "elements": elements,
        "unknowns": notes or [],
    })


# S01: top row form states.
for num, x, mismatch in [(1, 78, False), (2, 582, True)]:
    els = [
        text("9:41", x-5, 117, 40, 18, 14), text("100%", x+350, 117, 43, 18, 14),
        text("注册账号", x+45, 149, 150, 28, 20, "Medium"),
        art("S01", f"back-{num}", [x-2, 153, 20, 19]),
        art("S01", f"status-{num}", [x+295, 117, 51, 17]),
        text("邮箱", x, 196, 80, 21, 16),
        rect("邮箱输入", [x, 220, 380 if num == 1 else 375, 44]),
        art("S01", f"email-{num}", [x+15, 232, 22, 21]),
        text("hello@example.com", x+54, 232, 270, 25, 16),
        text("密码", x, 277, 100, 21, 16),
        rect("密码输入", [x, 300, 380 if num == 1 else 375, 45]),
        art("S01", f"lock-password-{num}", [x+16, 310, 21, 24]),
        text("Abc12345", x+54, 312, 250, 25, 17),
        art("S01", f"eye-open-{num}", [x+341 if num == 1 else x+337, 312, 25, 21]),
        text("确认密码", x, 357, 150, 23, 16),
        rect("确认密码输入", [x, 380, 380 if num == 1 else 375, 46], "error-red-outline" if mismatch else "outlined"),
        art("S01", f"lock-confirm-{num}", [x+16, 391, 21, 24]),
        text("••••••••••", x+54, 392, 220, 23, 17),
        art("S01", f"eye-closed-{num}", [x+341 if num == 1 else x+337, 393, 25, 22]),
    ]
    if mismatch:
        els += [
            art("S01", "confirm-error", [581, 428, 24, 25]),
            text("两次输入的密码不一致", 613, 432, 300, 23, 16, color="error"),
            rect("注册禁用", [582, 465, 375, 47], "disabled"),
            text("注册", 736, 478, 65, 24, 18, "Medium", "white"),
            rect("返回", [582, 524, 375, 47]),
            text("返回", 736, 537, 65, 25, 18, "Medium"),
        ]
    else:
        els += [
            rect("可继续", [78, 452, 381, 51], "green"),
            text("可继续", 231, 466, 90, 25, 18, "Medium", "white"),
            rect("返回", [78, 514, 381, 47]),
            text("返回", 240, 527, 65, 25, 18, "Medium"),
        ]
    state(f"S01-0{num}", [55 if num == 1 else 553, 110, 435, 474], els,
          ["Password bullet count visually estimated. Each eye remains a separate replaceable asset.",
           "Source label 可继续 is literal source copy, not a proposed production wording."])

# S01 email code variants use distinct source geometry, not normalized clones.
code_variants = [
    (3, [1058, 110, 434, 454], [1083, 356, 395, 51], [1252, 197, 53, 40], 1083, 117, 1134, 150, 1166, 251, 1176, 280, 1083, 330, 1146, 370, 418, [1083,473,189,51], [1287,473,191,51]),
    (4, [178, 642, 512, 355], [188, 833, 490, 45], [409,702,49,35], 188, 646, 241, 680, 324, 747, 338, 775, 188, 808, 247, 846, 890, [188,929,238,51], [440,929,238,51]),
    (5, [856, 642, 597, 355], [870, 835, 570, 45], [1115,702,50,35], 870, 646, 923, 680, 1028, 747, 1047, 775, 870, 810, 929, 848, 893, [870,933,263,47], [1150,933,290,47]),
]
for n, vp, inp, envelope, sx, sy, tx, ty, dx, dy, ex, ey, lx, ly, ix, iy, fy, left, right in code_variants:
    wait = n == 5
    status_box = [1384,117,54,18] if n == 3 else ([583,646,54,18] if n == 4 else [1343,646,54,18])
    percent_x = 1440 if n == 3 else (640 if n == 4 else 1401)
    els = [
        text("9:41", sx-2, sy, 42, 20, 14),
        art("S01", f"status-{n}", status_box),
        text("100%", percent_x, sy, 44, 20, 14),
        art("S01", f"back-{n}", [sx, ty+2, 22, 24]),
        text("邮箱验证码", tx, ty, 170, 29, 20, "Medium"),
        art("S01", f"envelope-{n}", envelope),
        text("我们已向以下邮箱发送了验证码", dx, dy, 306 if n == 3 else 330, 23, 16),
        text("hello@example.com", ex, ey, 300, 29, 22, "Medium"),
        text("验证码", lx, ly, 100, 22, 16),
        rect("验证码输入", inp, "error-red-outline" if n == 3 else "outlined"),
        art("S01", f"shield-{n}", [inp[0]+18, inp[1]+12, 27, 28]),
        text("381204", ix, iy, 185, 26, 18),
        art("S01", f"feedback-{n}", [inp[0], fy-2, 25, 25]),
        text("48秒后重发" if wait else ("验证码已过期" if n == 4 else "验证码错误，请重试"), inp[0]+34, fy, 285, 24, 16, color="ink" if wait else "error"),
        rect("编辑邮箱", left),
        text("编辑邮箱", left[0]+(left[2]-100)/2, left[1]+14, 100, 25, 18, "Medium"),
        rect("等待重发" if wait else "主要操作", right, "disabled" if wait else "green"),
        text("重新发送" if n >= 4 else "重试", right[0]+(right[2]-100)/2, right[1]+14, 100, 25, 18, "Medium", "white"),
    ]
    if n == 3:
        els.append(art("S01", "code-error-clear", [1435, 369, 25, 26]))
    state(f"S01-0{n}", vp, els, ["Wait variant lacks a distinct verification submit action in source. Reproduce source here; functional remediation must be separately labelled."])

# S02 keyboard and long content, boundaries are explicit card edges.
login = [
    text("9:41",59,113,45,18,14),
    text("老白の日记",88,142,195,36,26,"Bold","green"),
    text("把日常，写成更好的自己",88,178,238,24,16,color="muted"),
    rect("邮箱",[88,215,625,45],"soft-field"),
    art("S02","login-mail",[104,228,23,19]),
    text("邮箱",145,228,37,24,14,color="muted"),
    rect("邮箱竖线",[182,226,1,23],"divider",0),
    text("laobai@example.com",193,230,395,20,14),
    rect("密码",[88,269,625,46],"soft-field"),
    art("S02","login-lock",[105,280,22,24]),
    text("密码",145,282,38,22,14,color="muted"),
    rect("密码竖线",[182,280,1,23],"divider",0),
    text("••••••••",194,283,330,23,16),
    art("S02","login-eye",[675,283,23,19]),
    rect("登录",[88,325,625,40],"green",6),
    text("登录",369,334,60,24,16,"Medium","white"),
    text("注册账号",356,376,96,22,15,color="green"),
    rect("系统键盘",[41,404,718,220],"keyboard-background",0),
    rect("手势条",[347,601,75,7],"gesture",4),
]
keyboard_rows = [
    ("qwertyuiop",54,412,59,35,8),
    ("asdfghjkl",98,455,59,36,8),
    ("zxcvbnm",165,498,59,37,8),
]
for chars,x,y,w,h,gap in keyboard_rows:
    for j,ch in enumerate(chars):
        kx=x+j*(w+gap)
        login += [rect(f"键 {ch}",[kx,y,w,h],"key",5),text(ch,kx+15,y+5,w-30,27,21)]
login += [
    rect("shift",[54,498,89,37],"modifier-key",5),
    art("S02","keyboard-shift",[87,506,23,22]),
    rect("delete",[647,498,98,38],"modifier-key",5),
    art("S02","keyboard-delete",[684,505,30,25]),
    rect("数字键",[54,543,98,38],"modifier-key",5),
    text("?123",83,551,60,25,18),
    rect("表情键",[161,543,63,38],"modifier-key",5),
    art("S02","keyboard-face",[180,549,24,24]),
    rect("空格",[232,543,325,38],"key",5),
    rect("句点",[567,543,69,38],"key",5),
    text(".",594,550,20,25,18),
    rect("回车",[647,543,98,38],"blue-key",5),
    art("S02","keyboard-return",[683,551,26,21]),
    art("S02","keyboard-hide",[99,597,21,14]),
    art("S02","keyboard-switch",[679,594,25,19]),
]
state("S02-01",[41,107,718,517],login,[
    "Banner art at [271,107,488,99] contains baked notebook/mug text. NOT extracted as no-text artwork; clean source absent.",
    "Status connectivity/battery lives in board label strip y73-106, not this UI frame; do not duplicate it.",
    "Keyboard is an illustrative raster reference; key geometry reproduced natively, real Android IME must remain OS-provided.",
], "measured")
state("S02-02",[778,107,718,517],[
    text("9:41",800,112,60,25,20),
    text("欢迎回来",852,146,335,46,34,"Bold"),
    text("在这里，继续记录生活",852,193,470,32,22,color="muted"),
    rect("邮箱",[829,241,616,78],"outlined",11),
    art("S02","large-mail",[851,266,33,28]),
    rect("邮箱竖线",[902,257,1,47],"divider",0),
    text("邮箱",919,250,100,28,20,color="muted"),
    text("laobai.diary.user.2025@example.com",919,278,510,35,26),
    rect("密码",[829,332,616,80],"outlined",11),
    art("S02","large-lock",[853,354,31,37]),
    rect("密码竖线",[902,348,1,47],"divider",0),
    text("密码",919,341,100,28,20,color="muted"),
    text("••••••••",922,372,380,37,26),
    art("S02","large-eye",[1390,359,34,29]),
    rect("登录",[829,433,616,64],"green",10),
    text("登录",1098,450,90,36,25,"Medium","white"),
    text("注册账号",1077,522,180,34,23,color="blue"),
],["Status connectivity/battery appears in strip y73-106; inherited strip is not in viewport.","Long email exactly fits reference; font is unknown, so calibrate instead of shrinking indiscriminately."],"measured")
state("S02-03",[41,671,718,340],[
    art("S02","food-back",[62,687,25,25]),
    text("记录饮食",125,687,180,31,22,"Medium"),
    text("完成",695,687,51,30,20,"Medium","green"),
    rect("食物卡",[63,734,674,256],"outlined",12),
    art("S02","food-dish",[87,761,106,96]),
    text("香煎鸡胸肉配西兰花\n与黑胡椒酱",211,762,345,66,27,"Bold"),
    text("每100g",572,785,72,28,20,color="muted"),
    art("S02","food-add",[653,763,65,63]),
    text("165",229,859,64,29,22),
    text("千卡",230,887,60,25,18,color="muted"),
    text("31.2g",358,859,74,29,22),
    text("蛋白质",358,887,82,25,18,color="muted"),
    text("5.6g",498,859,65,29,22),
    text("脂肪",500,887,58,25,18,color="muted"),
    text("2.8g",635,859,61,29,22),
    text("碳水化合物",616,887,108,25,18,color="muted"),
    rect("分隔1",[316,859,1,44],"divider",0),
    rect("分隔2",[452,859,1,44],"divider",0),
    rect("分隔3",[585,859,1,44],"divider",0),
    rect("横分隔",[87,921,627,1],"divider",0),
    text("食用重量",87,943,167,29,22),
    text("200",564,944,79,29,21),
    text("g",654,944,25,29,21),
    art("S02","weight-chevron",[689,949,20,16]),
],["Nutrition numbers are source examples, not new-account records.","Card shape is native; food dish and circular add pictogram remain independent assets."],"measured")
note = [
    art("S02","note-back",[797,677,26,24]),
    text("编辑备注",858,677,196,30,22,"Medium"),
    rect("备注输入",[852,707,598,127],"outlined",6),
    text("今天的午餐整体还不错，鸡胸肉煎得很香，西兰花也很清爽。\n黑胡椒酱稍微有点咸，下次可以少放一点。工作比较忙，\n但还是抽时间好好吃饭了，这种感觉很好。希望能继续保持，\n让饮食更规律，身体更有活力。",879,718,546,109,20),
    rect("滚动轨道",[1436,717,7,78],"soft-field",4),
    rect("滚动滑块",[1436,717,7,53],"scrollbar",4),
    rect("光标",[1149,798,2,27],"green",0),
    text("89/500",1390,811,46,18,12,color="muted"),
    rect("取消",[852,844,278,34],"green-outline",5),
    text("取消",971,851,54,22,17,"Medium","green"),
    rect("保存",[1141,844,309,34],"green",5),
    text("保存",1277,851,55,22,17,"Medium","white"),
    rect("系统键盘可见区",[778,884,718,127],"keyboard-background",0),
    rect("数字键",[791,927,107,40],"modifier-key",5),
    text("?123",823,936,68,26,19),
    rect("表情键",[906,927,74,40],"modifier-key",5),
    art("S02","note-keyboard-face",[930,934,25,25]),
    rect("逗号",[989,927,56,40],"key",5),
    text(",",1008,935,20,26,20),
    rect("空格",[1053,927,238,40],"key",5),
    rect("句号",[1300,927,71,40],"key",5),
    text("。",1326,936,25,26,20),
    rect("回车",[1378,927,104,40],"blue-key",5),
    art("S02","note-keyboard-return",[1417,936,28,21]),
    art("S02","note-keyboard-hide",[831,981,20,14]),
    art("S02","note-keyboard-switch",[1416,978,25,20]),
    rect("手势条",[1114,985,76,8],"gesture",4),
    art("S02","candidate-chevron",[1441,897,22,15]),
]
for word,x in zip(["我","你","在","这","不","一","是","有","今天"],[813,877,940,1002,1066,1130,1196,1260,1334]):
    note.append(text(word,x,893,46 if word=="今天" else 30,25,20))
state("S02-04",[778,671,718,340],note,["Visible note counter 89/500 is source artwork text; not calculated from transcribed string.","IME visible region has only candidate and bottom rows; do not invent hidden QWERTY rows."],"measured")

# S03 error and migration states. All are inline pages, not dialogs.
s03 = [
    (1,[60,119,675,406],[340,181,107,91],"无法连接服务器",[288,283,330,43,29],"请检查网络连接后重试",[282,330,329,31,22],[[200,377,385,50,"重试","green"],[200,437,385,51,"返回登录","outlined"]]),
    (2,[807,119,674,406],[1101,186,99,80],"同步失败，请稍后重试",[1005,287,394,42,28],"服务器暂时不可用，已保留您的登录状态",[959,331,442,30,21],[[944,376,410,52,"重试","green"],[944,437,410,51,"返回","outlined"]]),
    (3,[60,579,675,430],[342,615,104,85],"无法打开本地数据",[280,712,365,43,29],"可能是存储空间不足或数据文件异常",[230,754,395,31,21],[[200,866,388,49,"重试","green"],[200,926,388,48,"返回登录","outlined"]]),
    (4,[807,579,674,430],[1091,626,123,89],"账号迁移尚未完成",[1034,725,354,41,28],"您的历史数据正在迁移中\n记录不会被删除，请耐心等待",[1018,770,383,57,21],[[943,910,414,52,"返回登录","green"]]),
]
for n,vp,ab,heading,hb,desc,db,buttons in s03:
    left = 78 if n%2 else 824
    top = 123 if n<3 else 584
    hx,hy,hw,hh,hs=hb
    dx,dy,dw,dh,ds=db
    els=[
        text("9:41",left,top,62,24,18),
        art("S03",f"status-{n}",[604 if n%2 else 1357,top,65,20]),
        text("100%",675 if n%2 else 1427,top,59,24,18),
        text("老白の日记",left-2,top+35,197,34,25,"Bold"),
        art("S03",f"error-art-{n}",ab),
        text(heading,hx,hy,hw,hh,hs,"Bold"),
        text(desc,dx,dy,dw,dh,ds,color="muted"),
        rect("手势条",[318 if n%2 else 1068,512 if n<3 else 994,150 if n%2 else 157,7],"gesture",4),
    ]
    if n==2:
        els += [art("S03","signed-in-avatar",[1365,161,52,51]),text("小白",1426,158,59,30,21),text("已登录",1426,190,59,26,17,color="muted")]
    if n==3:
        els += [
            rect("详情入口",[162,796,462,54],"soft-field",13),
            art("S03","details-document",[183,806,30,32]),
            text("查看详情",231,809,169,31,22,"Medium"),
            art("S03","details-chevron",[590,812,15,24]),
        ]
    if n==4:
        els += [
            rect("迁移状态入口",[919,839,462,55],"soft-field",13),
            art("S03","migration-clock",[941,850,36,34]),
            text("查看状态",997,852,177,32,22,"Medium"),
            art("S03","migration-chevron",[1346,855,15,25]),
        ]
    for bx,by,bw,bh,label,style in buttons:
        els += [rect(label,[bx,by,bw,bh],style,8),text(label,bx+(bw-144)/2,by+11,144,34,23,"Medium","white" if style=="green" else "green")]
    state(f"S03-0{n}",vp,els,["Screen edges are unframed; crop is a conservative envelope, not a physical device aspect ratio.","Source is an inline state, with no dimming mask or modal.","Migration/sync retention copy is a visible design specimen and cannot prove backend migration status."])


def sampled(board, name, xy):
    rgb=Image.open(BOARDS/f"{board}.png").convert("RGB").getpixel(tuple(xy))
    return {"name":name,"value":evidence("#"+"".join(f"{v:02x}" for v in rgb),method=f"Exact pixel {board}{tuple(xy)}; one-point sample, not a flat-fill claim"),"sampleXY":xy}


doc = {
    "schemaVersion":"1.1.0",
    "createdAt":"2026-09-28",
    "scope":"Additive source measurement for S01-S03, 13 substates; no Figma writes; no generated external artwork",
    "interpretation":"面向个人健康记录用户的表单校验、键盘内容适配与首次进入失败状态；浅灰白底、绿动作、蓝过程、红错误。DESIGN_VARIANCE 2 / MOTION_INTENSITY 2 / VISUAL_DENSITY 6。",
    "sourceBoards":[{"id":b,"path":str(BOARDS/f"{b}.png"),"size":list(Image.open(BOARDS/f"{b}.png").size),"sha256":hashlib.sha256((BOARDS/f"{b}.png").read_bytes()).hexdigest(),"viewed":True} for b in ["S01","S02","S03"]],
    "corrections":[
        "Do not reuse old build_state_specs.py equal-height screen grid.",
        "S01 horizontal divider y598, upper vertical dividers x517 and1021; bottom vertical x768.",
        "S02 top card y73..624, bottom card y638..1011; state label strips are not app UI.",
        "S03 horizontal divider y536 and vertical divider x768; titles excluded from viewport.",
        "All screen sizes are board specimen crops; scaling to 512x1024 would distort the source.",
    ],
    "geometryLegend":{
        "measured":"Native-raster visually bounded contour, +/-2px except noted; not design source metadata.",
        "inferred":"Logical text frame, typography, semantics, layering, or unframed viewport; must validate in screenshot.",
        "unknown":"Font family, exact original fill/shadow/material model, runtime keyboard insets, backend state."
    },
    "globalUnknowns":{
        "fontFamily":evidence(None,"unknown","PNG contains no font metadata; Noto Sans SC may be used only as disclosed fallback."),
        "originalTextBaseline":evidence(None,"unknown","Only raster glyph envelopes are visible."),
        "texture":evidence("Subtle flattened gray-blue background and green button noise","inferred","Native flat fills will not reproduce every texture pixel."),
        "productionInsets":evidence(None,"unknown","These are board crops, not device screenshots."),
    },
    "colors":[sampled("S01","page",(50,300)),sampled("S01","green-primary",(95,479)),sampled("S01","disabled",(600,482)),sampled("S01","error-red",(1085,428)),sampled("S02","keyboard-background",(750,420)),sampled("S03","secondary-outline",(201,459))],
    "states":states,
    "assets":assets,
    "componentPlan":[
        {"family":"S01 registration","instances":["S01-01","S01-02"],"native":["labels","inputs","feedback","buttons"],"replaceable":["mail","lock","eye","status"],"properties":["Password:TEXT","Confirm:TEXT","Error:TEXT","ErrorVisible:BOOLEAN","Eye:INSTANCE_SWAP","SubmitEnabled:BOOLEAN"]},
        {"family":"S01 code validation","instances":["S01-03","S01-04","S01-05"],"native":["email","input","feedback","buttons"],"replaceable":["envelope","shield","error/wait"],"properties":["Email:TEXT","Code:TEXT","Feedback:TEXT","FeedbackArt:INSTANCE_SWAP","Submit:TEXT","SubmitEnabled:BOOLEAN"],"note":"Geometry differs per source variant; do not force uniform widths."},
        {"family":"S02 login responsive specimens","instances":["S02-01","S02-02"],"native":["inputs","buttons","keyboard keycaps and characters"],"replaceable":["field symbols"],"note":"Banner no-text artwork missing; keyboard illustrative only."},
        {"family":"S02 food row","instances":["S02-03"],"native":["title","nutrition columns","amount row"],"replaceable":["dish","add","chevron"]},
        {"family":"S02 note editor","instances":["S02-04"],"native":["textarea","text","counter","scrollbar","buttons","IME keys"]},
        {"family":"S03 inline failure","instances":["S03-01","S03-02","S03-03","S03-04"],"native":["title","body","actions","detail rows","status text"],"replaceable":["main art","detail icon","avatar"],"properties":["Title:TEXT","Message:TEXT","Artwork:INSTANCE_SWAP","DetailVisible:BOOLEAN","AccountVisible:BOOLEAN"]},
    ],
    "acceptance":{"figmaBuilt":False,"visualRounds":0,"accepted":False,"remaining":["Source crops retain light matte; compare edge color after import.","S02-01 hero art includes lettering and has no clean no-text source.","Logical text frames and fallback typography require Figma calibration.","No full-screen bitmap asset was generated."]},
}
if OUT.exists():
    raise SystemExit(f"Refusing to overwrite existing artifact: {OUT}")
OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"path":str(OUT),"states":len(states),"assets":len(assets),"elements":sum(len(s["elements"]) for s in states)},ensure_ascii=False))
