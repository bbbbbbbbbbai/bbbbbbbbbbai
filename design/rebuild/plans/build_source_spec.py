from pathlib import Path
import sys
import json
sys.path.insert(0,str(Path(__file__).parent.parent))
from source_spec_common_readonly import build, measured as m, inferred as i, unknown as u

ROOT=Path(__file__).parent
TEXT={f"G{n:02}":[] for n in range(1,10)}


def t(code,key,text,box,size=20,weight=400,light=False,align="LEFT"):
    TEXT[code].append((key,text,box,size,weight,light,align))


for code,label,title in [
("G01","G01 问题目录","问题目录"),("G02","G02 问题与历次回答","问题与历次回答"),
("G03","G03 写下回答","写下回答"),("G04","G04 自定义问题","新增自定义问题"),("G05","G05 人生清单","人生清单")]:
    t(code,"code",label,[18,3,339,28],16)
    t(code,"time","9:41",[31,34 if code in {"G01","G02"} else 39,71,29],18)
    t(code,"battery","100%",[440 if code in {"G01","G02"} else 426,34 if code in {"G01","G02"} else 39,72,29],18)
    t(code,"title",title,[31,91,359,52] if code=="G01" else [96,91,335,48],34 if code=="G01" else 30,700)
for index,label in enumerate(["全部","未答","已答"]):
    t("G01",f"filter-{index}",label,[31+index*151,190,151,39],24,700 if index==0 else 400,index==0,"CENTER")
for key,text,box,size,weight in [
("system-heading","系统问题",[31,278,376,43],26,700),("system-count","3",[467,282,22,40],24,400),
("custom-heading","自定义问题",[31,655,376,45],26,700),("custom-count","1",[467,659,22,40],24,400),
]:
    t("G01",key,text,box,size,weight)
QUESTIONS=[
("今天最想记住什么？","已答",357,359),
("最近有什么事情让你感到期待？","未答",447,452),
("今年想培养的习惯是什么？","已答",546,548),
("我希望如何安排下一个周末？","未答",740,742),
]
for n,(question,state,by,ty) in enumerate(QUESTIONS):
    t("G01",f"question-{n}",question,[80,ty,282,37],21)
    t("G01",f"answer-state-{n}",state,[370,by+3,77,32],20,400,False,"CENTER")
for index,label in enumerate(["今日","记录","向往","我的"]):
    t("G01",f"nav-{index}",label,[index*128,941,128,35],19,500 if index==2 else 400,False,"CENTER")
for key,text,box,size,weight in [
("question-label","当前问题",[31,198,450,35],23,400),
("question","最近有什么事情让你感到期待？",[31,240,451,48],30,700),
("question-context","关于未来的期待，可以是生活、工作、学习或其他\n任何让你开心的事情。",[31,299,451,65],20.5,400),
("answers-heading","已有答案及日期",[31,424,241,44],26,700),
("history-explanation","历史答案会被完整保留，\n不会被新回答覆盖。",[280,418,202,61],19,400),
("date-1","2025年3月12日",[31,508,449,37],23,400),
("answer-1","周末去公园走走。",[31,549,449,41],24,400),
("date-2","2025年3月05日",[31,629,449,37],23,400),
("answer-2","把书架重新整理好。",[31,670,449,42],24,400),
("date-3","2025年2月21日",[31,753,449,38],23,400),
("answer-3","学会一道新菜。",[31,795,449,42],24,400),
]:
    t("G02",key,text,box,size,weight)
t("G02","continue","继续回答",[129,905,254,44],25,700,True,"CENTER")
for code in ["G03","G04"]:
    t(code,"save-top","保存",[436,91,56,41],24,500)
t("G03","question","今天，什么让你感到轻松？",[48,177,420,40],24,700)
t("G03","context","可以是一件小事、一个瞬间，或任何让你放松的东西。",[49,222,426,31],18)
t("G03","placeholder","写下你的回答…",[48,306,425,42],23)
t("G03","counter","0/500",[429,546,49,30],17)
for code,y in [("G03",625),("G04",609)]:
    t(code,"cancel","取消",[27,y,219,38],22,400,False,"CENTER")
    t(code,"save-bottom","保存",[266,y,220,38],22,500,True,"CENTER")
