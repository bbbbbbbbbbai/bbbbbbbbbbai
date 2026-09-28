from pathlib import Path
from hashlib import sha256
from datetime import datetime
import json
from PIL import Image, ImageStat

ROOT=Path(__file__).parent
SOURCE=ROOT.parent.parent/"screens"
MANIFEST=ROOT.parent.parent/"manifest.json"
ROOT.mkdir(parents=True,exist_ok=True)


def ev(value,status,source):
    return {"value":value,"status":status,"source":source}


def m(value,source="Original source PNG; native-pixel observation, approximate edge tolerance1-2px"):
    return ev(value,"measured",source)


def i(value,source="Candidate inferred from original raster; not original editable metadata"):
    return ev(value,"inferred",source)


def u(source):
    return ev(None,"unknown",source)


# id,text, editing-box candidate XYWH, font size candidate, font weight,
# white text, horizontal alignment. Visible-ink XYWH is measured separately.
TEXT={
"H01":[
("time","9:41",[25,10,61,26],18,400,False,"LEFT"),
("battery","100%",[438,10,62,27],18,400,False,"LEFT"),
("title","我的",[171,58,170,38],25,700,False,"CENTER"),
("avatar-initial","老",[29,155,130,84],54,700,False,"CENTER"),
("name","老白",[185,143,220,39],29,700,False,"LEFT"),
("email","la***@example.com",[185,185,295,31],20,400,False,"LEFT"),
("sync-state","已同步",[216,229,220,31],20,500,False,"LEFT"),
("sync-confirmed-at","上次确认：2026年9月26日 20:14",[185,260,302,31],18,400,False,"LEFT"),
("menu-profile","个人资料",[84,345,340,35],21,400,False,"LEFT"),
("menu-goals","目标设置",[84,419,340,35],21,400,False,"LEFT"),
("menu-sync","同步状态",[84,492,340,35],21,400,False,"LEFT"),
("menu-backup","备份与恢复",[84,566,340,35],21,400,False,"LEFT"),
("menu-clear","清空个人数据",[84,640,340,35],21,400,False,"LEFT"),
("menu-logout","退出登录",[84,741,340,35],21,400,False,"LEFT"),
("nav-today","今日",[25,940,77,31],18,400,False,"CENTER"),
("nav-record","记录",[153,940,77,31],18,400,False,"CENTER"),
("nav-aspiration","向往",[282,940,77,31],18,400,False,"CENTER"),
("nav-profile","我的",[411,940,77,31],18,500,False,"CENTER"),
],
"H02":[
("time","9:41",[25,10,61,26],18,400,False,"LEFT"),
("battery","100%",[438,10,62,27],18,400,False,"LEFT"),
("title","编辑个人资料",[120,58,272,38],25,700,False,"CENTER"),
("nickname-label","昵称",[26,131,220,32],19,400,False,"LEFT"),
("nickname-value","老白",[45,179,380,36],23,400,False,"LEFT"),
("gender-label","性别",[26,246,220,33],20,400,False,"LEFT"),
("gender-man","男",[96,296,61,31],22,400,False,"LEFT"),
("gender-woman","女",[257,296,62,31],22,400,False,"LEFT"),
("gender-other","其他",[412,296,62,31],22,400,False,"LEFT"),
("height-label","身高（厘米）",[26,367,276,33],20,400,False,"LEFT"),
("height-value","175",[45,414,380,37],23,400,False,"LEFT"),
("age-label","年龄（岁）",[26,486,276,33],20,400,False,"LEFT"),
("age-value","28",[45,532,380,37],23,400,False,"LEFT"),
("activity-label","活动水平",[26,607,276,34],20,400,False,"LEFT"),
("activity-value","中等",[45,655,350,37],23,400,False,"LEFT"),
("save","保存",[190,868,132,37],23,500,True,"CENTER"),
],
"H03":[
("time","9:41",[25,6,61,26],18,400,False,"LEFT"),
("battery","100%",[422,6,71,26],18,400,False,"LEFT"),
("screen-code","H03",[88,39,95,23],14,400,False,"LEFT"),
("title","目标与热量设置",[88,61,359,38],26,700,False,"LEFT"),
("start-label","起始体重",[25,139,94,34],22,700,False,"LEFT"),
("start-label-unit","（kg）",[119,141,96,33],20,400,False,"LEFT"),
("start-value","68.0",[301,139,142,35],23,400,False,"LEFT"),
("start-unit","kg",[463,141,38,33],20,400,False,"LEFT"),
("current-label","当前体重",[25,217,94,34],22,700,False,"LEFT"),
("current-label-unit","（kg）",[119,219,96,33],20,400,False,"LEFT"),
("current-value","65.8",[301,216,142,35],23,400,False,"LEFT"),
("current-unit","kg",[463,218,38,33],20,400,False,"LEFT"),
("target-label","目标体重",[25,295,94,34],22,700,False,"LEFT"),
("target-label-unit","（kg）",[119,297,96,33],20,400,False,"LEFT"),
("target-value","62.0",[301,294,142,35],23,400,False,"LEFT"),
("target-unit","kg",[463,296,38,33],20,400,False,"LEFT"),
("change-label","变化目标",[25,375,168,35],22,700,False,"LEFT"),
("change-period","每周",[225,375,56,35],21,400,False,"LEFT"),
("change-value","-0.5",[343,376,95,35],23,400,False,"LEFT"),
("change-unit","kg",[463,378,38,33],20,400,False,"LEFT"),
("mode-auto","自动热量",[25,474,232,36],22,700,True,"CENTER"),
("mode-manual","手动热量",[257,474,231,36],22,700,False,"CENTER"),
("auto-title","自动热量",[25,545,333,35],23,700,False,"LEFT"),
("auto-description","根据目标变化与记录估算每日热量范围",[25,582,445,31],18,400,False,"LEFT"),
("daily","每日",[25,630,55,35],22,400,False,"LEFT"),
("auto-calories","1,850",[76,611,112,65],46,700,False,"LEFT"),
("auto-calories-unit","kcal",[192,632,106,38],26,400,False,"LEFT"),
("manual-title","手动热量",[25,717,333,35],23,700,False,"LEFT"),
("manual-description","切换为手动热量后，可输入每日热量",[25,753,438,31],18,400,False,"LEFT"),
("manual-placeholder","例如 1800",[43,806,312,38],22,400,False,"LEFT"),
("manual-unit","kcal",[431,807,56,35],20,400,False,"LEFT"),
("save","保存设置",[137,908,239,39],24,700,True,"CENTER"),
],
"H04":[
("time","9:41",[25,6,61,26],18,400,False,"LEFT"),
("battery","100%",[422,6,71,26],18,400,False,"LEFT"),
("screen-code","H04",[88,39,95,23],14,400,False,"LEFT"),
("title","同步详情与恢复入口",[88,61,391,38],26,700,False,"LEFT"),
("hero-state","等待",[124,132,343,41],29,700,False,"LEFT"),
("hero-pending","有 3 条记录等待同步",[124,171,343,34],21,400,False,"LEFT"),
("hero-offline","离线记录 3 条，尚未上传",[124,207,343,32],18,400,False,"LEFT"),
("status-heading","同步状态说明",[25,270,430,34],20,700,False,"LEFT"),
("status-synced","已同步",[90,317,125,31],18,700,False,"LEFT"),
("status-synced-description","记录已成功上传",[226,319,261,30],17,400,False,"LEFT"),
("status-waiting","等待",[90,361,125,31],18,700,False,"LEFT"),
("status-waiting-description","有记录等待同步",[226,363,261,30],17,400,False,"LEFT"),
("status-offline","离线",[90,408,125,31],18,700,False,"LEFT"),
("status-offline-description","在离线状态下的本地记录",[226,410,261,30],17,400,False,"LEFT"),
("status-failed","失败",[90,455,125,31],18,700,False,"LEFT"),
("status-failed-description","同步失败，需重试",[226,457,261,30],17,400,False,"LEFT"),
("status-signin","需登录",[90,503,125,31],18,700,False,"LEFT"),
("status-signin-description","未登录，无法同步",[226,505,261,30],17,400,False,"LEFT"),
("confirmed-heading","最近确认同步",[24,560,445,34],21,700,False,"LEFT"),
("confirmed-date","2025年06月18日 09:42",[24,594,460,31],21,400,False,"LEFT"),
("confirmed-description","已确认同步（不包含当前待上传的记录）",[24,622,460,32],18,400,False,"LEFT"),
("pending-label","待处理",[24,683,367,33],21,700,False,"LEFT"),
("pending-count","3 条",[449,683,43,33],21,400,False,"LEFT"),
("offline-label","离线记录",[24,742,367,33],21,700,False,"LEFT"),
("offline-count","3 条",[449,742,43,33],21,400,False,"LEFT"),
("retry","重试同步",[139,805,234,37],23,500,True,"CENTER"),
("return-login","返回登录",[176,866,160,34],21,400,False,"CENTER"),
("footnote","普通记录会在联网后自动同步；备份与恢复请在备份页面操作",[67,927,417,31],15.5,400,False,"LEFT"),
],
"H05":[
("time","9:41",[25,6,61,26],18,400,False,"LEFT"),
("battery","100%",[422,6,71,26],18,400,False,"LEFT"),
("screen-code","H05",[88,39,95,23],14,400,False,"LEFT"),
("title","备份与恢复",[88,61,359,38],26,700,False,"LEFT"),
("export-heading","导出备份",[24,130,452,36],23,700,False,"LEFT"),
("export-description","导出为本地文件，可选操作，不影响日常自动同步",[24,165,464,32],18,400,False,"LEFT"),
("export-button","导出记录",[235,221,162,39],24,700,True,"LEFT"),
("import-heading","导入恢复",[24,313,452,36],23,700,False,"LEFT"),
("import-description","从本地备份文件导入，恢复您的数据",[24,348,464,32],18,400,False,"LEFT"),
("select-file","选取文件",[240,405,161,39],23,700,False,"LEFT"),
("preview-heading","导入预览",[43,489,417,34],21,700,False,"LEFT"),
("preview-file","laobai_backup_2025-06-18.json",[43,522,417,33],19,400,False,"LEFT"),
("preview-diaries","日记记录",[43,564,307,32],20,400,False,"LEFT"),
("preview-diaries-count","24 条",[423,564,47,32],20,400,False,"LEFT"),
("preview-goals","目标设置",[43,602,307,32],20,400,False,"LEFT"),
("preview-goals-count","1 条",[435,602,35,32],20,400,False,"LEFT"),
("preview-exercise","运动记录",[43,640,307,32],20,400,False,"LEFT"),
("preview-exercise-count","18 条",[423,640,47,32],20,400,False,"LEFT"),
("warning","导入将覆盖当前同类数据",[73,705,404,33],20,700,False,"LEFT"),
("confirm-scope","我已确认覆盖范围",[65,757,408,33],19,400,False,"LEFT"),
("confirm-import","确认导入",[135,810,244,38],23,500,False,"CENTER"),
("cancel","取消",[177,872,158,34],22,400,False,"CENTER"),
("footnote","备份与恢复是可选操作，不影响日常的自动同步。",[67,937,414,31],16,400,False,"LEFT"),
],
}

