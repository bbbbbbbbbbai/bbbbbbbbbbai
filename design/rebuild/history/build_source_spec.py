from pathlib import Path
import sys
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent.parent))
from source_spec_common_readonly import build, measured as m, inferred as i, unknown as u

ROOT=Path(__file__).parent
SOURCE=ROOT.parent.parent/"screens"
TEXT={code:[] for code in ["F01","F02","F03","F04","F05","F06","F07"]}


def t(code,key,content,box,size=20,weight=400,light=False,align="LEFT"):
    TEXT[code].append((key,content,box,size,weight,light,align))


for code,title in [("F01","历史记录"),("F02","日历"),("F03","趋势与统计")]:
    t(code,"time","9:41",[18,3,63,25] if code=="F01" else [240,3,67,25],14)
    t(code,"code","F01" if code=="F01" else ("P:02" if code=="F02" else "F03"),
      [241,3,56,25] if code=="F01" else [15,3,69,25],14)
    t(code,"battery","100%",[441,3,65,26],16)
    t(code,"title",title,[128,43,256,36],24,700,False,"CENTER")
    for index,label in enumerate(["今日","记录","向往","我的"]):
        t(code,"nav-"+str(index),label,[index*128,971,128,26],15,500 if index==1 else 400,False,"CENTER")

for key,content,box,size,weight in [
("range-7","7天",[24,108,106,31],18,500),
("range-30","30天",[130,108,110,31],18,400),
("category-label","分类",[24,164,109,25],14,400),
("date-label","日期范围",[155,164,221,25],14,400),
("order-label","时间顺序",[393,164,99,25],14,400),
("category-value","全部分类",[36,199,74,29],15,400),
("date-value","2025/05/01 – 2025/05/31",[164,199,181,29],14,400),
("order-value","从新到旧",[402,199,71,29],15,400),
("count","共 12 条记录",[24,261,180,29],16,400),
("filter-memory","筛选已保存 · 返回后保持当前筛选和滚动位置",[220,263,272,28],12.5,400),
]:
    t("F01",key,content,box,size,weight,key=="range-7","CENTER" if key.startswith("range-") else "LEFT")
HISTORY_ROWS=[
("5月20日　周二","12:30","饮食","午餐 · 685 千卡",306,333,350,339,369,344,"food"),
("5月19日　周一","08:20","运动","跑步 · 5.2 公里 · 320 千卡",407,438,456,446,474,450,"exercise"),
("5月18日　周日","19:10","饮食","晚餐 · 520 千卡",517,547,566,556,583,558,"food"),
("5月17日　周六","07:40","体重","68.5 公斤",625,655,673,664,690,665,"weight"),
("5月16日　周五","12:15","饮食","午餐 · 612 千卡",735,766,785,775,802,777,"food"),
("5月15日　周四","18:50","运动","健身 · 60 分钟 · 280 千卡",846,875,896,884,910,885,"exercise"),
]
for n,(day,time,title,detail,dy,line,ty,hy,sy,iy,kind) in enumerate(HISTORY_ROWS):
    t("F01",f"date-{n}",day,[24,dy,462,28],16)
    t("F01",f"time-{n}",time,[24,ty,71,29],17)
    t("F01",f"type-{n}",title,[158,hy,294,30],19,500)
    t("F01",f"detail-{n}",detail,[158,sy,311,27],17)

t("F02","month","2025年5月",[154,110,204,34],23,500,False,"CENTER")
CAL_X=[53,120,188,255,323,390,457]
for x,day in zip(CAL_X,["日","一","二","三","四","五","六"]):
    t("F02","weekday-"+day,day,[x-20,162,40,28],16,400,False,"CENTER")
