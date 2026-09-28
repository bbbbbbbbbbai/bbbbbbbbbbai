from pathlib import Path
from hashlib import sha256
from datetime import datetime
import json
from PIL import Image, ImageStat

ROOT=Path(__file__).parent
SOURCE=ROOT.parent.parent/"boards"
MANIFEST=ROOT.parent.parent/"manifest.json"
ROOT.mkdir(parents=True,exist_ok=True)


def m(value,source="Original board PNG; native-pixel measurement or direct transcription"):
    return {"value":value,"status":"measured","source":source}


def i(value,source="Candidate inferred from source board; not original editable metadata"):
    return {"value":value,"status":"inferred","source":source}


def u(source):
    return {"value":None,"status":"unknown","source":source}


BOARD_LAYOUT={
 "S01":[
   ("S01-01","显示密码",[0,0,512,600]),("S01-02","两次不一致",[512,0,1024,600]),("S01-03","验证码错误",[1024,0,1536,600]),
   ("S01-04","验证码过期",[0,600,768,1024]),("S01-05","重发等待",[768,600,1536,1024])],
 "S02":[
   ("S02-01","登录键盘",[0,0,768,512]),("S02-02","长邮箱与大字",[768,0,1536,512]),
   ("S02-03","长菜名",[0,512,768,1024]),("S02-04","长备注",[768,512,1536,1024])],
 "S03":[
   ("S03-01","首次离线",[0,0,768,512]),("S03-02","同步失败",[768,0,1536,512]),
   ("S03-03","本地空间错误",[0,512,768,1024]),("S03-04","旧账号待处理",[768,512,1536,1024])],
 "S04":[
   ("S04-01","正在搜索",[0,0,768,512]),("S04-02","无匹配结果",[768,0,1536,512]),
   ("S04-03","相关搜索",[0,512,768,1024]),("S04-04","清空搜索",[768,512,1536,1024])],
 "S05":[
   ("S05-01","查询超时",[0,0,768,512]),("S05-02","离线结果",[768,0,1536,512]),
   ("S05-03","请求过快",[0,512,768,1024]),("S05-04","恢复联网",[768,512,1536,1024])],
}
PANELS={
 "S01":{
 "S01-01":{"title":"注册账号","main":"密码显示","details":["邮箱 hello@example.com","密码 Abc12345","确认密码 ••••••••••"],"actions":["可继续","返回"],"feedback":None,"risk":"展示密码仅为安全示例；确认密码保持隐藏。"},
 "S01-02":{"title":"注册账号","main":"两次不一致","details":["邮箱 hello@example.com","密码 Abc12345","确认密码 ••••••••••"],"actions":["注册 disabled","返回"],"feedback":"两次输入的密码不一致","risk":"保留输入，提交按钮禁用。"},
 "S01-03":{"title":"邮箱验证码","main":"验证码错误","details":["hello@example.com","验证码 381204"],"actions":["编辑邮箱","重试"],"feedback":"验证码错误，请重试","risk":"错误输入高亮；不可显示验证成功。"},
 "S01-04":{"title":"邮箱验证码","main":"验证码过期","details":["hello@example.com","验证码 381204"],"actions":["编辑邮箱","重新发送"],"feedback":"验证码已过期","risk":"允许重发；保留编辑邮箱。"},
 "S01-05":{"title":"邮箱验证码","main":"重发等待","details":["hello@example.com","验证码 381204","48秒后重发"],"actions":["编辑邮箱","重新发送 disabled"],"feedback":"48秒后重发","risk":"验证提交动作仍须保留；按钮文案与主页面统一。"},
 },
 "S02":{
 "S02-01":{"title":"登录键盘","main":"键盘展开","details":["邮箱 laobai@example.com","密码 ••••••••","登录按钮仍在键盘上方"],"actions":["登录","注册账号"],"feedback":"系统键盘遮挡下方内容","risk":"键盘图只是遮挡关系示意，不是定制系统键盘。"},
 "S02-02":{"title":"长邮箱与大字","main":"长邮箱和大字体","details":["laobai.diary.user.2025@example.com","密码 ••••••••"],"actions":["登录","注册账号"],"feedback":"无裁切、无眼睛图标重叠","risk":"真实设备大字体与安全区需验证。"},
 "S02-03":{"title":"记录饮食","main":"长菜名","details":["香煎鸡胸肉配西兰花与黑胡椒酱","每100g","165千卡 /31.2g蛋白质 /5.6g脂肪 /2.8g碳水"],"actions":["加号","完成"],"feedback":"两行食物名保持加号对齐","risk":"长菜名应可换行，不裁切营养数据。"},
 "S02-04":{"title":"编辑备注","main":"长备注","details":["89/500","长文本在可滚动编辑区"],"actions":["取消","保存"],"feedback":"键盘展开，保存可见","risk":"长备注滚动时不可丢失输入。"},
 },
 "S03":{
 "S03-01":{"title":"老白の日记","main":"无法连接服务器","details":["请检查网络连接后重试"],"actions":["重试","返回登录"],"feedback":"首次离线","risk":"不创建虚假空账号。"},
 "S03-02":{"title":"老白の日记","main":"同步失败，请稍后重试","details":["服务器暂时不可用，已保留您的登录状态","右上角小白 / 已登录"],"actions":["重试","返回"],"feedback":"服务器暂时不可用","risk":"保留登录状态；失败可重试。"},
 "S03-03":{"title":"老白の日记","main":"无法打开本地数据","details":["可能是存储空间不足或数据文件异常"],"actions":["查看详情","重试","返回登录"],"feedback":"本地空间错误","risk":"不默认清空；原始数据库错误不直接暴露。"},
 "S03-04":{"title":"老白の日记","main":"账号迁移尚未完成","details":["您的历史数据正在迁移中","记录不会被删除，请耐心等待"],"actions":["查看状态","返回登录"],"feedback":"旧账号待处理","risk":"状态文案须绑定真实后端处理状态。"},
 },
 "S04":{
 "S04-01":{"title":"老白の日记","main":"正在搜索","details":["查询 番茄炒蛋","搜索结果（加载中…）","保留旧结果"],"actions":["取消","清空"],"feedback":"小型加载指示","risk":"同一查询下保留输入与旧结果。"},
 "S04-02":{"title":"老白の日记","main":"未找到相关记录","details":["查询 番茄炒面","相关搜索：番茄炒蛋 / 番茄拌面 / 西红柿炒蛋 / 鸡蛋拌面"],"actions":["自定义添加「番茄炒面」"],"feedback":"无匹配结果","risk":"不能把未匹配误报为没有该食物；自定义入口应弱化。"},
 "S04-03":{"title":"老白の日记","main":"相关搜索","details":["查询 番茄","相关搜索：番茄炒蛋 / 番茄拌面 / 番茄汤 / 番茄炒鸡蛋","别名建议：西红柿（与番茄为同一食材） / 番茄（别名：西红柿）"],"actions":["选择建议"],"feedback":"相关词与别名建议","risk":"没有真实历史时不可预置个人搜索记录。"},
 "S04-04":{"title":"老白の日记","main":"清空搜索","details":["输入框为空","最近搜索：番茄 / 鸡蛋 / 番茄炒蛋 / 西红柿","热门搜索：番茄炒蛋 / 鸡蛋 / 土豆 / 牛肉 / 白菜"],"actions":["清空","选择最近/热门"],"feedback":"键盘焦点合理","risk":"清空后恢复空搜索/建议状态。"},
 },
 "S05":{
 "S05-01":{"title":"老白の日记","main":"查询超时，请检查网络后重试","details":["这不是没有结果，请检查网络连接"],"actions":["重试","查看本地记录"],"feedback":"网络超时","risk":"区别网络失败与无结果。"},
 "S05-02":{"title":"老白の日记","main":"当前为离线结果","details":["远程请求不可用，仅显示本地记录","西红柿炒蛋 / 番茄炒蛋（改良版） / 西红柿鸡蛋面"],"actions":["重试联网","查看离线条目"],"feedback":"离线 marker","risk":"显示食物和营养数据，不显示图中烹饪时间；缓存能力尚未实现。"},
 "S05-03":{"title":"老白の日记","main":"请求过快，请稍后再试","details":["请等待片刻后重试，避免频繁请求","可在8秒后重试"],"actions":["重试 disabled","查看本地记录"],"feedback":"限流等待","risk":"不伪造无结果。"},
 "S05-04":{"title":"老白の日记","main":"正在恢复联网…","details":["正在尝试连接到网络，请稍候"],"actions":["正在重试… disabled","取消"],"feedback":"恢复联网加载","risk":"同一查询保留；加载完成后再刷新结果。"},
 },
}
PANELS["S01"]["_review"]="验证码重发等待时仍须保留验证提交动作；按钮文案需与主页面统一。"
PANELS["S02"]["_review"]="键盘图只是遮挡关系示意，不是定制系统键盘；真实设备安全区和大字体仍需验证。"
PANELS["S03"]["_review"]="“正在迁移”“记录不会被删除”等文案不能靠推测显示，须绑定真实后端处理状态。"
PANELS["S04"]["_review"]="相关词与历史建议属于搜索体验补齐；未有真实历史时不可预置个人搜索记录。"
PANELS["S05"]["_review"]="离线结果应显示食物和营养数据，不应显示图中的烹饪时间；缓存能力尚未因出图而实现。"

