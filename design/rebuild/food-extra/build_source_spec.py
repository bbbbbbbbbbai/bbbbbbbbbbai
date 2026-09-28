from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent.parent))
from source_spec_common_readonly import build, measured as m, inferred as i, unknown as u

TEXT={
"D04":[
("code","D04",[17,5,51,28],18,400,False,"LEFT"),
("time","9:41",[72,5,65,28],18,400,False,"LEFT"),
("battery","100%",[422,5,72,28],18,400,False,"LEFT"),
("title","最近/常吃食物",[76,45,319,39],26,700,False,"LEFT"),
("tab-recent","最近使用",[25,113,219,34],20,700,False,"CENTER"),
("tab-common","常吃食物",[244,113,244,34],20,400,False,"CENTER"),
("hint-1","这是你最近使用过的食物列表，",[88,187,396,29],18,400,False,"LEFT"),
("hint-2","方便快速再次选择。不是已保存的每日饮食记录。",[88,212,396,31],18,400,False,"LEFT"),
],
"D05":[
("code","D05",[17,5,51,28],18,400,False,"LEFT"),
("time","9:41",[72,5,65,28],18,400,False,"LEFT"),
("battery","100%",[422,5,72,28],18,400,False,"LEFT"),
("title","收藏食物",[76,45,319,39],26,700,False,"LEFT"),
("hint-1","收藏的食物是你手动添加的，方便快速选择，",[90,118,390,29],18,400,False,"LEFT"),
("hint-2","不会自动添加。你可以随时取消收藏。",[90,144,390,29],18,400,False,"LEFT"),
],
"D06":[
("time","9:41",[25,7,61,27],18,400,False,"LEFT"),
("battery","100%",[426,7,72,27],17,400,False,"LEFT"),
("title","自定义食物",[128,50,256,40],26,700,False,"CENTER"),
("create","创建",[445,53,56,35],21,400,False,"LEFT"),
("heading","我的食物",[23,129,451,39],26,700,False,"LEFT"),
("oatmeal-name","自制燕麦粥",[86,197,378,35],23,400,False,"LEFT"),
("oatmeal-info","每100克：68千卡 · 蛋白质2.5克 · 碳水12克 · 脂肪1.2克",[86,231,379,29],16,400,False,"LEFT"),
("meatball-name","家常牛肉丸",[86,294,378,35],23,400,False,"LEFT"),
("meatball-info","每100克：250千卡 · 蛋白质18克 · 碳水6克 · 脂肪16克",[86,328,379,29],16,400,False,"LEFT"),
("soymilk-name","无糖豆浆",[86,392,378,35],23,400,False,"LEFT"),
("soymilk-info","每100克：33千卡 · 蛋白质3.0克 · 碳水1.4克 · 脂肪1.8克",[86,426,379,29],16,400,False,"LEFT"),
],
"D07":[
("time","9:41",[25,7,61,27],18,400,False,"LEFT"),
("battery","100%",[426,7,72,27],17,400,False,"LEFT"),
("title","创建食物",[128,50,256,40],26,700,False,"CENTER"),
("name-label","名称",[31,127,451,33],20,400,False,"LEFT"),
("name-value","自制燕麦粥",[47,175,417,36],23,400,False,"LEFT"),
("calories-label","每100克热量（千卡）",[31,240,451,33],20,400,False,"LEFT"),
("calories-value","68",[47,288,417,36],23,400,False,"LEFT"),
("protein-label","每100克蛋白质（克）",[31,353,451,33],20,400,False,"LEFT"),
("protein-value","2.5",[47,401,417,36],23,400,False,"LEFT"),
("carbs-label","每100克碳水（克）",[31,466,451,33],20,400,False,"LEFT"),
("carbs-value","12",[47,514,417,36],23,400,False,"LEFT"),
("fat-label","每100克脂肪（克）",[31,580,451,33],20,400,False,"LEFT"),
("fat-value","1.2",[47,628,417,36],23,400,False,"LEFT"),
("serving-label","每份克重（克）",[31,693,451,33],20,400,False,"LEFT"),
("serving-value","250",[47,741,417,36],23,400,False,"LEFT"),
("save","保存食物",[141,830,230,40],23,500,True,"CENTER"),
("cancel","取消",[141,910,230,39],23,400,False,"CENTER"),
],
}