# id,type,source visible rectangle XYWH,radius/stroke candidate,visible state
RECTS={
"H01":[
("avatar","ellipse",[29,131,130,130],65,0,"placeholder"),
("profile-divider","line",[28,314,456,1],0,0,""),
("menu-divider-1","line",[28,397,456,1],0,0,""),
("menu-divider-2","line",[28,471,456,1],0,0,""),
("menu-divider-3","line",[28,544,456,1],0,0,""),
("menu-divider-4","line",[28,618,456,1],0,0,""),
("menu-divider-5","line",[28,704,456,1],0,0,""),
("nav-divider","line",[0,891,512,1],0,0,""),
("gesture","rect",[169,998,174,7],4,0,""),
],
"H02":[
("nickname-input","rect",[27,166,459,56],9,1,"filled"),
("gender-man","rect",[26,282,141,54],8,1,"selected"),
("gender-woman","rect",[187,282,142,54],8,1,"default"),
("gender-other","rect",[346,282,141,54],8,1,"default"),
("radio-man-outer","ellipse",[48,300,19,19],10,0,"selected"),
("radio-man-inner","ellipse",[54,306,7,7],4,0,"selected"),
("radio-woman","ellipse",[211,301,17,17],9,2,"unselected"),
("radio-other","ellipse",[370,301,17,17],9,2,"unselected"),
("height-input","rect",[27,402,459,56],8,1,"filled"),
("age-input","rect",[27,520,459,56],8,1,"filled"),
("activity-input","rect",[27,643,459,56],8,1,"filled"),
("save","rect",[27,855,459,59],14,0,""),
("gesture","rect",[169,998,174,7],4,0,""),
],
"H03":[
("start-input","rect",[286,132,164,48],6,1,"filled"),
("start-divider","line",[25,194,463,1],0,0,""),
("current-input","rect",[286,209,164,48],6,1,"filled"),
("current-divider","line",[25,271,463,1],0,0,""),
("target-input","rect",[286,287,164,48],6,1,"filled"),
("target-divider","line",[25,350,463,1],0,0,""),
("change-input","rect",[208,366,242,51],6,1,"filled"),
("change-divider","line",[322,366,1,51],0,0,""),
("change-section-divider","line",[25,441,463,1],0,0,""),
("mode-shell","rect",[25,463,463,56],9,0,""),
("mode-auto","rect",[25,464,232,53],8,0,"selected"),
("auto-section-divider","line",[25,694,463,1],0,0,""),
("manual-input","rect",[25,792,461,59],6,1,"disabled"),
("save","rect",[25,891,463,67],12,0,""),
("gesture","rect",[185,1003,142,6],3,0,""),
],
"H04":[
("hero-waiting","rect",[22,114,468,140],10,0,"waiting"),
("status-heading-divider","line",[24,308,464,1],0,0,""),
("waiting-row","rect",[23,355,466,44],7,0,"selected"),
("offline-divider","line",[24,447,464,1],0,0,""),
("failed-divider","line",[24,494,464,1],0,0,""),
("signin-divider","line",[24,547,464,1],0,0,""),
("confirmed-divider","line",[24,666,464,1],0,0,""),
("pending-divider","line",[24,726,464,1],0,0,""),
("retry","rect",[24,791,464,59],9,0,""),
("info","rect",[24,913,465,55],8,0,""),
("gesture","rect",[185,1003,142,6],3,0,""),
],
"H05":[
("export","rect",[24,208,464,60],8,0,""),
("export-divider","line",[24,292,464,1],0,0,""),
("select-file","rect",[24,393,464,59],7,1,""),
("preview","rect",[24,475,464,202],10,0,"file-selected"),
("preview-table","rect",[25,559,462,118],8,1,""),
("preview-divider-1","line",[43,598,425,1],0,0,""),
("preview-divider-2","line",[43,636,425,1],0,0,""),
("warning","rect",[24,695,464,50],10,0,""),
("confirmation-checkbox","rect",[28,761,24,24],3,2,"unchecked"),
("confirm-import","rect",[24,799,464,56],8,0,"disabled"),
("info","rect",[24,925,464,52],8,0,""),
("gesture","rect",[185,1003,142,6],3,0,""),
],
}

