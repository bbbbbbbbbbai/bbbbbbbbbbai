from pathlib import Path
from datetime import datetime
from hashlib import sha256
import json
from PIL import Image, ImageStat


def measured(value, source="Original source PNG; visible-edge native-pixel measurement, tolerance1-2px"):
    return {"value":value,"status":"measured","source":source}


def inferred(value, source="Candidate inferred from original raster; not original editable metadata"):
    return {"value":value,"status":"inferred","source":source}


def unknown(source):
    return {"value":None,"status":"unknown","source":source}


def build(root, text, controls, crops, titles, samples, extras=None):
    root=Path(root)
    source=root.parent.parent/"screens"
    manifest=json.loads((root.parent.parent/"manifest.json").read_text(encoding="utf-8-sig"))
    lookup={p["id"]:p for p in manifest["pages"] if p["id"] in text}
    root.mkdir(parents=True,exist_ok=True)
    spec={
      "schemaVersion":"1.0.0","createdAt":datetime.now().astimezone().isoformat(),
      "scope":"Original-source analysis only; no Figma creation or mutation",
      "coordinateSystem":"Original screen-local pixels,512x1024. Boxes XYWH; crops LTRB exclusive end.",
      "geometryMeaning":"Text x/y/w/h are measured visible-ink bounds inside candidate ROI, not original editable text frames.",
      "fontPolicy":{"actualFamily":unknown("No source font metadata supplied"),"candidateFamily":inferred("Noto Sans SC; calibrate original glyph metrics before acceptance")},
      "fieldStatusRules":{
        "text":{"measured":["text","x","y","w","h","inkMedianRGB"],"inferred":["textBoxCandidate","fontSizeCandidate","fontWeightCandidate","lineHeightCandidate","letterSpacingCandidate","textAlignCandidate","colorRole"]},
        "controls":{"measured":["x","y","w","h"],"inferred":["radiusCandidate","strokeCandidate","visibleState"]},
        "source":"Original PNG. Candidate font/line-height is not proven source typography. Shape edge tolerance1-2px."
      },"screens":[]
    }
    assets={
      "schemaVersion":"1.0.0","scope":"source crop planning only; crop files not generated","sources":{},
      "fieldStatusRules":{
        "measured":["sourceScreen","cropLTRB","pixelSize","classification","sourcePixelSHA256","vector","fileCreated"],
        "inferred":["plannedFile","status","componentRule"],"unknown":["alpha"],
        "source":"sourceScreen resolves through sources. Source artwork remains bitmap."
      },
      "componentRule":inferred("Use independent bitmap masters, reuse instances at natural pixel size within stable outer slots. Do not normalize all image fills to one size."),
      "assets":[]
    }
    for code, rows in text.items():
        path=source/f"{code}.png"
        image=Image.open(path).convert("RGB")
        assert image.size==(512,1024)
        digest=sha256(path.read_bytes()).hexdigest()
        assets["sources"][code]={"path":str(path),"sha256":digest,"status":"measured"}
        items=[]
        for key,content,box,size,weight,light,align in rows:
            x,y,w,h=box
            part=image.crop((x,y,x+w,y+h))
            pixels=list(part.getdata())
            flags=[min(p)>215 if light else min(p)<190 for p in pixels]
            mask=Image.new("L",part.size)
            mask.putdata([255 if flag else 0 for flag in flags])
            bb=mask.getbbox()
            ink=[x+bb[0],y+bb[1],bb[2]-bb[0],bb[3]-bb[1]] if bb else [None]*4
            foreground=[p for p,flag in zip(pixels,flags) if flag]
            color=[sorted(p[c] for p in foreground)[len(foreground)//2] for c in range(3)] if foreground else None
            items.append({
              "id":key,"text":content,"x":ink[0],"y":ink[1],"w":ink[2],"h":ink[3],
              "geometryStatus":"measured" if bb else "unknown","inkMedianRGB":color,
              "textBoxCandidate":box,"fontSizeCandidate":size,"fontWeightCandidate":weight,
              "lineHeightCandidate":round(size*1.4,1),"letterSpacingCandidate":0,
              "textAlignCandidate":align,"colorRole":"white" if light else "source_ink_sample"
            })
        colors={}
        for role,roi in samples[code].items():
            part=image.crop(roi)
            stat=ImageStat.Stat(part)
            pixels=list(part.getdata())
            if role=="accent":
                pixels=[p for p in pixels if p[1]-p[0]>25 and p[1]-p[2]>5]
            elif role=="primary_ink":
                pixels=[p for p in pixels if max(p)<140]
            colors[role]={
              "roiLTRB":measured(roi,"sampling coordinates"),
              "meanRGB":measured([round(v,2) for v in stat.mean],"source ROI mean"),
              "stddevRGB":measured([round(v,2) for v in stat.stddev],"source ROI stddev"),
              "filteredMedianRGB":measured([sorted(p[c] for p in pixels)[len(pixels)//2] for c in range(3)] if pixels else None,"Accent filters green, primary filters dark ink, others unfiltered")
            }
        screen={
          "id":code,"title":measured(titles[code],"original visible title"),
          "manifestName":measured(lookup[code]["name"],"manifest.json"),
          "sourceFile":str(path),"sourceSHA256":digest,"width":512,"height":1024,"dimensionStatus":"measured",
          "background":colors["background"],"colors":colors,"text":items,
          "controls":[{"id":key,"type":kind,"x":box[0],"y":box[1],"w":box[2],"h":box[3],
                       "geometryStatus":"measured","radiusCandidate":radius,"strokeCandidate":stroke,"visibleState":state}
                      for key,kind,box,radius,stroke,state in controls[code]],
          "assets":[name for name,src,*_ in crops if src==code],
          "reviewNotes":measured(lookup[code]["reviewNotes"],"manifest.json"),
          "dataBoundary":measured(lookup[code]["dataBoundary"],"manifest.json"),
          "trueDeviceSafeInset":unknown("Concept image, no device/density metadata")
        }
        if extras and code in extras:
            screen.update(extras[code])
        spec["screens"].append(screen)
    for name,code,crop,kind,note in crops:
        image=Image.open(source/f"{code}.png").convert("RGB").crop(crop)
        assets["assets"].append({
          "id":name,"sourceScreen":code,"cropLTRB":crop,"pixelSize":[crop[2]-crop[0],crop[3]-crop[1]],
          "plannedFile":str(root/"assets"/f"{name}.png"),"fileCreated":False,
          "classification":kind,"sourcePixelSHA256":sha256(image.tobytes()).hexdigest(),"vector":False,
          "alpha":unknown("Flattened PNG; transparency/source-matte handling must be explicit."),
          "status":"needs_clean_extraction" if kind.endswith("with_overlay") else "ready_for_exact_crop",
          "notes":note
        })
    for filename,data in [("source-spec.json",spec),("asset-manifest.json",assets)]:
        path=root/filename
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        json.loads(path.read_text(encoding="utf-8"))
        print(str(path),path.stat().st_size)
    print("screens",len(spec["screens"]),"texts",sum(len(s["text"]) for s in spec["screens"]),"assets",len(assets["assets"]))