manifest=json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
manifest_pages={p["id"]:p for p in manifest["pages"] if p["id"] in PANELS}
spec={
 "schemaVersion":"1.0.0","createdAt":datetime.now().astimezone().isoformat(),
 "scope":"State boards S01-S05 source analysis only; no Figma mutation",
 "coordinateSystem":"Board native pixels,1536x1024. Panel bounds are LTRB; panel-local visual boxes are inferred unless explicitly listed.",
 "boardSourceOfTruth":{"boards":[{"id":f"S0{i}","path":str(SOURCE/f"S0{i}.png"),"size":[1536,1024],"sha256":sha256((SOURCE/f"S0{i}.png").read_bytes()).hexdigest()} for i in range(1,6)]},
 "fieldStatusRules":{
  "measured":"Board size, panel bounds, visible state labels and transcribed copy from source.",
  "inferred":"Panel-local UI geometry, token candidates, component reuse and implementation recommendations.",
  "unknown":"Original text frames, actual runtime keyboard/safe inset, backend truth, and source font metadata."
 },
 "boards":[]
}
assets={"schemaVersion":"1.0.0","scope":"State board asset plan; no crops generated","assets":[],"sharedMasterCandidates":i(["status bars","back arrows","retry/loading indicators","error/status illustrations","search/keyboard controls"])}
components={"schemaVersion":"1.0.0","scope":"State-board component plan only","masterPage":i("02｜组件库与素材"),"screenPage":i("05｜交互状态"),"components":[],"acceptance":i("NOT BUILT / NOT ACCEPTED")}