CAL_WEEKS=[
 [27,28,29,30,1,2,3],
 [4,5,6,7,8,9,10],
 [11,12,13,14,15,16,17],
 [18,19,20,21,22,23,24],
 [25,26,27,28,29,30,31],
 [1,2,3,4,5,6,7],
]
CAL_YS=[205,261,318,376,434,492]
for row,(week,y) in enumerate(zip(CAL_WEEKS,CAL_YS)):
    for col,(day,x) in enumerate(zip(week,CAL_X)):
        selected=row==3 and col==2
        t("F02",f"day-{row}-{col}",str(day),[x-24,y,48,30],20 if selected else 17,700 if selected else 400,selected,"CENTER")
for key,content,box,size,weight in [
("selected-date","2025年5月20日",[22,553,155,33],20,700),
("selected-weekday","周二",[171,554,72,33],20,400),
("selected-count","共 2 条记录",[421,559,71,27],14,400),
("results-heading","当天结果",[22,604,451,32],20,700),
("weight-time","08:00",[22,655,69,30],17,400),
("weight-title","体重",[160,642,305,31],20,500),
("weight-value","68.3 公斤",[160,670,305,29],17,400),
("food-time","12:30",[22,725,69,30],17,400),
("food-title","饮食",[160,712,305,31],20,500),
("food-value","午餐 · 685 千卡",[160,740,305,29],17,400),
("empty-heading","无记录日期示例",[22,785,451,32],20,700),
("empty-date","5月21日",[106,828,81,31],18,400),
("empty-weekday","周三",[181,829,70,30],18,400),
("empty-caption","暂无记录",[106,856,324,28],16,400),
]:
    t("F02",key,content,box,size,weight)

t("F03","range-7","7天",[23,109,100,31],18,500,True,"CENTER")
t("F03","range-30","30天",[123,109,103,31],18,400,False,"CENTER")
t("F03","date-range","2025/05/14 – 2025/05/20",[287,109,204,31],16)
for key,title,y,unit in [("intake","热量摄入",166,"千卡"),("exercise","运动消耗",428,"千卡"),("weight","体重趋势",688,"公斤")]:
    t("F03",key+"-heading",title,[22,y,352,34],20,700)
    t("F03",key+"-unit","单位："+unit,[421,y+3,70,28],14)

INTAKE=[1620,1380,1250,980,1420,1310,1560]
EXERCISE=[320,280,0,450,200,320,0]
WEIGHTS=[69.2,69.0,68.8,68.6,68.4,68.5,68.3]
INTAKE_X=[98,157,217,276,336,396,458]
EXERCISE_X=[93,153,214,274,334,394,457]
WEIGHT_POINTS=[[82,800],[145,805],[207,809],[270,813],[333,818],[396,815],[458,820]]
DATES=["5/14","5/15","5/16","5/17","5/18","5/19","5/20"]
for n,(x,value,ly) in enumerate(zip(INTAKE_X,INTAKE,[211,228,241,258,227,236,209])):
    t("F03",f"intake-value-{n}",f"{value:,}",[x-30,ly,60,24],14,400,False,"CENTER")
    t("F03",f"intake-date-{n}",DATES[n],[x-27,349,54,26],14,400,False,"CENTER")
for n,(x,value,ly) in enumerate(zip(EXERCISE_X,EXERCISE,[518,527,582,485,542,518,580])):
    t("F03",f"exercise-value-{n}",str(value),[x-29,ly,58,24],14,400,False,"CENTER")
    t("F03",f"exercise-date-{n}",DATES[n],[x-27,611,54,26],14,400,False,"CENTER")
for n,((x,y),value) in enumerate(zip(WEIGHT_POINTS,WEIGHTS)):
    t("F03",f"weight-value-{n}",f"{value:.1f}",[x-29,y-31,58,25],14,400,False,"CENTER")
    t("F03",f"weight-date-{n}",DATES[n],[x-28,870,56,26],14,400,False,"CENTER")
for key,values,ys,x,w in [
("intake",["1,800","1,200","600","0"],[212,254,296,333],18,44),
("exercise",["600","400","200","0"],[471,513,554,594],24,31),
("weight",["72","70","68","66"],[731,772,813,854],20,25),
]:
    for n,(label,y) in enumerate(zip(values,ys)):
        t("F03",f"{key}-axis-{n}",label,[x,y,w,25],14,400,False,"RIGHT")