# These are pixel-crop plans, not original vectors. No photos exist in these pages.
ASSETS=[
("status-warm","H01",[364,12,433,35],"icon","No100% text in this crop."),
("synced-check-small","H01",[184,230,210,257],"icon",""),
("profile-menu","H01",[28,345,60,381],"icon",""),
("goals-menu","H01",[26,417,62,454],"icon",""),
("sync-menu","H01",[24,492,64,525],"icon",""),
("backup-menu","H01",[27,564,61,601],"icon",""),
("clear-menu","H01",[28,639,61,675],"icon",""),
("logout-menu","H01",[26,737,64,776],"icon",""),
("menu-chevron","H01",[469,351,487,376],"icon","Reuse a master at measured row positions; original occurrences may differ slightly."),
("nav-today","H01",[45,903,83,939],"icon",""),
("nav-record","H01",[175,902,209,939],"icon",""),
("nav-aspiration","H01",[301,902,342,940],"icon",""),
("nav-profile-selected","H01",[433,902,468,940],"icon",""),
("back-warm","H02",[24,61,56,94],"icon",""),
("activity-chevron","H02",[445,661,469,685],"icon",""),
("status-cool","H03",[337,5,418,33],"icon","Separate from warm-page status artwork."),
("back-cool","H03",[21,61,55,94],"icon","H04/H05 candidate reuse; verify occurrence size."),
("more","H03",[468,62,490,96],"icon","Shared H03/H05 master candidate."),
("period-chevron","H03",[280,384,298,400],"icon",""),
("auto-information","H03",[453,545,486,579],"icon","Outline information mark differs from filled footer icons."),
("manual-chevron","H03",[466,730,485,756],"icon",""),
("waiting-clock-large","H04",[42,143,97,198],"icon","Original pixel artwork, not assumed vector."),
("status-synced","H04",[34,317,67,350],"icon",""),
("status-waiting","H04",[33,361,67,394],"icon",""),
("status-offline","H04",[31,407,68,441],"icon",""),
("status-failed","H04",[32,454,67,488],"icon",""),
("status-signin","H04",[34,502,67,537],"icon",""),
("info-footer-sync","H04",[29,925,60,958],"icon","Light-blue matte must be preserved or cleaned."),
("export-download","H05",[186,219,220,256],"icon","White glyph on green matte; keep the button background separate."),
("select-folder","H05",[190,407,226,440],"icon",""),
("import-warning","H05",[34,704,67,737],"icon","Keep independent from warning copy."),
("info-footer-backup","H05",[29,935,60,968],"icon","Similar to H04 footer but source crop separate; verify before reuse."),
]

