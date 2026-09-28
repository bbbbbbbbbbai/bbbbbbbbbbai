"""Analyze existing G01-G09 reference pixels; never writes Figma or application code."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from source_spec_common_readonly import build, measured, inferred, unknown

text = {}
controls = {}
crops = []
titles = {}
samples = {}
extras = {}


def t(key, content, box, size=22, weight=400, light=False, align="LEFT"):
    return (key, content, box, size, weight, light, align)


def c(key, kind, box, radius=0, stroke=0, state=""):
    return (key, kind, box, radius, stroke, state)


def asset(code, name, box, kind="source_icon", note="Exact original crop; no neighboring editable text."):
    crops.append((f"{code}-{name}", code, box, kind, note))


def region(name, box, kind, fixed=False):
    return {
        "name": measured(name, "visible source grouping"),
        "boundsXYWH": measured(box),
        "type": inferred(kind),
        "fixed": inferred(fixed, "screen composition; scrolling behavior is not proven by a static raster"),
    }


def setup(code, title, bg, ink, accent, regions):
    titles[code] = title
    samples[code] = {"background": bg, "primary_ink": ink, "accent": accent}
    text[code] = []
    controls[code] = []
    extras[code] = {
        "regions": regions,
        "viewport": measured([0, 0, 512, 1024]),
        "visibleSafeAreas": {
            "top": measured([0, 0, 512, 65]),
            "bottom": measured([0, 990, 512, 34]),
            "actualAndroidInsets": unknown("Generated reference has no device density or system inset metadata"),
        },
        "materials": [
            inferred("Flattened very-light surface with subtle texture and soft shadows; plain fill alone will not be pixel-identical."),
            unknown("Original shadow blur/spread/opacity and texture blend mode are unavailable."),
        ],
        "fontMetrics": {
            "actualFamily": unknown("Raster source only"),
            "candidateFamily": inferred("Noto Sans SC"),
            "letterSpacing": inferred(0),
            "direction": measured("LTR", "visible text reading order"),
            "baseline": unknown("Ink bounds are measured; original font baseline is not embedded in PNG."),
            "wrapping": inferred("Keep explicit source line breaks; calibrate fallback font before screenshot acceptance."),
        },
        "zOrder": inferred(["background", "regions and control surfaces", "asset instances", "editable text", "selection and action overlays"]),
        "uncertainties": [
            unknown("Exact original font and text-frame dimensions"),
            unknown("Real touch targets, keyboard viewport, and scroll behavior"),
            inferred("Coordinates are original raster pixels; do not reinterpret as Android dp."),
        ],
    }


setup("G01", "问题目录", (215, 831, 322, 862), (31, 102, 161, 133), (47, 190, 76, 223), [
    region("页头", [0, 0, 512, 160], "header", True),
    region("回答状态筛选", [31, 179, 452, 59], "segmented control"),
    region("系统问题", [31, 282, 452, 339], "section and repeated rows"),
    region("自定义问题", [31, 663, 452, 145], "section and repeated rows"),
    region("底部导航", [0, 886, 512, 103], "navigation", True),
])
text["G01"] = [
    t("reference-code", "G01 问题目录", [17, 5, 180, 25], 17),
    t("time", "9:41", [30, 35, 62, 29], 20),
    t("battery", "100%", [439, 34, 66, 30], 20),
    t("title", "问题目录", [30, 95, 320, 50], 34, 700),
    t("all", "全部", [31, 194, 151, 37], 24, 600, True, "CENTER"),
    t("unanswered", "未答", [182, 194, 151, 37], 24, 400, False, "CENTER"),
    t("answered", "已答", [333, 194, 150, 37], 24, 400, False, "CENTER"),
    t("system-title", "系统问题", [31, 282, 360, 38], 26, 700),
    t("system-count", "3", [456, 284, 25, 38], 25, 400, False, "RIGHT"),
    t("custom-title", "自定义问题", [31, 659, 360, 43], 26, 700),
    t("custom-count", "1", [456, 664, 25, 36], 25, 400, False, "RIGHT"),
]
for i, (name, y, state) in enumerate([
    ("今天最想记住什么？", 359, "已答"),
    ("最近有什么事情让你感到期待？", 451, "未答"),
    ("今年想培养的习惯是什么？", 550, "已答"),
    ("我希望如何安排下一个周末？", 741, "未答"),
]):
    text["G01"] += [
        t(f"question-{i}", name, [79, y, 286, 34], 22),
        t(f"state-{i}", state, [370, y+2, 77, 34], 20, 400, False, "CENTER"),
    ]
    controls["G01"] += [
        c(f"state-pill-{i}", "rounded_rect", [369, y-1, 78, 39], 20, 0, state),
    ]
for i, (s, x) in enumerate([("今日", 42), ("记录", 165), ("向往", 291), ("我的", 416)]):
    text["G01"].append(t(f"nav-label-{i}", s, [x, 944, 58, 33], 20, 400, False, "CENTER"))
controls["G01"] += [
    c("filter-track", "rounded_rect", [31, 179, 452, 59], 16),
    c("filter-active", "rounded_rect", [31, 179, 151, 58], 16, 0, "全部"),
    *[c(f"divider-{y}", "line", [31, y, 452, 1]) for y in [332, 421, 516, 620, 710, 807]],
    c("navigation-divider", "line", [0, 886, 512, 1]),
    c("gesture", "rounded_rect", [179, 1004, 154, 6], 3),
]
asset("G01", "system-status", (364, 34, 434, 60))
asset("G01", "help", (439, 96, 480, 137))
asset("G01", "question-icon", (30, 357, 62, 393))
asset("G01", "row-chevron", (466, 365, 481, 388))
for name, box in [
    ("nav-today", (50, 902, 88, 941)),
    ("nav-history", (174, 902, 212, 940)),
    ("nav-life-active", (300, 900, 340, 942)),
    ("nav-profile", (424, 902, 463, 940)),
]:
    asset("G01", name, box)
extras["G01"]["sourceVsProductConflict"] = measured([
    "原图未画新增自定义问题入口。",
    "原图未画问题/清单/足迹分区切换。",
    "严格还原稿保留原图；需求补齐另用清楚标注的修订变体，不悄悄改动参考稿。",
], "manifest reviewNotes and original source")

setup("G02", "问题与历次回答", (183, 972, 321, 995), (95, 103, 300, 130), (59, 906, 94, 940), [
    region("页头", [0, 0, 512, 174], "header", True),
    region("当前问题", [31, 200, 450, 197], "question context"),
    region("已有答案及日期", [31, 423, 450, 420], "answer history"),
    region("继续回答", [31, 885, 451, 77], "primary action", True),
])
text["G02"] = [
    t("reference-code", "G02 问题与历次回答", [15, 3, 240, 26], 17),
    t("time", "9:41", [31, 34, 66, 31], 20),
    t("battery", "100%", [439, 34, 65, 31], 20),
    t("title", "问题与历次回答", [94, 96, 319, 49], 31, 700),
    t("question-label", "当前问题", [31, 199, 360, 39], 23),
    t("question", "最近有什么事情让你感到期待？", [31, 243, 451, 43], 29, 700),
    t("question-help", "关于未来的期待，可以是生活、工作、学习或其他\n任何让你开心的事情。", [31, 301, 451, 65], 21),
    t("history-title", "已有答案及日期", [31, 425, 240, 39], 24, 600),
    t("history-explanation", "历史答案会被完整保留，\n不会被新回答覆盖。", [278, 421, 204, 57], 19),
    t("continue", "继续回答", [31, 906, 451, 38], 25, 600, True, "CENTER"),
]
for i, (date, answer, y) in enumerate([
    ("2025年3月12日", "周末去公园走走。", 510),
    ("2025年3月05日", "把书架重新整理好。", 631),
    ("2025年2月21日", "学会一道新菜。", 755),
]):
    text["G02"] += [
        t(f"date-{i}", date, [31, y, 451, 36], 22),
        t(f"answer-{i}", answer, [31, y+39, 451, 42], 25),
    ]
controls["G02"] = [
    *[c(f"divider-{y}", "line", [31, y, 451, 1]) for y in [174, 397, 493, 614, 739]],
    c("continue", "rounded_rect", [31, 885, 451, 77], 12),
]
asset("G02", "system-status", (364, 34, 434, 61))
asset("G02", "back", (28, 102, 60, 131))
asset("G02", "help", (438, 95, 480, 138))
extras["G02"]["sourceVsProductConflict"] = measured(
    "参考图包含历史保留实现说明；manifest要求后续产品修订删去，但严格还原稿应忠实保留并另做修订变体。",
    "manifest reviewNotes and original",
)

setup("G03", "写下回答", (163, 848, 317, 900), (100, 98, 206, 124), (291, 628, 324, 654), [
    region("页头", [0, 0, 512, 146], "header", True),
    region("问题上下文", [27, 158, 460, 110], "context panel"),
    region("回答编辑器", [27, 291, 460, 292], "multiline input"),
    region("取消保存", [27, 613, 460, 57], "actions"),
])
text["G03"] = [
    t("reference-code", "G03 写下回答", [20, 8, 230, 24], 16),
    t("time", "9:41", [31, 39, 67, 32], 20),
    t("battery", "100%", [425, 38, 66, 33], 20),
    t("title", "写下回答", [98, 91, 286, 44], 28, 700),
    t("header-save", "保存", [437, 94, 50, 39], 24, 500),
    t("question", "今天，什么让你感到轻松？", [48, 179, 421, 38], 25, 600),
    t("question-help", "可以是一件小事、一个瞬间，或任何让你放松的东西。", [48, 222, 425, 34], 18),
    t("placeholder", "写下你的回答…", [48, 307, 420, 42], 23),
    t("counter", "0/500", [414, 546, 59, 31], 18, 400, False, "RIGHT"),
    t("cancel", "取消", [27, 625, 220, 38], 23, 400, False, "CENTER"),
    t("save", "保存", [266, 625, 221, 38], 23, 500, True, "CENTER"),
]
controls["G03"] = [
    c("question-context", "rounded_rect", [27, 158, 460, 110], 12),
    c("answer", "rounded_rect", [27, 291, 460, 292], 9, 1, "empty"),
    c("cancel", "rounded_rect", [27, 613, 220, 57], 10, 1),
    c("save", "rounded_rect", [266, 613, 221, 57], 10),
    c("gesture", "rounded_rect", [179, 1004, 154, 6], 3),
]
asset("G03", "system-status", (353, 42, 422, 66))
asset("G03", "back", (28, 96, 57, 126))
extras["G03"]["sourceVsProductConflict"] = measured([
    "原图上下有两个保存入口；产品修订应合并，严格还原稿保留后另标修订。",
    "0/500仅是生成原图示例；真实上限未知，不能据此改业务约束。",
], "manifest reviewNotes and original")

setup("G04", "新增自定义问题", (153, 851, 319, 895), (98, 98, 281, 123), (291, 612, 324, 638), [
    region("页头", [0, 0, 512, 144], "header", True),
    region("上下文", [27, 161, 460, 64], "context"),
    region("问题表单", [27, 246, 460, 320], "form"),
    region("取消保存", [27, 597, 460, 58], "actions"),
])
text["G04"] = [
    t("reference-code", "G04 自定义问题", [20, 8, 240, 24], 16),
    t("time", "9:41", [31, 39, 67, 32], 20),
    t("battery", "100%", [425, 38, 66, 33], 20),
    t("title", "新增自定义问题", [97, 92, 320, 42], 28, 700),
    t("header-save", "保存", [437, 94, 50, 39], 24, 500),
    t("context-title", "编辑自定义问题", [27, 160, 460, 33], 21, 600),
    t("context-help", "创建一个属于你自己的问题，用于日常记录。", [27, 193, 460, 35], 18),
    t("group-label", "分组", [27, 246, 460, 32], 21, 600),
    t("group-value", "生活", [45, 296, 385, 36], 22),
    t("question-label", "问题", [27, 369, 460, 34], 21, 600),
    t("question-placeholder", "输入你想问自己的问题...", [45, 418, 423, 39], 21),
    t("counter", "0/100", [414, 529, 59, 31], 18, 400, False, "RIGHT"),
    t("cancel", "取消", [27, 611, 220, 38], 23, 400, False, "CENTER"),
    t("save", "保存", [266, 611, 221, 38], 23, 500, True, "CENTER"),
]
controls["G04"] = [
    c("group", "rounded_rect", [27, 284, 460, 55], 9, 1, "生活"),
    c("question", "rounded_rect", [27, 405, 460, 161], 9, 1, "empty"),
    c("cancel", "rounded_rect", [27, 597, 220, 58], 10, 1),
    c("save", "rounded_rect", [266, 597, 221, 58], 10),
    c("gesture", "rounded_rect", [179, 1004, 154, 6], 3),
]
asset("G04", "system-status", (353, 42, 422, 66))
asset("G04", "back", (28, 96, 57, 126))
asset("G04", "dropdown", (449, 302, 471, 321))
extras["G04"]["sourceVsProductConflict"] = measured([
    "原图标题是新增，说明是编辑；原图文本照录，不据此猜测编辑状态。",
    "上下保存重复，0/100不是经代码验证的字符上限。",
], "manifest and source")

setup("G05", "人生清单", (150, 951, 360, 981), (101, 100, 211, 124), (43, 218, 68, 237), [
    region("页头", [0, 0, 512, 151], "header", True),
    region("分类", [26, 169, 461, 78], "segmented control"),
    region("完成统计", [26, 267, 461, 111], "three summary tiles"),
    region("系统模板", [26, 414, 461, 300], "checklist section"),
    region("自定义", [26, 750, 461, 173], "checklist section"),
])
text["G05"] = [
    t("reference-code", "G05 人生清单", [21, 8, 226, 24], 16),
    t("time", "9:41", [31, 39, 67, 32], 20),
    t("battery", "100%", [425, 38, 66, 33], 20),
    t("title", "人生清单", [99, 92, 278, 43], 28, 700),
    t("add", "添加", [443, 94, 49, 35], 21, 500),
    t("category-label", "分类", [25, 166, 460, 34], 21, 600),
    t("category-travel", "旅行", [26, 211, 153, 32], 19, 400, True, "CENTER"),
    t("category-learning", "学习", [179, 211, 154, 32], 19, 400, False, "CENTER"),
    t("category-life", "生活", [333, 211, 154, 32], 19, 400, False, "CENTER"),
    t("system-title", "系统模板", [25, 414, 463, 34], 21, 700),
    t("system-help", "这些是内置的示例清单项，你可以参考或按自己的想法调整。", [25, 446, 463, 31], 17),
    t("custom-title", "自定义", [25, 750, 463, 35], 21, 700),
    t("custom-help", "你添加的个人清单项。", [25, 782, 463, 29], 17),
]
for i, (label, count, x) in enumerate([("未开始", "3", 26), ("进行中", "1", 187), ("已完成", "2", 347)]):
    text["G05"] += [
        t(f"summary-label-{i}", label, [x+59, 285, 80, 31], 17),
        t(f"summary-count-{i}", count, [x+58, 315, 28, 43], 32, 500),
        t(f"summary-unit-{i}", "项", [x+83, 326, 37, 30], 19),
    ]
    controls["G05"].append(c(f"summary-{i}", "rounded_rect", [x, 267, 141, 110], 9, 1))
for i, (name, state, y) in enumerate([
    ("去看一次海", "未开始", 490),
    ("登上一座山", "进行中", 556),
    ("去一个从未去过的城市", "已完成", 621),
    ("和喜欢的人一起去旅行", "已完成", 830),
]):
    text["G05"] += [
        t(f"item-title-{i}", name, [75, y+3, 288, 33], 22),
        t(f"item-state-{i}", state, [368, y+4, 75, 30], 17, 400, False, "CENTER"),
    ]
    controls["G05"].append(c(f"item-pill-{i}", "rounded_rect", [368, y, 75, 37], 10, 0, state))
text["G05"] += [
    t("feeling-2", "完成感受：看到了不一样的风景，心情很放松。", [89, 677, 387, 29], 17),
    t("feeling-3", "完成感受：一路上有很多开心的回忆。", [89, 886, 387, 29], 17),
]
controls["G05"] += [
    c("header-divider", "line", [26, 150, 461, 1]),
    c("category-track", "rounded_rect", [26, 205, 461, 42], 8, 1),
    c("category-selected", "rounded_rect", [26, 205, 153, 41], 7, 0, "旅行"),
    c("category-divider", "line", [333, 210, 1, 31]),
    *[c(f"divider-{y}", "line", [26, y, 461, 1]) for y in [397, 541, 605, 734]],
    c("feeling-2", "rounded_rect", [76, 666, 411, 46], 9),
    c("feeling-3", "rounded_rect", [76, 877, 411, 45], 9),
    c("gesture", "rounded_rect", [179, 1004, 154, 6], 3),
]
asset("G05", "system-status", (353, 42, 422, 66))
asset("G05", "back", (28, 96, 57, 127))
asset("G05", "add", (406, 96, 437, 127))
asset("G05", "state-idle-large", (24, 491, 61, 527))
asset("G05", "state-progress-large", (23, 556, 61, 593))
asset("G05", "state-complete-large", (23, 620, 62, 658))
asset("G05", "more", (468, 497, 480, 521))
asset("G05", "summary-idle", (41, 287, 73, 320))
asset("G05", "summary-progress", (203, 285, 240, 322))
asset("G05", "summary-complete", (364, 285, 401, 322))
extras["G05"]["sourceVsProductConflict"] = measured([
    "菜单具体内容不可见，不能推断系统模板可被删除。",
    "完成数为原图示例；新账号不得继承3/1/2和任何完成勾选。",
    "系统模板名称与项目真实目录是否一致尚未核对。",
], "manifest reviewNotes and visible source")

setup("G06", "创建清单项目", (156, 561, 346, 599), (30, 130, 254, 163), (53, 816, 91, 841), [
    region("页头", [0, 0, 512, 178], "large title header", True),
    region("项目分类表单", [29, 209, 455, 242], "form"),
    region("保存取消", [29, 794, 455, 153], "actions", True),
])
text["G06"] = [
    t("time", "9:41", [27, 12, 66, 30], 19),
    t("title", "创建清单项目", [29, 121, 458, 58], 38, 700),
    t("item-label", "项目", [29, 206, 455, 35], 21),
    t("item-value", "每天阅读30分钟", [47, 262, 382, 42], 24, 500),
    t("category-label", "分类", [29, 346, 455, 36], 21),
    t("category-value", "学习成长", [47, 400, 376, 42], 25),
    t("save", "保存", [29, 813, 455, 42], 27, 500, True, "CENTER"),
    t("cancel", "取消", [29, 895, 455, 42], 27, 500, False, "CENTER"),
]
controls["G06"] = [
    c("item", "rounded_rect", [29, 243, 455, 68], 10, 1, "filled"),
    c("category", "rounded_rect", [29, 382, 455, 68], 10, 1, "学习成长"),
    c("save", "rounded_rect", [29, 794, 454, 69], 13),
    c("cancel", "rounded_rect", [29, 877, 454, 70], 13),
    c("gesture", "rounded_rect", [172, 998, 169, 7], 4),
]
asset("G06", "system-status", (376, 15, 469, 37))
asset("G06", "back", (28, 63, 63, 97))
asset("G06", "clear", (441, 263, 471, 293))
asset("G06", "dropdown", (446, 406, 469, 426))

setup("G07", "记录完成感受", (162, 755, 324, 778), (31, 132, 254, 161), (53, 816, 91, 842), [
    region("页头", [0, 0, 512, 178], "large title header", True),
    region("关联清单项目", [29, 192, 455, 77], "context row"),
    region("完成感受", [29, 298, 455, 205], "multiline input"),
    region("照片", [29, 532, 454, 207], "attachment row"),
    region("保存取消", [29, 794, 455, 153], "actions", True),
])
text["G07"] = [
    t("time", "9:41", [27, 12, 66, 30], 19),
    t("title", "记录完成感受", [29, 121, 458, 58], 38, 700),
    t("item-title", "每天阅读30分钟", [101, 214, 362, 35], 22, 500),
    t("feeling-label", "完成感受", [29, 296, 455, 37], 21),
    t("feeling", "今天读完了《被讨厌的勇气》的一章，内容\n很有启发。放下别人的期待，专注自己的生活，\n感觉心里轻松了很多。", [47, 349, 422, 100], 22),
    t("counter", "42/500", [400, 466, 68, 28], 18, 400, False, "RIGHT"),
    t("photo-label", "照片（2/3）", [29, 531, 455, 37], 21),
    t("save", "保存", [29, 813, 455, 42], 27, 500, True, "CENTER"),
    t("cancel", "取消", [29, 895, 455, 42], 27, 500, False, "CENTER"),
]
controls["G07"] = [
    c("context", "rounded_rect", [29, 192, 455, 77], 12),
    c("feeling", "rounded_rect", [29, 334, 455, 169], 11, 1, "filled"),
    c("photo-1-slot", "rounded_rect", [29, 571, 150, 168], 11),
    c("photo-2-slot", "rounded_rect", [188, 571, 150, 168], 11),
    c("photo-add", "dashed_rounded_rect", [347, 571, 136, 168], 11, 1),
    c("save", "rounded_rect", [29, 794, 454, 69], 13),
    c("cancel", "rounded_rect", [29, 877, 454, 70], 13),
    c("gesture", "rounded_rect", [172, 998, 169, 7], 4),
]
asset("G07", "system-status", (380, 15, 472, 37))
asset("G07", "back", (28, 63, 63, 97))
asset("G07", "delete", (455, 62, 486, 98))
asset("G07", "book-context", (48, 211, 91, 250))
asset("G07", "book-photo-1", (29, 571, 179, 739), "source_photo_with_overlay",
      "Contains removable X control at top-right. Do not use as final clean photo until overlay is removed; book cover text is photographic content, not UI.")
asset("G07", "book-photo-2", (188, 571, 338, 739), "source_photo_with_overlay",
      "Contains removable X control at top-right. Keep photograph and editable remove action separate; requires clean extraction.")
asset("G07", "photo-remove", (140, 575, 176, 611), "source_icon_with_overlay",
      "Circular X over photographic pixels; only inner circle can be reused cleanly, alpha unknown. Needs mask/crop verification.")
asset("G07", "photo-add", (394, 635, 435, 677))
extras["G07"]["sourceVsProductConflict"] = measured([
    "42/500与可见正文长度未验证；不能推断真实输入长度限制。",
    "书封和页面内印刷文字属于照片，不拆成界面文字。",
], "visible source")

setup("G08", "生活足迹", (195, 841, 332, 871), (27, 69, 155, 96), (303, 915, 340, 939), [
    region("页头", [0, 0, 512, 157], "title and subtitle", True),
    region("问题清单足迹", [0, 161, 512, 56], "tabs"),
    region("向往介绍", [25, 239, 464, 73], "section heading"),
    region("足迹列表", [18, 330, 477, 493], "repeated entry cards"),
    region("底部导航", [0, 891, 512, 92], "navigation", True),
])
text["G08"] = [
    t("time", "9:41", [26, 12, 66, 30], 19),
    t("title", "生活足迹", [25, 58, 391, 52], 34, 700),
    t("subtitle", "记录生活的点滴，珍藏每一段时光", [25, 111, 463, 34], 19),
    t("tab-questions", "问题", [19, 169, 151, 35], 22, 400, False, "CENTER"),
    t("tab-checklist", "清单", [181, 169, 151, 35], 22, 400, False, "CENTER"),
    t("tab-footprint", "足迹", [345, 169, 143, 35], 22, 500, False, "CENTER"),
    t("section-title", "向往", [25, 237, 462, 42], 30, 700),
    t("section-help", "在生活中发现美好，让日常也闪闪发光", [25, 281, 463, 34], 19),
    t("date-0", "2025年4月12日  周六", [40, 350, 325, 34], 17),
    t("entry-title-0", "公园散步", [40, 386, 296, 35], 23, 600),
    t("location-0", "星河公园", [69, 426, 267, 34], 20),
    t("body-0", "傍晚的公园微风很舒服，树木郁郁葱葱，\n走在湖边感觉整个人都放松下来了。", [40, 469, 299, 62], 18),
    t("date-1", "2025年4月5日  周六", [40, 600, 325, 34], 17),
    t("entry-title-1", "周末晚餐", [40, 636, 296, 35], 23, 600),
    t("location-1", "小满餐厅", [69, 676, 267, 34], 20),
    t("body-1", "和好朋友一起吃了期待很久的意面，\n聊了很多有趣的话题，简单的晚餐\n也很幸福。", [40, 721, 298, 80], 18),
]
for i, (label, x) in enumerate([("今日", 31), ("记录", 160), ("向往", 291), ("我的", 421)]):
    text["G08"].append(t(f"nav-label-{i}", label, [x, 944, 59, 35], 19, 400, False, "CENTER"))
controls["G08"] = [
    c("tabs-divider", "line", [0, 216, 512, 1]),
    c("tabs-active", "rounded_rect", [346, 213, 141, 4], 2, 0, "足迹"),
    c("entry-0", "rounded_rect", [18, 330, 477, 229], 11, 1),
    c("entry-1", "rounded_rect", [18, 579, 477, 244], 11, 1),
    c("photo-0-slot", "rounded_rect", [346, 396, 132, 141], 11),
    c("photo-1-slot", "rounded_rect", [346, 646, 132, 155], 11),
    c("nav-divider", "line", [0, 891, 512, 1]),
    c("gesture", "rounded_rect", [172, 998, 169, 7], 4),
]
asset("G08", "system-status", (389, 15, 483, 37))
asset("G08", "add", (450, 63, 488, 104))
asset("G08", "edit", (382, 349, 414, 383))
asset("G08", "delete", (443, 349, 471, 383))
asset("G08", "location", (39, 427, 63, 455))
asset("G08", "park-photo", (346, 396, 478, 537), "source_photo",
      "Original rounded crop, no adjacent editable UI text. Preserve natural source crop and radius.")
asset("G08", "dinner-photo", (346, 646, 478, 801), "source_photo",
      "Original rounded crop, no adjacent editable UI text. Source aspect differs from park thumbnail.")
for name, box in [
    ("nav-today", (42, 904, 79, 940)),
    ("nav-history", (173, 904, 209, 940)),
    ("nav-life-active", (301, 904, 343, 940)),
    ("nav-profile", (434, 904, 470, 940)),
]:
    asset("G08", name, box)

setup("G09", "新增足迹", (161, 964, 337, 986), (209, 67, 302, 89), (51, 869, 88, 894), [
    region("页头", [0, 0, 512, 115], "header", True),
    region("足迹表单", [27, 124, 460, 489], "form"),
    region("照片", [27, 632, 460, 177], "attachment row"),
    region("保存取消", [27, 849, 459, 115], "actions"),
])
text["G09"] = [
    t("time", "9:41", [25, 10, 64, 32], 19),
    t("battery", "100%", [437, 9, 66, 32], 20),
    t("title", "新增足迹", [130, 58, 253, 42], 25, 600, False, "CENTER"),
    t("title-label", "标题", [26, 121, 459, 31], 19),
    t("title-value", "海边散步", [46, 168, 420, 36], 22),
    t("location-label", "地点", [26, 228, 459, 33], 19),
    t("location-value", "东岸公园", [46, 276, 420, 36], 22),
    t("date-label", "日期", [26, 337, 459, 33], 19),
    t("date-value", "2026年9月26日", [46, 385, 387, 36], 24),
    t("body-label", "正文", [26, 447, 459, 33], 19),
    t("body", "下午的海风很温柔，沿着海岸慢慢走，听着\n海浪的声音，整个人都放松了。生活或许就是\n这样，在平凡的日子里也能找到小小的幸福。", [46, 495, 425, 99], 22),
    t("photo-label", "照片（2/3）", [26, 630, 459, 33], 19),
    t("save", "保存", [27, 863, 459, 40], 23, 500, True, "CENTER"),
    t("cancel", "取消", [27, 931, 459, 39], 22, 400, False, "CENTER"),
]
controls["G09"] = [
    c("title-input", "rounded_rect", [27, 156, 460, 55], 10, 1, "filled"),
    c("location-input", "rounded_rect", [27, 264, 460, 55], 10, 1, "filled"),
    c("date-input", "rounded_rect", [27, 373, 460, 56], 10, 1, "2026-09-26"),
    c("body-input", "rounded_rect", [28, 483, 459, 130], 10, 1, "filled"),
    c("photo-0-slot", "rounded_rect", [29, 667, 141, 141], 12),
    c("photo-1-slot", "rounded_rect", [187, 667, 141, 141], 12),
    c("photo-add", "dashed_rounded_rect", [346, 667, 140, 141], 12, 1),
    c("save", "rounded_rect", [27, 849, 459, 61], 13),
    c("gesture", "rounded_rect", [168, 998, 175, 6], 3),
]
asset("G09", "system-status", (363, 11, 432, 34))
asset("G09", "back", (24, 61, 54, 93))
asset("G09", "calendar", (443, 386, 472, 417))
asset("G09", "beach-photo", (29, 667, 170, 808), "source_photo_with_overlay",
      "Top-right remove control is baked into the source thumbnail. Requires clean extraction, not a complete UI-image replacement.")
asset("G09", "sunset-photo", (187, 667, 328, 808), "source_photo_with_overlay",
      "Top-right remove control is baked into the source thumbnail. Requires clean extraction.")
asset("G09", "photo-remove", (132, 672, 165, 705), "source_icon_with_overlay",
      "Circular X contains photographic matte at corners; mask or clean extraction needed.")
asset("G09", "photo-add", (396, 720, 429, 757))

if __name__ == "__main__":
    build(ROOT, text, controls, crops, titles, samples, extras)
    plan = {
        "schemaVersion": "1.0.0",
        "scope": "G01-G09 original-reference component planning only; no Figma edits",
        "designInterpretation": "面向个人生活与健康记录用户的向往、问题、人生清单及足迹页面；轻量浅色生活记录视觉，绿色操作强调，原图大标题/列表/表单各不相同。DESIGN_VARIANCE 2 / MOTION_INTENSITY 1 / VISUAL_DENSITY 5。",
        "statusRules": {
            "measured": "Visible source composition and strings",
            "inferred": "Suggested component boundaries, layout behaviors and properties",
            "unknown": "Source font metadata, unshown states, real safe insets and app constraints",
        },
        "sourceAuthority": "Each original G PNG is authoritative for the strict reproduction. Product reviewNotes must be represented as a separate labeled revision, not silently substituted.",
        "libraryPage": {"name": "02｜组件库与素材", "id": "75:2", "status": "inferred", "note": "Inherited from parent task, must verify file/page before use."},
        "fileKey": {"value": "ptA7IsUhV0rHsp8yRLFRVj", "status": "inferred", "note": "Parent-provided target identity, not queried by analysis agent"},
        "masters": [
            {"name": "区域 / 问题目录页头", "screens": ["G01"], "properties": ["TEXT:标题", "INSTANCE_SWAP:帮助图标"], "status": "inferred"},
            {"name": "控件 / 三项回答筛选", "screens": ["G01"], "properties": ["TEXT:选项", "VARIANT:全部/未答/已答"], "layout": "horizontal auto-layout within measured fixed track", "status": "inferred"},
            {"name": "列表项 / 问题", "screens": ["G01"], "properties": ["TEXT:问题", "TEXT:状态", "INSTANCE_SWAP:图标", "VARIANT:已答/未答"], "layout": "horizontal auto-layout; icon natural size; fixed pill; text fills remaining width", "status": "inferred"},
            {"name": "区域 / 问题分组标题", "screens": ["G01"], "properties": ["TEXT:标题", "TEXT:数量"], "status": "inferred"},
            {"name": "区域 / 底部导航 G01", "screens": ["G01"], "properties": ["TEXT:标签", "INSTANCE_SWAP:每项图标", "VARIANT:向往选中"], "note": "G08 uses different icons and spacing; do not force identical visuals.", "status": "inferred"},
            {"name": "区域 / 当前问题上下文", "screens": ["G02", "G03"], "properties": ["TEXT:问题", "TEXT:说明"], "note": "Separate appearance variants; G02 is unframed and G03 has subtle surface.", "status": "inferred"},
            {"name": "列表项 / 历次回答", "screens": ["G02"], "properties": ["TEXT:日期", "TEXT:回答"], "layout": "vertical auto-layout, divider outside text flow", "status": "inferred"},
            {"name": "区域 / 简洁编辑页头", "screens": ["G03", "G04", "G05"], "properties": ["TEXT:标题", "TEXT:右侧操作", "INSTANCE_SWAP:返回", "BOOLEAN:添加图标"], "status": "inferred"},
            {"name": "控件 / 多行编辑器", "screens": ["G03", "G04", "G07", "G09"], "properties": ["TEXT:内容", "TEXT:计数", "BOOLEAN:计数"], "note": "Measured fixed height per variant; do not invent common 500-character limit.", "status": "inferred"},
            {"name": "控件 / 标签输入字段", "screens": ["G04", "G06", "G09"], "properties": ["TEXT:标签", "TEXT:数值", "INSTANCE_SWAP:尾部图标", "BOOLEAN:尾部图标"], "layout": "vertical auto-layout label then fixed input", "status": "inferred"},
            {"name": "区域 / 双按钮横排", "screens": ["G03", "G04"], "properties": ["TEXT:主操作", "TEXT:次操作"], "status": "inferred"},
            {"name": "区域 / 分类切换", "screens": ["G05"], "properties": ["TEXT:三项分类", "VARIANT:旅行"], "status": "inferred"},
            {"name": "卡片 / 清单完成统计", "screens": ["G05"], "properties": ["TEXT:数量", "TEXT:标签", "INSTANCE_SWAP:状态图标"], "status": "inferred"},
            {"name": "列表项 / 人生清单", "screens": ["G05"], "properties": ["TEXT:项目", "TEXT:状态", "TEXT:完成感受", "BOOLEAN:完成感受", "INSTANCE_SWAP:状态图标"], "layout": "vertical row+optional feeling; horizontal row uses fixed icons and state pill", "status": "inferred"},
            {"name": "区域 / 大标题页头", "screens": ["G06", "G07"], "properties": ["TEXT:标题", "INSTANCE_SWAP:返回", "BOOLEAN:删除"], "status": "inferred"},
            {"name": "区域 / 保存取消纵排", "screens": ["G06", "G07"], "properties": ["TEXT:主操作", "TEXT:次操作"], "status": "inferred"},
            {"name": "区域 / 关联清单项目", "screens": ["G07"], "properties": ["TEXT:项目", "INSTANCE_SWAP:图标"], "status": "inferred"},
            {"name": "控件 / 可移除照片", "screens": ["G07", "G09"], "properties": ["INSTANCE_SWAP:照片", "INSTANCE_SWAP:移除图标", "BOOLEAN:可移除"], "note": "Source thumbnails contain baked X buttons. Clean image first; never double-render/remove-control overlay.", "status": "inferred"},
            {"name": "控件 / 添加照片", "screens": ["G07", "G09"], "properties": ["INSTANCE_SWAP:加号"], "status": "inferred"},
            {"name": "区域 / 照片编辑行", "screens": ["G07", "G09"], "properties": ["TEXT:照片数量", "INSTANCE_SWAP:照片1", "INSTANCE_SWAP:照片2"], "layout": "horizontal auto-layout for photos, natural ratio per measured source variant", "status": "inferred"},
            {"name": "区域 / 足迹页头与分区", "screens": ["G08"], "properties": ["TEXT:标题", "TEXT:说明", "VARIANT:足迹"], "status": "inferred"},
            {"name": "卡片 / 生活足迹", "screens": ["G08"], "properties": ["TEXT:日期", "TEXT:标题", "TEXT:地点", "TEXT:正文", "INSTANCE_SWAP:照片"], "layout": "vertical card; content row text+image; actions top-right; use native text and border", "status": "inferred"},
            {"name": "区域 / 底部导航 G08", "screens": ["G08"], "properties": ["TEXT:标签", "INSTANCE_SWAP:每项图标", "VARIANT:向往选中"], "status": "inferred"},
            {"name": "区域 / 足迹编辑页头", "screens": ["G09"], "properties": ["TEXT:标题", "INSTANCE_SWAP:返回"], "status": "inferred"},
            {"name": "区域 / 足迹编辑操作", "screens": ["G09"], "properties": ["TEXT:保存", "TEXT:取消"], "status": "inferred"},
        ],
        "assemblyRules": [
            "All meaningful screen regions are component instances; masters arranged explicitly on library page.",
            "Use original source-local 512x1024 coordinates; do not resize artwork to normalized square slots.",
            "Do not use full-screen source image as visible UI background.",
            "Text remains editable, including dates/status/labels/numbers; source photos may contain incidental printed text.",
            "Reference-code labels G01-G05 are part of original raster. Preserve in strict-reproduction frame; omit only in separately labeled production revision.",
            "G01 and G08 bottom navigation look different in source; do not silently normalize them.",
            "All account content shown is example content, never preseed a new account.",
            "No generated image requested or used by this analysis agent; assets are plans for exact source extraction.",
        ],
        "acceptance": {
            "status": "not_started",
            "required": [
                "Verify target file/page IDs before writing.",
                "Clean overlay-baked thumbnails and verify isolated asset boundaries.",
                "Export every screen at512x1024, compare against original with at least two evidence-backed repair passes.",
                "Disable all full-reference images during final screenshot.",
                "Test text override and asset swap in disposable clone.",
                "Record real Figma master/instance/screen IDs and exact screenshot paths.",
            ],
        },
    }
    out = ROOT / "component-plan.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(out), out.stat().st_size)