t("F03","legend-intake","实际摄入",[166,381,80,27],14)
t("F03","legend-target","目标值（1,500）",[286,381,190,27],14)
t("F03","legend-exercise","运动消耗",[240,644,112,27],14)
t("F03","legend-weight","体重",[251,903,90,28],14)

for code,title in [("F04","饮食记录详情"),("F05","运动记录详情"),("F06","体重记录详情")]:
    t(code,"code",code+" "+title,[17,4,285,27],16)
    t(code,"time","9:41",[29,32,69,30],19)
    t(code,"battery","100%",[403,32,86,30],19)
    t(code,"title",title,[89,79,294,48],29,700)
for key,content,box,size,weight,align in [
("meal-label","餐次",[92,167,233,40],24,400,"LEFT"),
("meal-value","午餐",[353,167,132,40],24,400,"RIGHT"),
("quantity-label","数量",[92,244,233,40],24,400,"LEFT"),
("quantity-value","350 g",[353,244,132,40],25,400,"RIGHT"),
("nutrition-heading","营养",[92,321,233,40],24,400,"LEFT"),
("energy-label","热量",[143,374,182,35],22,400,"LEFT"),
("energy-value","520 kcal",[336,373,149,38],25,400,"RIGHT"),
("protein-label","蛋白质",[143,423,182,35],22,400,"LEFT"),
("protein-value","28 g",[365,423,120,38],25,400,"RIGHT"),
("carbs-label","碳水",[143,474,182,35],22,400,"LEFT"),
("carbs-value","62 g",[365,474,120,38],25,400,"RIGHT"),
("fat-label","脂肪",[143,526,182,36],22,400,"LEFT"),
("fat-value","18 g",[365,526,120,38],25,400,"RIGHT"),
("source-label","来源",[92,610,233,40],24,400,"LEFT"),
("source-value","手动记录",[333,610,152,40],24,400,"RIGHT"),
("basis-label","估算依据",[92,687,351,40],24,400,"LEFT"),
("basis-value","食材数据库估算",[94,722,353,35],20,400,"LEFT"),
("date-label","日期",[92,798,233,40],24,400,"LEFT"),
("date-value","2025年3月8日",[278,798,207,40],24,400,"RIGHT"),
("note-label","备注",[92,880,213,40],24,400,"LEFT"),
("note-value","少油，正常份量",[284,880,201,40],24,400,"RIGHT"),
]:
    t("F04",key,content,box,size,weight,False,align)
for key,label,value,y in [
("type","类型","跑步",158),("duration","时长","42 分钟",221),
("distance","距离","6.2 km",285),("intensity","强度","中等",350),
("energy","消耗估算","约 410 kcal",414),("steps","步数","7,860 步",482),
]:
    t("F05",key+"-label",label,[91,y,225,38],23)
    t("F05",key+"-value",value,[317,y,168,38],24,400,False,"RIGHT")
t("F05","basis-label","估算依据",[91,545,349,39],23)
t("F05","basis-value","时长、距离与强度公式",[91,575,360,32],19)
t("F05","note-label","备注",[91,871,217,40],23)
t("F05","note-value","晚间慢跑",[321,871,164,40],23,400,False,"RIGHT")
t("F05","date-label","日期",[91,938,217,40],23)
t("F05","date-value","2025年3月7日",[282,938,203,40],23,400,False,"RIGHT")
for key,label,value,y in [
("weight","体重","69.5 kg",168),("sleep","睡眠","7.5 小时",251),
("date","日期","2025年3月8日",334),("note","备注","起床后记录",418),
]:
    t("F06",key+"-label",label,[91,y,215,42],24)
    t("F06",key+"-value",value,[300,y,185,42],24,400,False,"RIGHT")