TITLES={"H01":"我的","H02":"编辑个人资料","H03":"目标与热量设置","H04":"同步详情与恢复入口","H05":"备份与恢复"}


def text_measure(image,box,light):
    x,y,w,h=box
    area=image.crop((x,y,x+w,y+h)).convert("RGB")
    values=list(area.getdata())
    selected=[p for p in values if min(p)>215] if light else [p for p in values if min(p)<190]
    mask=Image.new("L",area.size)
    mask.putdata([255 if (min(p)>215 if light else min(p)<190) else 0 for p in values])
    b=mask.getbbox()
    ink=[x+b[0],y+b[1],b[2]-b[0],b[3]-b[1]] if b else [None]*4
    color=[sorted(p[c] for p in selected)[len(selected)//2] for c in range(3)] if selected else None
    return ink,color


manifest=json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
source_pages={p["id"]:p for p in manifest["pages"] if p["id"] in TEXT}
spec={
 "schemaVersion":"1.0.0","createdAt":datetime.now().astimezone().isoformat(),
 "scope":"H01-H05 original-source analysis only; no Figma creation or modification",
 "coordinateSystem":"Original screen-local pixels,512x1024. Boxes XYWH; crops LTRB exclusive end.",
 "geometryMeaning":"Text x/y/w/h are thresholded visible-ink bounds, not editable text-box metadata. textBoxCandidate is inferred.",
 "fontPolicy":{"actualFamily":u("Raster generator did not provide actual font metadata"),"candidateFamily":i("Noto Sans SC; calibrate original glyph metrics rather than trusting fallback")},
 "fieldStatusRules":{
  "text":{"measured":["text","x","y","w","h","inkMedianRGB"],"inferred":["textBoxCandidate","fontSizeCandidate","fontWeightCandidate","lineHeightCandidate","letterSpacingCandidate","textAlignCandidate","colorRole"]},
  "controls":{"measured":["x","y","w","h"],"inferred":["radiusCandidate","strokeCandidate","visibleState"]},
  "source":"Original PNG. Manually measured edge tolerance1-2px. Text ink threshold within candidate ROI may include outlines; original baseline/font unknown."
 },
 "screens":[]
}
assets={
 "schemaVersion":"1.0.0","scope":"source asset planning only; crop files not generated",
 "sources":{},
 "fieldStatusRules":{
  "measured":["sourceScreen","cropLTRB","pixelSize","classification","sourcePixelSHA256","vector","fileCreated"],
  "inferred":["plannedFile","status","componentRule"],"unknown":["alpha"],
  "source":"sourceScreen resolves through sources. Crops native pixel size; source text outside artwork must remain editable."
 },
 "componentRule":i("Use independent bitmap artwork masters at native pixel size inside fixed shells. Repeated icons use instances; no claim of original vector source."),
 "assets":[]
}

for code,rows in TEXT.items():
    path=SOURCE/f"{code}.png"
    image=Image.open(path).convert("RGB")
    assert image.size==(512,1024)
    digest=sha256(path.read_bytes()).hexdigest()
    assets["sources"][code]={"path":str(path),"sha256":digest,"status":"measured"}
    texts=[]
    for key,content,box,size,weight,light,align in rows:
        ink,color=text_measure(image,box,light)
        texts.append({
            "id":key,"text":content,"x":ink[0],"y":ink[1],"w":ink[2],"h":ink[3],
            "geometryStatus":"measured" if ink[0] is not None else "unknown",
            "inkMedianRGB":color,"textBoxCandidate":box,
            "fontSizeCandidate":size,"fontWeightCandidate":weight,
            "lineHeightCandidate":round(size*1.4,1),"letterSpacingCandidate":0,
            "textAlignCandidate":align,
            "colorRole":"white" if light else "source_ink_sample",
        })
    sample_rois={
      "background":[310,942,350,978] if code=="H02" else ([210,800,270,848] if code=="H01" else [320,978,360,994]),
      "primary_ink":[233,64,255,86] if code=="H01" else ([187,65,213,84] if code=="H02" else [89,69,117,88]),
      "accent":[190,235,206,251] if code=="H01" else ([39,869,135,899] if code=="H02" else ([38,478,83,506] if code=="H03" else ([40,807,126,832] if code=="H04" else [39,222,135,250]))),
    }
    if code in {"H04","H05"}:
        sample_rois["danger_surface"]=[35,119,77,135] if code=="H04" else [270,702,454,732]
        sample_rois["information_surface"]=[352,917,480,925] if code=="H04" else [352,928,480,937]
    if code=="H02":
        sample_rois["selected_surface"]=[78,287,130,296]
    colors={}
    for role,roi in sample_rois.items():
        part=image.crop(roi)
        stat=ImageStat.Stat(part)
        pixels=list(part.getdata())
        if role=="accent":
            pixels=[p for p in pixels if p[1]-p[0]>30 and p[1]-p[2]>5]
        elif role=="primary_ink":
            pixels=[p for p in pixels if max(p)<140]
        colors[role]={
          "roiLTRB":m(roi,"source sampling coordinates"),
          "meanRGB":m([round(v,2) for v in stat.mean],"Pillow source ROI mean"),
          "stddevRGB":m([round(v,2) for v in stat.stddev],"Pillow source ROI variation"),
          "filteredMedianRGB":m([sorted(p[c] for p in pixels)[len(pixels)//2] for c in range(3)] if pixels else None,"Accent filtered green; primary filtered dark; other roles unfiltered"),
        }
    item={
      "id":code,"title":m(TITLES[code],"original visible title"),
      "manifestName":m(source_pages[code]["name"],"manifest.json"),
      "sourceFile":str(path),"sourceSHA256":digest,
      "width":512,"height":1024,"dimensionStatus":"measured",
      "background":colors["background"],"colors":colors,"text":texts,
      "controls":[{"id":name,"type":kind,"x":box[0],"y":box[1],"w":box[2],"h":box[3],
                  "geometryStatus":"measured","radiusCandidate":radius,"strokeCandidate":stroke,"visibleState":state}
                 for name,kind,box,radius,stroke,state in RECTS[code]],
      "assets":[name for name,src,*_ in ASSETS if src==code],
      "reviewNotes":m(source_pages[code]["reviewNotes"],"manifest.json"),
      "dataBoundary":m(source_pages[code]["dataBoundary"],"manifest.json"),
      "trueDeviceSafeInset":u("Concept screenshot, no verified device metadata"),
    }
    if code=="H01":
        item["menuRows"]=m([
            {"name":"个人资料","box":[28,315,456,82],"icon":[28,345],"textX":84,"chevron":[469,351]},
            {"name":"目标设置","box":[28,398,456,73],"icon":[26,417],"textX":84,"chevron":[469,425]},
            {"name":"同步状态","box":[28,472,456,72],"icon":[24,492],"textX":84,"chevron":[469,498]},
            {"name":"备份与恢复","box":[28,545,456,73],"icon":[27,564],"textX":84,"chevron":[469,572]},
            {"name":"清空个人数据","box":[28,619,456,85],"icon":[28,639],"textX":84,"chevron":[469,646]},
            {"name":"退出登录","box":[28,705,456,102],"icon":[26,737],"textX":84,"chevron":None},
        ])
        item["avatarPolicy"]=i("130px editable ellipse plus editable 老 text. No actual portrait photo; do not substitute a stock avatar. Any original soft texture must be separate from text.")
        item["bottomNavigation"]=m({"band":[0,891,512,90],"centersX":[64,192,321,450],"selected":"我的","labels":["今日","记录","向往","我的"]},"source-visible geometry/state")
    if code=="H02":
        item["genderOptions"]=m(["男","女","其他"],"source screenshot")
        item["selectedGender"]=m("男","source screenshot")
        item["activityOptions"]=u("Only 中等 is visible. Do not invent hidden dropdown options from raster.")
    if code=="H03":
        item["visibleMode"]=m("自动热量 selected, manual section and disabled-looking manual input also visible","source screenshot")
        item["implementationConstraint"]=m("自动/手动模式应只显示对应输入；每周变化的正负语义以业务定义统一。","manifest reviewNotes")
        item["exampleDataPolicy"]=i("68.0/65.8/62.0/-0.5/1,850 are visual example values; not personal data or a verified nutrition recommendation.")
    if code=="H04":
        item["sourceVisibleStates"]=m(["已同步","等待","离线","失败","需登录"],"source status-explanation table")
        item["currentState"]=m({"state":"等待","pending":3,"offline":3},"source hero/counters; counts may overlap, do not sum without business rules")
        item["implementationConstraint"]=m("同步详情展示当前状态；参考图列举的其他状态应移至状态板，不堆成说明表。","manifest reviewNotes")
    if code=="H05":
        item["sourceState"]=m({"fileSelected":True,"checkboxChecked":False,"confirmImportEnabled":False,"preview":{"日记记录":24,"目标设置":1,"运动记录":18}},"original visible state; example backup only")
        item["implementationConstraint"]=m("导入预览的替换范围必须与实际导入策略一致；危险操作只在明确确认后执行。","manifest reviewNotes")
        item["noOperationPerformed"]=m("No file selected, export, import or overwrite executed. This is source-only analysis.","tool log")
    spec["screens"].append(item)

for name,code,crop,kind,note in ASSETS:
    image=Image.open(SOURCE/f"{code}.png").convert("RGB").crop(crop)
    assets["assets"].append({
      "id":name,"sourceScreen":code,"cropLTRB":crop,
      "pixelSize":[crop[2]-crop[0],crop[3]-crop[1]],
      "plannedFile":str(ROOT/"assets"/f"{name}.png"),"fileCreated":False,
      "classification":kind,"sourcePixelSHA256":sha256(image.tobytes()).hexdigest(),
      "vector":False,"alpha":u("Flattened original; source matte or transparency must be explicitly handled."),
      "status":"needs_matte_review" if "matte" in note else "ready_for_exact_crop","notes":note,
    })
assets["sharedMasterCandidates"]=i({
 "H01":["menu-chevron","synced-check-small"],"H01-H02":["status-warm"],
 "H03-H05":["status-cool","back-cool","more"],
 "verifyBeforeReuse":["info-footer-sync vs info-footer-backup","status-failed vs import-warning"],
 "keepDistinct":["warm/cool status families","outline auto-information vs filled footer information","profile avatar initial remains text, not bitmap"],
})
assets["photoCount"]=m(0,"all five original screenshots; no photographs")
assets["structuralNativeControls"]=i("Keep circles/radio dots/checkbox/fields/segments/dividers/typography native. Crop-based artwork and handwritten icon shape pixels are not source vectors.")
for name,payload in [("source-spec.json",spec),("asset-manifest.json",assets)]:
    destination=ROOT/name
    destination.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    json.loads(destination.read_text(encoding="utf-8"))
    print(name,destination.stat().st_size)
print("pages",len(spec["screens"]),"texts",sum(len(s["text"]) for s in spec["screens"]),"controls",sum(len(s["controls"]) for s in spec["screens"]),"assets",len(assets["assets"]))