for key,text,box,size,weight in [
("intro-heading","编辑自定义问题",[27,160,460,33],20,700),
("intro","创建一个属于你自己的问题，用于日常记录。",[27,193,460,33],18,400),
("group-label","分组",[27,246,460,33],20,700),
("group-value","生活",[45,296,382,34],21,400),
("question-label","问题",[27,369,460,33],20,700),
("placeholder","输入你想问自己的问题…",[45,416,425,39],20,400),
("counter","0/100",[431,529,49,30],17,400),
]:
    t("G04",key,text,box,size,weight)
for key,text,box,size,weight in [
("add","添加",[443,94,50,36],21,400),("category-heading","分类",[27,166,451,35],21,700),
("system-heading","系统模板",[27,413,451,34],21,700),
("system-description","这些是内置的示例清单项，你可以参考或按自己的想法调整。",[27,443,456,31],15.5,400),
("custom-heading","自定义",[27,749,451,34],21,700),
("custom-description","你添加的个人清单项。",[27,780,451,31],16,400),
]:
    t("G05",key,text,box,size,weight)
for n,label in enumerate(["旅行","学习","生活"]):
    t("G05",f"category-{n}",label,[27+n*153,209,153,34],18,400,n==0,"CENTER")
for n,(label,value,x) in enumerate([("未开始","3",26),("进行中","1",187),("已完成","2",347)]):
    t("G05",f"state-summary-{n}",label,[x+58,284,78,32],17)
    t("G05",f"count-{n}",value,[x+58,314,31,49],34,500)
    t("G05",f"count-unit-{n}","项",[x+86,323,43,35],20)
CHECKLIST=[
("去看一次海","未开始",489,493,None),
("登上一座山","进行中",555,559,None),
("去一个从未去过的城市","已完成",620,625,"完成感受：看到了不一样的风景，心情很放松。"),
("和喜欢的人一起去旅行","已完成",829,833,"完成感受：一路上有很多开心的回忆。"),
]
for n,(label,state,by,ty,note) in enumerate(CHECKLIST):
    t("G05",f"item-{n}",label,[76,ty,288,36],21)
    t("G05",f"state-{n}",state,[369,by+4,74,31],16,400,False,"CENTER")
    if note:
        t("G05",f"feeling-{n}",note,[89,677 if n==2 else 887,390,29],16)

for code,title in [("G06","创建清单项目"),("G07","记录完成感受")]:
    t(code,"time","9:41",[27,10,65,29],18)
    t(code,"title",title,[29,117,452,57],38,700)
    t(code,"save","保存",[142,809,227,45],25,700,True,"CENTER")
    t(code,"cancel","取消",[142,893,227,44],25,500,False,"CENTER")
t("G06","item-label","项目",[29,205,448,36],21)
t("G06","item-value","每天阅读30分钟",[47,258,375,43],25,500)
t("G06","category-label","分类",[29,346,448,36],21)
t("G06","category-value","学习成长",[47,399,374,43],25,500)
t("G07","associated-item","每天阅读30分钟",[101,210,360,39],21,700)
t("G07","feeling-label","完成感受",[29,295,451,36],21)
t("G07","feeling","今天读完了《被讨厌的勇气》的一章，内容\n很有启发。放下别人的期待，专注自己的生活，\n感觉心里轻松了很多。",[48,348,420,106],22)
t("G07","counter","42/500",[410,463,62,34],18)
t("G07","photos-label","照片（2/3）",[29,527,451,37],22)

t("G08","time","9:41",[25,10,65,29],18)
t("G08","title","生活足迹",[25,58,403,52],34,700)
t("G08","subtitle","记录生活的点滴，珍藏每一段时光",[25,110,463,35],20)
for n,label in enumerate(["问题","清单","足迹"]):
    t("G08",f"section-tab-{n}",label,[16+n*166,168,158,39],22,500 if n==2 else 400,False,"CENTER")