RECENT=[
("chicken","鸡胸肉（熟）","2025年4月24日","100克 · 165千卡",273,275,309,337,294),
("banana","香蕉","2025年4月23日","1根（120克） · 105千卡",388,390,424,451,408),
("broccoli","西兰花（熟）","2025年4月22日","100克 · 35千卡",503,504,537,565,523),
("egg","鸡蛋（煮）","2025年4月21日","1个（50克） · 78千卡",618,620,653,680,638),
("brown-rice","糙米饭（熟）","2025年4月20日","100克 · 116千卡",735,736,770,798,756),
("apple","苹果","2025年4月19日","1个（200克） · 104千卡",850,852,887,914,872),
]
FAVORITES=[
("chicken","鸡胸肉（熟）","100克 · 165千卡","100","克",201,201,233,265,282,293,290),
("salmon","三文鱼（熟）","100克 · 208千卡","100","克",359,361,393,424,441,452,449),
("egg","鸡蛋（煮）","1个（50克） · 78千卡","1","个",518,520,552,583,600,611,608),
("broccoli","西兰花（熟）","100克 · 35千卡","100","克",677,679,710,742,759,770,767),
("apple","苹果","1个（200克） · 104千卡","1","个",837,839,870,902,919,930,927),
]
for name,title,date,detail,py,ty,dy,sy,ay in RECENT:
    TEXT["D04"].extend([
      (name+"-title",title,[130,ty,289,35],22,700,False,"LEFT"),
      (name+"-date","上次："+date,[130,dy,289,30],18,400,False,"LEFT"),
      (name+"-serving",detail,[130,sy,289,30],18,400,False,"LEFT"),
    ])
for name,title,detail,value,unit,py,ty,sy,ly,by,cy,ny in FAVORITES:
    TEXT["D05"].extend([
      (name+"-title",title,[111,ty,335,34],21,700,False,"LEFT"),
      (name+"-serving",detail,[111,sy,335,31],19,400,False,"LEFT"),
      (name+"-portion-label","选择份量",[301,ly,178,26],17,400,False,"LEFT"),
      (name+"-view","查看",[81,by+9,52,28],17,400,False,"LEFT"),
      (name+"-unfavorite","取消收藏",[198,by+9,82,28],17,400,False,"LEFT"),
      (name+"-quantity",value,[347,ny+4,68,31],19,500,False,"CENTER"),
      (name+"-unit",unit,[425,ny+5,25,30],18,400,False,"LEFT"),
    ])

CONTROLS={
"D04":[
("tabs-divider","line",[24,157,464,1],0,0,""),
("recent-underline","rect",[24,155,220,3],1,0,"selected"),
("hint","rect",[20,176,472,77],12,0,""),
("gesture","rect",[184,1005,142,5],3,0,""),
],
"D05":[
("hint","rect",[20,107,472,78],12,0,""),
("gesture","rect",[185,1005,141,5],3,0,""),
],
"D06":[
("heading-divider","line",[24,180,464,1],0,0,""),
("oatmeal-divider","line",[24,278,464,1],0,0,""),
("meatball-divider","line",[24,375,464,1],0,0,""),
("soymilk-divider","line",[24,473,464,1],0,0,""),
("gesture","rect",[188,1002,136,6],3,0,""),
],
"D07":[
("name","rect",[31,164,451,54],8,1,"filled"),
("calories","rect",[31,276,451,55],8,1,"filled"),
("protein","rect",[31,390,451,54],8,1,"filled"),
("carbs","rect",[31,502,451,55],8,1,"filled"),
("fat","rect",[31,616,451,54],8,1,"filled"),
("serving","rect",[31,730,451,54],8,1,"filled"),
("save","rect",[28,819,457,62],9,0,""),
("cancel","rect",[28,898,457,61],9,1,""),
("gesture","rect",[188,1002,137,6],3,0,""),
],
}
for index,(name,title,date,detail,py,ty,dy,sy,ay) in enumerate(RECENT):
    CONTROLS["D04"].extend([
      (name+"-photo","rect",[24,py,89,89],10,0,""),
      (name+"-add","ellipse",[440,ay,46,46],23,0,""),
      (name+"-divider","line",[24,[376,489,604,721,838,953][index],464,1],0,0,""),
    ])
for index,(name,title,detail,value,unit,py,ty,sy,ly,by,cy,ny) in enumerate(FAVORITES):
    CONTROLS["D05"].extend([
      (name+"-photo","rect",[23,py,72,71],8,0,""),
      (name+"-view","rect",[23,by,114,47],11,1,""),
      (name+"-unfavorite","rect",[148,by,135,47],11,1,""),
      (name+"-minus","ellipse",[301,cy,34,34],17,1,""),
      (name+"-quantity","rect",[347,ny,68,39],8,1,"filled"),
      (name+"-plus","ellipse",[455,cy,34,34],17,0,""),
      (name+"-divider","line",[24,[344,503,662,822,982][index],464,1],0,0,""),
    ])