for key,content,box,size,weight,align in [
("code","F07 心情记录详情",[18,3,319,29],17,400,"LEFT"),
("time","9:41",[30,32,80,32],19,400,"LEFT"),
("battery","100%",[439,32,66,33],19,400,"LEFT"),
("title","心情记录详情",[91,94,250,49],30,700,"LEFT"),
("edit","编辑",[324,125,77,32],20,400,"CENTER"),
("delete","删除",[411,125,76,32],20,400,"CENTER"),
("mood-heading","心情",[30,198,451,39],25,700,"LEFT"),
("mood-relaxed","轻松",[86,265,54,34],20,400,"LEFT"),
("mood-okay","还行",[204,265,55,34],20,400,"LEFT"),
("mood-irritable","烦躁",[320,265,55,34],20,400,"LEFT"),
("mood-tired","疲惫",[439,265,56,34],20,400,"LEFT"),
("stress-heading","压力（1 - 5）",[30,358,451,44],26,400,"LEFT"),
("sleep-heading","睡眠",[30,524,451,39],25,700,"LEFT"),
("sleep-value","7.5",[103,575,55,46],31,400,"LEFT"),
("sleep-unit","小时",[154,581,87,37],24,400,"LEFT"),
("date-heading","日期",[30,674,451,39],25,700,"LEFT"),
("date-value","2025年3月18日",[104,730,377,47],27,400,"LEFT"),
("note-heading","备注",[30,827,451,39],25,700,"LEFT"),
("note-value","今天状态不错，完成了计划。",[105,881,383,48],25,400,"LEFT"),
]:
    t("F07",key,content,box,size,weight,False,align)
for n,x in enumerate([31,123,216,309,402],1):
    t("F07",f"stress-{n}",str(n),[x,419,65,43],26,400,n==2,"CENTER")

CONTROLS={
"F01":[
("range-shell","rect",[24,102,216,43],14,1,""),
("range-7","rect",[24,103,106,40],13,0,"selected"),
("category-filter","rect",[24,193,107,40],8,1,"all"),
("date-filter","rect",[154,193,220,40],7,1,"custom-range"),
("order-filter","rect",[393,193,97,40],8,1,"newest"),
("filter-divider","line",[0,255,512,1],0,0,""),
],
"F02":[
("selected-day","ellipse",[161,362,53,53],27,0,"20"),
("calendar-divider","line",[22,545,468,1],0,0,""),
("results-divider","line",[22,634,468,1],0,0,""),
("weight-row-divider","line",[22,704,468,1],0,0,""),
("food-row-divider","line",[22,774,468,1],0,0,""),
("empty-example","rect",[22,818,468,74],10,0,"source-only mixed example"),
],
"F03":[
("range-shell","rect",[23,102,203,44],14,1,""),
("range-7","rect",[23,103,100,42],13,0,"selected"),
("intake-y-axis","line",[69,225,1,120],0,0,""),
("intake-x-axis","line",[69,345,420,1],0,0,""),
("intake-target","line",[78,245,411,1.5],0,0,"dashed"),
("exercise-y-axis","line",[62,483,1,124],0,0,""),
("exercise-x-axis","line",[62,607,427,1],0,0,""),
("weight-y-axis","line",[51,744,1,122],0,0,""),
("weight-x-axis","line",[51,866,438,1],0,0,""),
("legend-intake","ellipse",[148,390,10,10],5,0,""),
("legend-target","line",[247,395,29,1.5],0,0,"dashed"),
("legend-exercise","ellipse",[222,652,10,10],5,0,""),
("legend-weight","ellipse",[234,911,10,10],5,0,""),
],
"F04":[],
"F05":[("photo","rect",[27,617,459,226],9,0,"existing attachment example")],
"F06":[],
"F07":[
("header-divider","line",[31,174,451,1],0,0,""),
("relaxed","rect",[31,252,103,58],16,0,"selected-read-only"),
("okay","rect",[150,252,102,58],16,0,"read-only"),
("irritable","rect",[267,252,103,58],16,0,"read-only"),
("tired","rect",[385,252,102,58],16,0,"read-only"),
("mood-divider","line",[31,334,451,1],0,0,""),
("stress-divider","line",[31,499,451,1],0,0,""),
("sleep-divider","line",[31,650,451,1],0,0,""),
("date-divider","line",[31,803,451,1],0,0,""),
],
}
for n,row in enumerate(HISTORY_ROWS):
    CONTROLS["F01"].append((f"date-divider-{n}","line",[24,row[5],466,1],0,0,""))