t("G08","heading","向往",[25,235,462,46],30,700)
t("G08","description","在生活中发现美好，让日常也闪闪发光",[25,280,462,34],19)
for key,text,box,size,weight in [
("date-1","2025年4月12日　周六",[41,349,296,31],18,400),
("title-1","公园散步",[41,382,284,39],24,700),
("place-1","星河公园",[70,425,258,35],20,400),
("body-1","傍晚的公园微风很舒服，树木郁郁葱葱，\n走在湖边感觉整个人都放松下来了。",[41,467,291,63],16.5,400),
("date-2","2025年4月5日　周六",[41,599,296,31],18,400),
("title-2","周末晚餐",[41,633,284,39],24,700),
("place-2","小满餐厅",[70,675,258,35],20,400),
("body-2","和好朋友一起吃了期待很久的意面，\n聊了很多有趣的话题，简单的晚餐\n也很幸福。",[41,718,290,88],17,400),
]:
    t("G08",key,text,box,size,weight)
for n,label in enumerate(["今日","记录","向往","我的"]):
    t("G08",f"nav-{n}",label,[n*128,942,128,34],19,500 if n==2 else 400,False,"CENTER")

for key,text,box,size,weight,align in [
("time","9:41",[25,10,65,28],18,400,"LEFT"),
("battery","100%",[438,10,66,28],18,400,"LEFT"),
("title","新增足迹",[127,57,258,40],25,700,"CENTER"),
("title-label","标题",[27,120,450,34],20,400,"LEFT"),
("title-value","海边散步",[47,166,407,39],23,400,"LEFT"),
("place-label","地点",[27,229,450,34],20,400,"LEFT"),
("place-value","东岸公园",[47,276,407,39],23,400,"LEFT"),
("date-label","日期",[27,338,450,34],20,400,"LEFT"),
("date-value","2026年9月26日",[47,384,362,39],23,400,"LEFT"),
("body-label","正文",[27,447,450,34],20,400,"LEFT"),
("body","下午的海风很温柔，沿着海岸慢慢走，听着\n海浪的声音，整个人都放松了。生活或许就是\n这样，在平凡的日子里也能找到小小的幸福。",[47,494,421,106],21,400,"LEFT"),
("photos-label","照片（2/3）",[27,629,450,35],20,400,"LEFT"),
("save","保存",[143,861,226,39],23,500,"CENTER"),
("cancel","取消",[143,930,226,37],21,400,"CENTER"),
]:
    t("G09",key,text,box,size,weight,key=="save",align)

CONTROLS={
"G01":[("filter","rect",[31,179,452,58],15,0,""),("filter-selected","rect",[31,179,151,58],15,0,"全部"),
("nav-divider","line",[0,885,512,1],0,0,""),("gesture","rect",[178,1004,156,6],3,0,"")],
"G02":[("continue","rect",[31,885,451,77],13,0,"")],
"G03":[("question-context","rect",[27,157,460,112],10,0,""),
("answer","rect",[27,292,460,291],9,1,"empty"),("cancel","rect",[27,613,219,57],9,1,""),
("save","rect",[266,613,220,57],9,0,""),("gesture","rect",[178,1004,156,6],3,0,"")],
"G04":[("group","rect",[27,284,460,55],8,1,"生活"),("question","rect",[27,405,460,161],8,1,"empty"),
("cancel","rect",[27,597,219,58],9,1,""),("save","rect",[267,597,219,58],9,0,""),("gesture","rect",[178,1004,156,6],3,0,"")],
"G05":[("header-divider","line",[27,150,460,1],0,0,""),("category","rect",[27,205,460,42],8,1,""),
("category-selected","rect",[27,205,152,41],7,0,"旅行"),("category-divider","line",[333,210,1,31],0,0,""),
("summary-0","rect",[26,268,141,109],11,1,"未开始"),("summary-1","rect",[187,268,140,109],11,1,"进行中"),
("summary-2","rect",[347,268,140,109],11,1,"已完成"),
("system-divider","line",[27,397,460,1],0,0,""),("item-divider-0","line",[27,540,460,1],0,0,""),
("item-divider-1","line",[27,606,460,1],0,0,""),("feeling-system","rect",[76,666,411,45],10,0,""),
("custom-divider","line",[27,734,460,1],0,0,""),("feeling-custom","rect",[76,876,411,46],10,0,""),
("gesture","rect",[178,1004,156,6],3,0,"")],
"G06":[("item","rect",[29,244,455,67],10,1,"filled"),("category","rect",[29,382,455,68],10,1,"学习成长")],
"G07":[("associated-item","rect",[29,191,455,78],13,0,""),
("feeling","rect",[29,335,455,168],11,1,"filled"),("photo-0","rect",[29,571,149,167],10,0,""),
("photo-1","rect",[188,571,148,167],10,0,""),("photo-add","rect",[346,571,136,167],10,1,"dashed")],
"G08":[("section-tabs-divider","line",[0,216,512,1],0,0,""),("section-selected","rect",[346,213,141,3],1,0,"足迹"),
("footprint-0","rect",[17,330,477,229],12,1,""),("footprint-1","rect",[17,580,477,243],12,1,""),
("photo-0","rect",[347,396,131,141],9,0,""),("photo-1","rect",[347,647,131,153],9,0,""),
("nav-divider","line",[0,891,512,1],0,0,""),("gesture","rect",[172,998,168,8],4,0,"")],
"G09":[("title","rect",[27,156,459,55],9,1,"filled"),("place","rect",[27,265,459,54],9,1,"filled"),
("date","rect",[27,374,459,55],9,1,"filled"),("body","rect",[27,484,459,128],10,1,"filled"),
("photo-0","rect",[29,667,140,141],10,0,""),("photo-1","rect",[187,667,141,141],10,0,""),
("photo-add","rect",[345,667,141,141],10,1,"dashed"),("save","rect",[27,849,459,61],14,0,""),
("gesture","rect",[169,998,174,7],4,0,"")],
}
for n,y in enumerate([332,421,516,620,710,807]):
    CONTROLS["G01"].append((f"divider-{n}","line",[31,y,451,1],0,0,""))
