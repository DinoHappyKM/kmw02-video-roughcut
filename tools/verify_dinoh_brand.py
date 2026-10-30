"""Check canonical DinoH assets before releasing the owner's KM/KMT/KMW plugins."""
from pathlib import Path
import hashlib,json,sys
EXPECTED="794ec09c4c718ec1bbb946057b4471a9503507d339368cf227d0b784d50e8cf1"
def verify(root):
 import yaml
 root=Path(root).resolve();errors=[];refs=[]
 def asset(base,value,label):
  if not isinstance(value,str):errors.append(label+": missing icon path");return
  p=(base/value).resolve()
  if not p.is_relative_to(root) or not p.is_file():errors.append(label+": missing or escaping asset");return
  if hashlib.sha256(p.read_bytes()).hexdigest()!=EXPECTED:errors.append(label+": not canonical original PNG")
  refs.append(p.relative_to(root).as_posix())
 for rel in ("plugin.json",".codex-plugin/plugin.json"):
  p=root/rel
  if not p.exists():
   if rel=="plugin.json":errors.append("plugin.json missing")
   continue
  m=json.loads(p.read_text(encoding="utf-8-sig"));i=m.get("extensions",{}).get("com.openai",{}).get("interface",m.get("interface",{}))
  for key in ("logo","composerIcon"):asset(root,i.get(key),rel+":"+key)
 skills=sorted((root/"skills").glob("*/SKILL.md"))
 if not skills:errors.append("no packaged skills")
 for sk in skills:
  ap=sk.parent/"agents/openai.yaml"
  if not ap.exists():errors.append(str(ap.relative_to(root))+": missing UI metadata");continue
  i=yaml.safe_load(ap.read_text(encoding="utf-8-sig")).get("interface",{})
  for key in ("icon_small","icon_large"):asset(sk.parent,i.get(key),str(ap.relative_to(root))+":"+key)
 return {"package":root.name,"skill_count":len(skills),"references_checked":len(refs),"errors":errors,"passed":not errors}
if __name__=="__main__":
 result=verify(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
 print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(not result["passed"])