for board,panels in BOARD_LAYOUT.items():
    path=SOURCE/f"{board}.png"
    boarddata={"id":board,"manifestName":m(manifest_pages[board]["name"],"manifest.json"),"sourceFile":str(path),"sourceSHA256":sha256(path.read_bytes()).hexdigest(),"size":[1536,1024],"panelLayout":[],"reviewNotes":m(manifest_pages[board]["reviewNotes"],"manifest.json"),"dataBoundary":m(manifest_pages[board]["dataBoundary"],"manifest.json")}
    for pid,label,bounds in panels:
        data=PANELS[board][pid]
        x0,y0,x1,y1=bounds
        localw,localh=x1-x0,y1-y0
        boarddata["panelLayout"].append({
         "id":pid,"label":m(label,"board header / manifest variant"),
         "boundsLTRB":m(list(bounds),"native board grid measurement"),
         "localViewport":[localw,localh],
         "title":m(data["title"],"visible state copy"),
         "state":m(data["main"],"visible state label"),
         "details":m(data["details"],"visible source copy and state details"),
         "actions":m(data["actions"],"visible action labels"),
         "feedback":m(data["feedback"],"visible feedback copy") if data["feedback"] else u("No explicit error/feedback line in this variant"),
         "risk":i(data["risk"]),
         "panelGeometry":i({"headerBand":[0,0,localw,58],"contentArea":[24,58,localw-48,localh-104],"actionSafeArea":[24,max(0,localh-170),localw-48,120]}),
         "textBoxes":u("Board raster has no source text-frame metadata; use visible text and local ROIs as guide."),
         "visualState":m(data["main"],"variant state"),
         "runtimeTruth":u("Static board cannot prove network/backend/keyboard/runtime state"),
         "panelReviewNote":m(PANELS[board]["_review"],"manifest reviewNotes")
        })
    spec["boards"].append(boarddata)

for board,panels in BOARD_LAYOUT.items():
    for pid,label,bounds in panels:
        x0,y0,x1,y1=bounds
        data=PANELS[board][pid]
        # Explicit source artwork candidates; do not substitute generic icon packs.
        kinds={
         "S01":"validation illustration / error icon / eye / email / shield",
         "S02":"keyboard bitmap, login art, food thumbnail, note editor controls",
         "S03":"offline cloud / retry / local storage / migration illustration",
         "S04":"search spinner / no-result search / recent clock / suggestion chips",
         "S05":"timeout clock / offline indicator / rate-limit clock / retry spinner",
        }
        assets["assets"].append({
         "id":pid+"-artwork","sourceBoard":board,"panel":pid,
         "cropLTRB":u("Panel-specific crop must be measured during writer extraction; board is not a UI background"),
         "pixelSize":u("Panel artwork boundaries vary; no generated crops in this analysis"),
         "classification":m(kinds[board],"visible source artwork family"),
         "vector":False,"alpha":u("Flattened board; transparency and matte unknown"),
         "status":i("needs_clean_extraction_or_ImageTwo"),
         "notes":i("Extract only artwork/icon pixels; keep all visible text, containers, states and controls native/editable."),
         "hash":m(None,"No standalone asset file created"),
        })

for board in PANELS:
    comps=[
      ("状态 / "+board+" 状态卡",["title","main","details","feedback"],["State:VARIANT","Title:TEXT","Details:TEXT","Feedback:TEXT"]),
      ("控件 / 重试与返回",["actions"],["Label:TEXT","Enabled:BOOLEAN","Style:VARIANT"]),
      ("素材 / "+board+" 状态插画",["artwork"],["Artwork:INSTANCE_SWAP"]),
    ]
    for name,slots,props in comps:
        components["components"].append({
         "name":i(name),"board":m(board,"source board id"),"sourceSlots":m(slots),
         "masterId":u("Not created"),"instanceIds":u("Not created"),"properties":i(props),
         "placement":i({"libraryColumn":len(components["components"])%3,"libraryRow":len(components["components"])//3,"gap":120}),
         "notes":i("Do not expose backend claims or create generic icon replacements. Keep variant-specific source copy and controls separate.")
        })

for filename,data in [("source-spec.json",spec),("asset-manifest.json",assets),("component-plan.json",components)]:
    path=ROOT/filename
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    json.loads(path.read_text(encoding="utf-8"))
    print(filename,path.stat().st_size)