for n,(_,state,y,_) in enumerate(QUESTIONS):
    CONTROLS["G01"].append((f"state-{n}","rect",[370,y,77,39],20,0,state))
for n,y in enumerate([174,396,492,614,738]):
    CONTROLS["G02"].append((f"divider-{n}","line",[31,y,451,1],0,0,""))
for n,(_,state,y,_,_) in enumerate(CHECKLIST):
    CONTROLS["G05"].append((f"state-{n}","rect",[369,y,74,37],10,0,state))
for code in ["G06","G07"]:
    CONTROLS[code].extend([("save","rect",[29,794,454,69],13,0,""),("cancel","rect",[29,878,454,69],13,0,""),
                           ("gesture","rect",[172,998,168,8],4,0,"")])

ASSETS=[
("status-soft","G01",[362,33,435,64],"icon","Preserve soft original raster; 100% text excluded."),
("help-soft","G01",[435,91,483,142],"icon",""),
("question-document","G01",[30,355,62,394],"icon","One native-sized master for repeated question rows."),
("question-chevron","G01",[465,361,484,389],"icon",""),
("nav-home-soft","G01",[49,900,89,943],"icon",""),
("nav-record-soft","G01",[175,900,211,943],"icon",""),
("nav-leaf-selected","G01",[298,899,339,944],"icon","Not interchangeable with G08 mountain mark."),
("nav-profile-soft","G01",[422,900,463,944],"icon",""),
("back-soft","G02",[27,96,59,134],"icon",""),
("status-form-soft","G03",[351,39,424,66],"icon",""),
("form-back","G03",[27,93,60,131],"icon",""),
("group-chevron","G04",[446,298,474,322],"icon",""),
("checklist-add","G05",[404,92,438,127],"icon",""),
("summary-unstarted","G05",[40,286,73,321],"icon",""),
("summary-progress","G05",[201,285,240,324],"icon",""),
("summary-done","G05",[362,285,402,324],"icon",""),
("item-unstarted","G05",[23,490,61,529],"icon",""),
("item-progress","G05",[22,554,61,594],"icon",""),
("item-done","G05",[22,620,61,661],"icon",""),
("item-more","G05",[466,492,483,522],"icon","System-template menu must not expose template deletion."),
("status-clean","G06",[375,13,472,41],"icon","No percentage in this source family."),
("back-clean","G06",[25,59,63,100],"icon",""),
("item-clear","G06",[441,263,472,295],"icon",""),
("category-chevron","G06",[444,405,472,432],"icon",""),
("delete-completion","G07",[453,59,487,100],"icon","Deletes completion record, not system template."),
("associated-book","G07",[47,209,89,250],"icon",""),
("feeling-photo-book","G07",[29,571,178,738],"photo_with_overlay","Close circle at141,578..174,611 is baked into photo. Clean underlying photo before independent close control. Printed book title is photographic content."),
("feeling-photo-openbook","G07",[188,571,336,738],"photo_with_overlay","Close circle at299,578..331,610 is baked into photo; clean extraction required."),
("photo-remove-clean","G07",[140,576,176,613],"icon","Exterior corners and photographic background need alpha extraction."),
("photo-add-clean","G07",[391,632,437,680],"icon",""),
("status-footprints","G08",[389,13,487,41],"icon",""),
("footprint-add","G08",[448,61,487,102],"icon",""),
("footprint-edit","G08",[380,347,415,383],"icon",""),
("footprint-delete","G08",[441,348,471,383],"icon",""),
("footprint-location","G08",[39,426,63,458],"icon",""),
("footprint-park","G08",[347,396,478,537],"photo","Independent source attachment; no UI overlap."),
("footprint-dinner","G08",[347,647,478,800],"photo","Independent source attachment; preserve its own131x153 framing."),
("nav-home-clean","G08",[41,902,79,942],"icon",""),
("nav-record-clean","G08",[173,903,207,943],"icon",""),
("nav-aspiration-clean","G08",[299,902,343,943],"icon",""),
("nav-profile-clean","G08",[432,902,469,943],"icon",""),
("status-warm","G09",[361,11,434,36],"icon",""),
("back-warm","G09",[24,60,56,95],"icon",""),
("footprint-calendar","G09",[442,386,471,418],"icon",""),
("footprint-seaside","G09",[29,667,169,808],"photo_with_overlay","Close button135,673..164,702 baked into photo; clean extraction before native close control."),
("footprint-sunset","G09",[187,667,328,808],"photo_with_overlay","Close button292,673..322,703 baked into photo; clean extraction before native close control."),
("photo-remove-warm","G09",[132,670,167,705],"icon",""),
("photo-add-warm","G09",[395,717,432,759],"icon",""),
]
SAMPLES={
 "G01":{"background":[236,824,355,856],"primary_ink":[34,106,94,128],"accent":[42,194,74,223],"surface":[201,184,296,190]},
 "G02":{"background":[212,845,330,866],"primary_ink":[103,106,157,129],"accent":[42,906,156,936]},
 "G03":{"background":[180,790,280,879],"primary_ink":[104,105,153,123],"accent":[280,625,321,655]},
 "G04":{"background":[180,790,280,879],"primary_ink":[103,102,151,121],"accent":[280,609,321,640]},
 "G05":{"background":[173,957,319,986],"primary_ink":[104,103,147,123],"accent":[39,215,66,235]},
 "G06":{"background":[164,648,330,712],"primary_ink":[32,137,91,159],"accent":[44,817,155,844]},
 "G07":{"background":[163,752,316,778],"primary_ink":[34,137,91,158],"accent":[44,817,155,844]},
 "G08":{"background":[202,840,335,877],"primary_ink":[28,73,86,94],"accent":[351,213,481,216]},
 "G09":{"background":[179,958,339,984],"primary_ink":[211,71,253,89],"accent":[43,869,159,893]},
}
EXTRAS={
"G01":{"missingSourceControls":u("新增自定义问题入口与问题/清单/足迹分区切换未出现在原图；位置待编排确定，不能虚构为已测得。"),
       "implementationConstraint":m("参考图遗漏新增自定义问题入口及问题/清单/足迹的分区切换，重建时必须补齐。","manifest reviewNotes")},
"G02":{"implementationConstraint":m("删去解释实现方式的历史保留说明；保留清楚的日期、内容和继续回答入口。","manifest reviewNotes"),
       "answerHistory":m({"dates":["2025年3月12日","2025年3月05日","2025年2月21日"],"newAnswerMustNotOverwrite":True},"source and requirements")},
"G03":{"implementationConstraint":m("上下重复的保存按钮需合并；字符上限按代码约束，不采用生成图中随意给出的500。","manifest reviewNotes"),
       "actualCharacterLimit":u("Code constraint not inspected in this source-only task."),
       "keyboard":u("Source keyboard hidden; runtime safe area and keyboard behavior must be verified separately.")},
"G04":{"implementationConstraint":m("上下重复的保存按钮需合并；字符上限按代码约束，不采用生成图中随意给出的100。","manifest reviewNotes"),
       "actualCharacterLimit":u("Code constraint not inspected."),
       "deleteSystemQuestion":m(False,"manifest requirements: system templates cannot gain an unsupported delete entry")},
"G05":{"implementationConstraint":m("系统模板菜单不能提供删除模板；完成状态和数量只来源于当前账号。","manifest reviewNotes"),
       "sourceCounts":m({"未开始":3,"进行中":1,"已完成":2},"visual examples only"),
       "sourceItems":m([{"text":v[0],"state":v[1],"type":"system" if n<3 else "custom"} for n,v in enumerate(CHECKLIST)],"original source")},
"G06":{"categoryOptions":u("Only 学习成长 is visible; no complete hidden enum is supplied."),
       "initialCompletionState":u("No completion control shown; do not infer default completed."),
       "systemTemplateReplacement":m(False,"manifest requirements")},
"G07":{"deleteScope":m("删除完成记录","manifest requirements"),
       "sourceCounter":m("42/500","source only; numeric maximum not verified code constraint"),
       "photoPolicy":i("Use source assets, clean baked close buttons before placing independent close controls. No replacement stock image.")},
"G08":{"tabs":m({"values":["问题","清单","足迹"],"selected":"足迹"},"source"),
       "records":m([{"title":"公园散步","date":"2025年4月12日","place":"星河公园","photo":"footprint-park"},{"title":"周末晚餐","date":"2025年4月5日","place":"小满餐厅","photo":"footprint-dinner"}],"example records")},
"G09":{"sourceState":m({"title":"海边散步","place":"东岸公园","date":"2026年9月26日","photos":"2/3"},"example input"),
       "photoPolicy":i("Photo crops include close controls that must be separated after cleaning.")},
}
build(ROOT,TEXT,CONTROLS,ASSETS,
      {"G01":"问题目录","G02":"问题与历次回答","G03":"写下回答","G04":"新增自定义问题","G05":"人生清单","G06":"创建清单项目","G07":"记录完成感受","G08":"生活足迹","G09":"新增足迹"},
      SAMPLES,EXTRAS)