for n,y in enumerate([400,506,615,725,835]):
    CONTROLS["F01"].append((f"record-divider-{n}","line",[24,y,466,1],0,0,""))
for code in ["F01","F02","F03"]:
    CONTROLS[code].extend([
      ("navigation-surface","rect",[0,933,512,67],0,0,"记录 selected"),
      ("navigation-divider","line",[0,933,512,1],0,0,""),
      ("gesture","rect",[198,1007,117,5],3,0,""),
    ])
for code,ys in [
("F04",[144,224,301,587,670,776,854]),
("F05",[145,209,271,335,399,465,530,855,920]),
("F06",[145,228,312,396]),
]:
    for n,y in enumerate(ys):
        CONTROLS[code].append((f"divider-{n}","line",[29,y,455,1],0,0,""))
    CONTROLS[code].append(("gesture","rect",[184,1002,145,6],3,0,""))
for n,x in enumerate([31,123,216,309,402],1):
    CONTROLS["F07"].append((f"stress-{n}","ellipse",[x,407 if n==2 else 408,65,65 if n==2 else 64],33,0,"selected-read-only" if n==2 else "read-only"))

DOTS=[
 (1,323,237,"green"),(3,457,237,"blue"),(5,120,293,"green"),(7,255,293,"red"),
 (9,390,293,"blue"),(12,120,350,"green"),(15,323,350,"blue"),(17,457,350,"red"),
 (19,120,407,"blue"),(20,188,407,"white"),
]
for day,x,y,color in DOTS:
    CONTROLS["F02"].append((f"calendar-dot-{day}","ellipse",[x-4,y-4,8,8],4,0,color))
for y in [225,267,309]:
    CONTROLS["F03"].append((f"intake-grid-{y}","line",[69,y,420,1],0,0,""))
for y in [483,525,566]:
    CONTROLS["F03"].append((f"exercise-grid-{y}","line",[62,y,427,1],0,0,""))
for y in [744,784,825]:
    CONTROLS["F03"].append((f"weight-grid-{y}","line",[51,y,438,1],0,0,""))
for n,(x,y) in enumerate(WEIGHT_POINTS):
    CONTROLS["F03"].append((f"weight-point-{n}","ellipse",[x-4.5,y-4.5,9,9],4.5,0,""))


def bar_measure(image,roi,color):
    x0,y0,x1,y1=roi
    part=image.crop(roi).convert("RGB")
    pixels=list(part.getdata())
    flag=[(g-r>20 and g-b>5 and g<195) if color=="green" else (b-r>25 and b-g>5) for r,g,b in pixels]
    mask=Image.new("L",part.size)
    mask.putdata([255 if v else 0 for v in flag])
    b=mask.getbbox()
    return [x0+b[0],y0+b[1],b[2]-b[0],b[3]-b[1]] if b else None


chart_image=Image.open(SOURCE/"F03.png").convert("RGB")
INTAKE_BARS=[bar_measure(chart_image,[x-21,228,x+22,346],"green") for x in INTAKE_X]
EXERCISE_BARS=[bar_measure(chart_image,[x-21,495,x+22,607],"blue") for x in EXERCISE_X]
for kind,bars in [("intake",INTAKE_BARS),("exercise",EXERCISE_BARS)]:
    for n,box in enumerate(bars):
        if box:
            CONTROLS["F03"].append((f"{kind}-bar-{n}","rect",box,0,0,"source example"))