ASSETS=[
("status-library","D04",[344,7,416,31],"icon","Different from D06/D07 header family; no time/100% text in crop."),
("back-library","D04",[22,52,52,83],"icon","Shared D04/D05 candidate."),
("search-library","D04",[396,50,427,82],"icon",""),
("more-library","D04",[465,49,486,84],"icon",""),
("recent-hint-clock","D04",[33,195,70,234],"icon","Source pale-blue matte; no copy in crop."),
("add-recent","D04",[438,292,489,343],"icon","Filled circular source control artwork; native interaction shell separate."),
("favorite-hint-star","D05",[36,127,73,166],"icon",""),
("favorite-star","D05",[456,205,490,240],"icon","Repeated selected star; source also shows cancel action, see manifest warning."),
("view-eye","D05",[42,294,69,320],"icon",""),
("unfavorite-trash","D05",[163,290,189,321],"icon","Red matte must remain separate from action label."),
("minus-favorite","D05",[300,291,337,329],"icon","Precise native minus geometry only after explicit source classification."),
("plus-favorite","D05",[453,291,492,330],"icon","Do not replace with D04 larger source control at forced scale."),
("status-custom","D06",[350,8,422,31],"icon","No interface text in crop."),
("back-custom","D06",[24,56,55,89],"icon","Shared D06/D07 candidate."),
("create-plus","D06",[405,56,436,88],"icon",""),
("oatmeal-bowl","D06",[23,207,65,250],"icon","Bitmap colored source icon, not vector."),
("meatball-red","D06",[22,305,65,347],"icon",""),
("soymilk-blue","D06",[27,404,61,448],"icon",""),
("custom-chevron","D06",[474,216,491,242],"icon","Reuse master at source row positions."),
]
for name,title,date,detail,py,ty,dy,sy,ay in RECENT:
    ASSETS.append(("recent-"+name,"D04",[24,py,113,py+89],"photo","Natural89x89 source crop; rounded-corner background pixels remain."))
for name,title,detail,value,unit,py,ty,sy,ly,by,cy,ny in FAVORITES:
    ASSETS.append(("favorite-"+name,"D05",[23,py,95,py+71],"photo","Natural72x71 source crop. Do not silently reuse D04 photo framing."))

SAMPLES={
"D04":{"background":[309,961,392,985],"primary_ink":[77,57,123,78],"accent":[449,299,478,334],"hint_surface":[30,181,71,192]},
"D05":{"background":[320,985,380,997],"primary_ink":[78,56,121,78],"accent":[456,211,483,232],"hint_surface":[30,112,77,124]},
"D06":{"background":[80,784,173,826],"primary_ink":[201,60,244,80],"accent":[30,219,58,245]},
"D07":{"background":[37,970,130,987],"primary_ink":[210,61,255,80],"accent":[41,837,145,862]},
}
EXTRAS={
"D04":{
 "pageIdentity":m("最近/常吃食物；这是食物快捷选择列表，不是已保存饮食历史","original D04 and manifest"),
 "tabs":m({"labels":["最近使用","常吃食物"],"selected":"最近使用"},"source"),
 "rows":m([{"asset":"recent-"+name,"title":title,"date":date,"serving":detail,"imageXYWH":[24,py,89,89],"textX":130,"addXYWH":[440,ay,46,46]} for name,title,date,detail,py,ty,dy,sy,ay in RECENT]),
},
"D05":{
 "pageIdentity":m("收藏食物；5个手动收藏条目及份量控件","original D05 and manifest"),
 "rows":m([{"asset":"favorite-"+name,"title":title,"detail":detail,"quantity":value,"unit":unit,"imageXYWH":[23,py,72,71],"controlsY":by,"favoriteSelected":True} for name,title,detail,value,unit,py,ty,sy,ly,by,cy,ny in FAVORITES]),
 "implementationConstraint":m("收藏星标与“取消收藏”存在重复操作，进入 Figma 时合并为一个明确入口。","manifest reviewNotes"),
 "referenceOnlyRedundancy":m("Raw source positions include both star and cancel action so the discrepancy is traceable. Production/accepted component should follow the explicit review decision.","original and manifest"),
},
"D06":{
 "pageIdentity":m("自定义食物目录，不是创建表单","original D06 and manifest"),
 "rows":m([{"name":"自制燕麦粥","box":[24,181,464,97],"iconCrop":"oatmeal-bowl"},{"name":"家常牛肉丸","box":[24,279,464,96],"iconCrop":"meatball-red"},{"name":"无糖豆浆","box":[24,376,464,97],"iconCrop":"soymilk-blue"}]),
 "createEntry":m({"plusCrop":"create-plus","text":"创建","position":[405,56]},"source"),
},
"D07":{
 "pageIdentity":m("创建自定义食物表单；六个字段，不是食物目录","original D07 and manifest"),
 "fields":m(["名称","每100克热量（千卡）","每100克蛋白质（克）","每100克碳水（克）","每100克脂肪（克）","每份克重（克）"],"source"),
 "exampleValues":m(["自制燕麦粥","68","2.5","12","1.2","250"],"source visual examples, not default personal/user data"),
 "photoInput":m(False,"No photo picker exists in original D07"),
},
}
build(Path(__file__).parent,TEXT,CONTROLS,ASSETS,
      {"D04":"最近/常吃食物","D05":"收藏食物","D06":"自定义食物","D07":"创建食物"},
      SAMPLES,EXTRAS)