COMPONENTS=[
("区域 / 问题目录筛选",["G01"],["filter","filter-selected"],["Selected:VARIANT"],"全部/未答/已答；原图只选中全部"),
("列表项 / 问题",["G01"],["question-0","question-1","question-2","question-3"],["Question:TEXT","State:VARIANT","Icon:INSTANCE_SWAP"],"问题文本、状态徽标、文档图标与chevron统一母版"),
("区域 / 问题上下文",["G02","G03"],["question","question-context"],["Question:TEXT","Description:TEXT"],"不同源图字号/布局用有依据变体，不强行缩放"),
("列表项 / 历次回答",["G02"],["date-1","answer-1","date-2","answer-2","date-3","answer-3"],["Date:TEXT","Answer:TEXT"],"旧答案保留；不把说明实现方式的文案混进组件"),
("控件 / 编辑表单",["G03","G04","G06","G07","G09"],["answer","question","item","category","feeling","title","place","date","body"],["Label:TEXT","Value:TEXT","Helper:TEXT","ShowCounter:BOOLEAN"],"Auto-layout label/field/helper；源图计数字符上限非业务约束"),
("控件 / 保存取消",["G03","G04","G06","G07","G09"],["save","cancel"],["Label:TEXT","Style:VARIANT"],"G03/G04只留一个清楚保存入口；G09取消是文本，不能套用G06背景按钮"),
("区域 / 分类切换",["G05"],["category","category-selected"],["Selected:VARIANT"],"旅行/学习/生活"),
("卡片 / 清单统计",["G05"],["summary-0","summary-1","summary-2"],["State:VARIANT","Count:TEXT","Icon:INSTANCE_SWAP"],"不将3/1/2作为默认账号数据"),
("列表项 / 清单项目",["G05"],["item-0","item-1","item-2","item-3"],["Title:TEXT","State:VARIANT","IsSystem:BOOLEAN","Feeling:TEXT","ShowFeeling:BOOLEAN"],"系统模板禁止删除模板；自定义与系统必须可区分"),
("区域 / 关联项目",["G07"],["associated-item"],["Title:TEXT","Artwork:INSTANCE_SWAP"],"独立书本像素素材"),
("控件 / 照片附件",["G07","G09"],["photo-0","photo-1","photo-add"],["Photo:INSTANCE_SWAP","ShowRemove:BOOLEAN"],"保持每个源图照片比例；先清理烘焙关闭按钮"),
("卡片 / 足迹记录",["G08"],["footprint-0","footprint-1"],["Date:TEXT","Title:TEXT","Place:TEXT","Body:TEXT","Photo:INSTANCE_SWAP"],"将编辑/删除操作做共用图标实例；照片与文字独立"),
("区域 / 向往分区",["G08","G01"],["section-tab-0","section-tab-1","section-tab-2"],["Selected:VARIANT"],"G08源图可测；G01遗漏入口的新增位置unknown，父编排需确定"),
("区域 / 底部导航",["G01","G08"],["nav-0","nav-1","nav-2","nav-3"],["Selected:VARIANT","Icons:INSTANCE_SWAP"],"G01叶片与G08山形原图不同，不互换"),
("素材 / 原图艺术与图标",list(TEXT),[r[0] for r in ASSETS],["Artwork:INSTANCE_SWAP"],"所有源图艺术仍是位图，先干净提取；无法干净提取才走Image Two，禁止通用图标替代"),
]
plan={
"schemaVersion":"1.0.0",
"scope":m("Source-only component plan; no Figma inspection or mutation in this task","task"),
"sourceSpecs":m(["source-spec.json","asset-manifest.json"],"local outputs"),
"masterPage":i("02｜组件库与素材"),"screenPage":i("01｜还原稿与组件"),
"figmaFileKey":u("No target document read during this source-only analysis"),
"order":i(["tokens from original samples","accepted asset masters","atomic controls","region masters","screen instances","visual and editable QA"]),
"components":[{"name":i(name),"screens":m(pages,"source applicability"),"sourceElementIds":m(ids,"source-spec ids, not Figma node IDs"),
               "masterNodeId":u("Not created"),"instanceNodeIds":u("Not created"),"properties":i(props),
               "notes":i(notes),"placement":i({"column":n%3,"row":n//3,"gap":120},"proposed nonoverlapping library grid")}
              for n,(name,pages,ids,props,notes) in enumerate(COMPONENTS)],
"reviewNotes":{code:m(json.loads((ROOT/"source-spec.json").read_text(encoding="utf-8"))["screens"][n]["reviewNotes"]["value"],"original manifest copied unchanged")
               for n,code in enumerate(TEXT)},
"acceptance":i("NOT BUILT / NOT ACCEPTED. Parent writer must resolve review gates, verify source-size screenshots and editability."),
}
(ROOT/"component-plan.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")

# Every field receives local explicit provenance without breaking the compact schema.
INFERRED_KEYS={"id","type","colorRole","radiusCandidate","strokeCandidate","visibleState","plannedFile","status",
              "textBoxCandidate","fontSizeCandidate","fontWeightCandidate","lineHeightCandidate","letterSpacingCandidate","textAlignCandidate",
              "geometryMeaning","coordinateSystem","fieldStatusRules","componentRule","scope"}
def annotate(value):
    if isinstance(value,list):
        return [annotate(v) for v in value]
    if not isinstance(value,dict):
        return value
    if {"value","status","source"}.issubset(value):
        return value
    result={key:annotate(child) for key,child in value.items()}
    result["_fieldStatus"]={key:("unknown" if child is None else ("inferred" if key in INFERRED_KEYS or key.endswith("Candidate") else "measured"))
                            for key,child in value.items()}
    return result
for filename in ["source-spec.json","asset-manifest.json","component-plan.json"]:
    path=ROOT/filename
    content=annotate(json.loads(path.read_text(encoding="utf-8")))
    path.write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding="utf-8")
    print(filename,len(path.read_bytes()))