ASSETS=[
("status-overview","F01",[373,3,438,26],"icon","Only icons, no100% text."),
("back-overview","F01",[23,45,44,74],"icon",""),
("calendar-action","F01",[376,106,407,137],"icon",""),
("chart-action","F01",[450,106,483,137],"icon",""),
("calendar-filter-small","F01",[346,201,369,226],"icon",""),
("filter-chevron","F01",[106,205,125,221],"icon",""),
("record-food","F01",[98,342,145,390],"icon","Bitmap food category mark; repeated row instance candidate."),
("record-exercise","F01",[98,447,145,496],"icon",""),
("record-weight","F01",[98,663,145,712],"icon",""),
("record-chevron","F01",[472,355,488,379],"icon",""),
("nav-home","F01",[52,939,84,973],"icon",""),
("nav-record-selected","F01",[177,939,210,971],"icon",""),
("nav-aspiration","F01",[302,939,339,974],"icon",""),
("nav-profile","F01",[430,938,462,973],"icon",""),
("month-previous","F02",[36,115,53,140],"icon",""),
("month-next","F02",[460,115,481,141],"icon",""),
("calendar-record-weight","F02",[98,642,147,693],"icon",""),
("calendar-record-food","F02",[98,712,147,763],"icon",""),
("empty-record","F02",[38,830,88,882],"icon",""),
("chart-date-calendar","F03",[246,107,276,139],"icon","No chart content, axes or data labels in crop."),
("status-detail","F04",[323,34,398,62],"icon",""),
("back-detail","F04",[28,83,61,118],"icon",""),
("edit-detail","F04",[387,82,422,119],"icon",""),
("delete-detail","F04",[453,83,487,119],"icon",""),
("meal","F04",[26,164,62,207],"icon",""),
("quantity-blue","F04",[25,241,65,282],"icon",""),
("nutrition-bars","F04",[27,322,63,356],"icon",""),
("energy-coral","F04",[88,371,124,409],"icon",""),
("protein-blue","F04",[89,420,126,458],"icon",""),
("carbs-amber","F04",[88,472,126,514],"icon",""),
("fat-coral","F04",[89,523,124,566],"icon",""),
("source-document","F04",[27,608,65,649],"icon",""),
("basis-book","F04",[26,691,66,729],"icon",""),
("basis-chevron","F04",[458,697,484,722],"icon",""),
("date-blue","F04",[25,794,66,836],"icon",""),
("note-green","F04",[26,876,66,918],"icon",""),
("exercise-green","F05",[26,157,64,198],"icon",""),
("duration-blue","F05",[26,220,64,258],"icon",""),
("distance-coral","F05",[28,285,63,323],"icon",""),
("intensity-green","F05",[26,349,64,383],"icon",""),
("exercise-energy-coral","F05",[27,413,63,452],"icon",""),
("steps-blue","F05",[26,479,67,518],"icon",""),
("exercise-attachment","F05",[27,617,486,843],"photo","Existing source attachment example; clean independent picture, no decorative replacement."),
("weight-green","F06",[26,166,67,208],"icon",""),
("sleep-blue","F06",[23,250,69,290],"icon",""),
("date-coral","F06",[25,332,67,376],"icon",""),
("status-mood","F07",[359,32,435,62],"icon","Soft original raster distinct from F04-F06 family."),
("back-mood","F07",[25,99,61,136],"icon",""),
("edit-mood","F07",[344,87,381,125],"icon","Editable 编辑 label excluded."),
("delete-mood","F07",[432,87,466,126],"icon","Editable 删除 label excluded."),
("mood-relaxed","F07",[41,261,80,301],"icon","Read-only source state, not input."),
("mood-okay","F07",[161,260,201,301],"icon",""),
("mood-irritable","F07",[277,260,317,301],"icon",""),
("mood-tired","F07",[396,260,436,301],"icon",""),
("sleep-outline","F07",[27,579,79,620],"icon",""),
("date-outline","F07",[30,724,75,774],"icon",""),
("note-outline","F07",[31,879,74,929],"icon",""),
]
SAMPLES={
"F01":{"background":[286,53,350,77],"primary_ink":[216,52,256,69],"accent":[32,114,53,133]},
"F02":{"background":[307,52,360,83],"primary_ink":[239,54,269,70],"accent":[169,377,181,397]},
"F03":{"background":[315,55,363,79],"primary_ink":[204,52,242,69],"accent":[90,256,104,311],"exercise_blue":[270,532,282,590],"target_blue":[250,244,272,246]},
"F04":{"background":[126,944,235,974],"primary_ink":[98,92,137,112],"accent":[34,169,53,196]},
"F05":{"background":[210,968,299,985],"primary_ink":[98,92,137,112],"accent":[34,165,54,190]},
"F06":{"background":[121,701,266,809],"primary_ink":[98,92,137,112],"accent":[30,173,62,201]},
"F07":{"background":[164,954,330,991],"primary_ink":[102,107,145,128],"accent":[133,424,145,451],"selected_mood":[89,257,120,266]},
}
EXTRAS={
"F01":{
 "dateFilterGeometry":m({
   "quickRangeXYWH":[24,102,216,43],"selectedQuickRange":"7天",
   "categoryXYWH":[24,193,107,40],"dateRangeXYWH":[154,193,220,40],
   "orderXYWH":[393,193,97,40],"visibleDateRange":["2025/05/01","2025/05/31"],
   "calendarActionCrop":"calendar-action","statisticsActionCrop":"chart-action",
 },"visible source geometry and state"),
 "sourceRecords":m([{"dateLabel":r[0],"time":r[1],"type":r[2],"description":r[3],"dateY":r[4],"iconXYWH":[100,r[9],42,42]} for r in HISTORY_ROWS],"original example rows only"),
 "implementationConstraint":m("7/30天与自定义日期范围需互斥；图中星期、日期与范围不完全一致，重建时使用真实日期。","manifest reviewNotes"),
 "navigationRequirement":m("返回保持当前筛选与滚动位置","manifest requirements/source helper"),
},
"F02":{
 "calendarGeometry":m({
   "month":"2025年5月","weekdayCentersX":CAL_X,"dayRows":CAL_WEEKS,
   "dayTextCandidateY":CAL_YS,"selected":{"day":20,"circleXYWH":[161,362,53,53]},
   "markerCenters":[{"day":day,"x":x,"y":y,"colorRole":color,"radius":4} for day,x,y,color in DOTS],
   "monthPreviousCrop":"month-previous","monthNextCrop":"month-next",
 },"native source-pixel measurements; all day text stays editable"),
 "ambiguousCodeLabel":u("Top-left generated label appears P:02 rather than F02; file/manifest identity is F02. Confirm before reproducing artifact text."),
 "implementationConstraint":m("移除混排的“无记录日期示例”，选中哪一天只显示那一天的实际结果。","manifest reviewNotes"),
},
"F03":{
 "dateFilterGeometry":m({"quickRangeXYWH":[23,102,203,44],"selected":"7天","calendarXYWH":[248,110,27,28],"dateTextCandidateXYWH":[287,109,204,31],"dates":["2025/05/14","2025/05/20"]}),
 "charts":[
  {
   "id":"calorie-intake","kind":"bar",
   "plotXYWH":m([69,225,420,120]),
   "xValues":m(DATES,"original axis labels"),
   "barCentersX":m([box[0]+box[2]/2 for box in INTAKE_BARS],"geometric centers derived from measured pixel rectangles"),
   "xTickCentersCandidate":i(INTAKE_X,"original date-label approximate centers"),
   "sourceValues":m(INTAKE,"example labels only, not real user data"),
   "barRectanglesXYWH":m(INTAKE_BARS,"Pillow source green-pixel bounding boxes, independent from values"),
   "yAxis":m([{"value":1800,"pixelY":225},{"value":1200,"pixelY":267},{"value":600,"pixelY":309},{"value":0,"pixelY":345}],"source geometry; do not assume exact data scale"),
   "targetLine":m({"labelValue":1500,"from":[78,245],"to":[489,245]}),
   "targetDashCandidate":i([6,4]),"barCornerCandidate":i(0),
  },
  {
   "id":"exercise-energy","kind":"bar",
   "plotXYWH":m([62,483,427,124]),"xValues":m(DATES,"source axis labels"),
   "barCentersX":m([box[0]+box[2]/2 if box else None for box in EXERCISE_BARS],"geometric centers derived from measured rectangles; zero-value has no bar"),
   "xTickCentersCandidate":i(EXERCISE_X,"original date-label approximate centers"),
   "sourceValues":m(EXERCISE,"example labels only"),
   "barRectanglesXYWH":m(EXERCISE_BARS,"Pillow blue-pixel bounds; null means visible zero label without a bar"),
   "yAxis":m([{"value":600,"pixelY":483},{"value":400,"pixelY":525},{"value":200,"pixelY":566},{"value":0,"pixelY":607}]),
  },
  {
   "id":"weight-trend","kind":"line",
   "plotXYWH":m([51,744,438,122]),"xValues":m(DATES,"source axis labels"),
   "sourceValues":m(WEIGHTS,"example numeric labels only"),
   "polylinePixelPoints":m(WEIGHT_POINTS,"manual original circle-center measurements; tolerance1px"),
   "pointRadiusCandidate":i(4.5),"lineWidthCandidate":i(2.5),"lineInterpolation":i("straight segments"),
   "yAxis":m([{"value":72,"pixelY":744},{"value":70,"pixelY":784},{"value":68,"pixelY":825},{"value":66,"pixelY":866}]),
  },
 ],
 "chartEditability":m("No complete chart image crop. Bars, line segments, points, axes and all numeric/date/legend text are separate native-editable structure.","explicit task instruction"),
 "implementationConstraint":m("图表数值、轴刻度和目标线仅示意，最终由数据生成，不描摹图片数字。","manifest reviewNotes"),
 "sourceVsRuntime":i("Store geometry/numbers solely as source-reference evidence. Runtime charts derive from real records; no fabricated curve for empty data."),
},
"F04":{
 "missingFoodName":u("Original does not display the specific food name; cannot infer it from350g or520kcal."),
 "implementationConstraint":m("当前参考图遗漏了具体食物名称；可编辑设计必须补上名称再进入开发。","manifest reviewNotes"),
 "nutritionExample":m({"energy":"520 kcal","protein":"28 g","carbs":"62 g","fat":"18 g"},"source example only"),
},
"F05":{
 "attachment":m({"asset":"exercise-attachment","cropLTRB":[27,617,486,843],"cornerCandidate":9},"source photo"),
 "sourceData":m({"type":"跑步","duration":"42 分钟","distance":"6.2 km","intensity":"中等","estimatedEnergy":"约410kcal","steps":"7,860步"},"example only"),
},
"F06":{
 "sourceData":m({"weight":"69.5kg","sleep":"7.5小时","date":"2025年3月8日","note":"起床后记录"},"example only"),
 "unsupportedMetrics":m("No body-fat measurement or new health metric appears in source.","source and manifest"),
},
"F07":{
 "sourceState":m({"mood":"轻松","stress":2,"sleep":"7.5小时","date":"2025年3月18日"},"example only"),
 "readOnlyDetails":m(True,"manifest reviewNotes"),
 "implementationConstraint":m("详情页的心情与压力应只读；点击编辑后才进入可调整的控件。","manifest reviewNotes"),
 "materialNote":i("Original is visibly softer and lower-contrast than F04-F06; do not impose their crisp-white surface/typography without comparison."),
},
}
build(ROOT,TEXT,CONTROLS,ASSETS,
      {"F01":"历史记录","F02":"日历","F03":"趋势与统计","F04":"饮食记录详情","F05":"运动记录详情","F06":"体重记录详情","F07":"心情记录详情"},
      SAMPLES,EXTRAS)
