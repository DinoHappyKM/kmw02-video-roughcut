"""Build the self-contained KMW02 skills-only plugin from canonical sources."""
from pathlib import Path
import hashlib, json, posixpath, re, tempfile, zipfile
from urllib.parse import quote, unquote
ROOT=Path(__file__).resolve().parents[1]
SLUG="kmw02-ai-editing"
VERSION="0.1.0"
DISPLAY="黃嘉偉KMW02AI剪輯"
LINK=re.compile(r"(!?\[[^\]]*\]\()([^)\n]+)(\))")
REPO="https://github.com/DinoHappyKM/kmw02-video-roughcut/blob/main/"
def sha(data): return hashlib.sha256(data).hexdigest()
def build():
    sources={ROOT/"START_HERE.md":"references/START_HERE.md"}
    for p in sorted((ROOT/"docs"/"production").rglob("*.md")):
        sources[p]="references/"+p.relative_to(ROOT).as_posix()
    for p in sorted((ROOT/".agents"/"skills").glob("*/SKILL.md")):
        sources[p]="skills/"+p.parent.name+"/SKILL.md"
    files={}; provenance=[]
    for source,dest in sources.items():
        raw=source.read_bytes(); text=raw.decode("utf-8")
        def change(m):
            url=m.group(2).strip("<>")
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:",url) or url.startswith("#"): return m.group(0)
            path,sep,anchor=url.partition("#")
            absolute=(source.parent/unquote(path)).resolve()
            if absolute in sources:
                target=posixpath.relpath(sources[absolute],posixpath.dirname(dest) or ".")
            elif absolute==ROOT/"docs"/"production"/"SKILLS.json":
                target=posixpath.relpath("references/docs/production/SKILLS.json",posixpath.dirname(dest))
            else:
                assert absolute.is_relative_to(ROOT),f"External local path: {source}"
                target=REPO+quote(absolute.relative_to(ROOT).as_posix(),safe="/")
            return m.group(1)+target+("#"+anchor if sep else "")+m.group(3)
        text=LINK.sub(change,text)
        text=text.replace("這是儲存庫內的技能入口，通用規則唯一來源在 docs/production。使用時須保留整個儲存庫的相對路徑；不要只複製此技能資料夾當成完整學生安裝包。",
            "這是黃嘉偉KMW02AI剪輯的完整部署副本，內含 references 流程文件；規則主檔在 GitHub，更新後重新打包。")
        text=text.replace("路徑以儲存庫根目錄為準","路徑以此外掛根目錄為準")
        text=text.replace(".agents/skills/*/SKILL.md","skills/*/SKILL.md")
        if source.parent.name=="mv-emotional-editing" and source.name=="SKILL.md":
            text=text.replace("也不代表已安裝到 ChatCut 技能庫或全域技能目錄","也不代表已安裝到 ChatCut 技能庫或驗證所有工具連線")
        files[dest]=text.encode("utf-8")
        provenance.append({"source":source.relative_to(ROOT).as_posix(),"deployment":dest,"sourceSha256":sha(raw),"deploymentSha256":sha(files[dest])})
    registry=json.loads((ROOT/"docs"/"production"/"SKILLS.json").read_text(encoding="utf-8"))
    registry["menuSkill"]="skills/video-workflow-menu/SKILL.md"
    for item in registry["skills"]:
        item["entry"]="skills/"+item["slug"]+"/SKILL.md"
        item["workflow"]="references/"+item["workflow"]
    files["references/docs/production/SKILLS.json"]=(json.dumps(registry,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    interface={"displayName":DISPLAY,"shortDescription":"多機訪談與MV情緒敘事剪輯","longDescription":"輸入0開啟主選單，選技能1多機訪談剪輯或技能2MV情緒敘事剪輯。依確認方案與交付方式製作，保留可恢復原聲。需要本機素材及可用剪輯工具。","developerName":"黃嘉偉","category":"Productivity","capabilities":[],"defaultPrompt":"使用 $video-workflow-menu，顯示黃嘉偉KMW02AI剪輯的主選單。"}
    manifest={"$schema":"https://agent-plugins.org/schemas/1.0.0/plugin.schema.json","name":SLUG,"version":VERSION,"description":"多機訪談與MV情緒敘事剪輯工作流程","author":{"name":"黃嘉偉"},"repository":"https://github.com/DinoHappyKM/kmw02-video-roughcut","extensions":{"com.openai":{"requires_local_executor":True,"interface":interface,"onboardingSkill":"./skills/video-workflow-menu/SKILL.md"}}}
    files["plugin.json"]=(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    files["Install-Windows.ps1"]=(ROOT/"tools"/"plugin-install-windows.ps1").read_bytes()
    files["安裝說明.md"]=(ROOT/"docs"/"production"/"PLUGIN_INSTALL.md").read_bytes()
    files["BUILD_SOURCES.json"]=(json.dumps({"version":VERSION,"sources":provenance},ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    assert len(interface["shortDescription"])<=30
    for key,data in list(files.items()):
        if not key.endswith(".md"):continue
        for m in LINK.finditer(data.decode("utf-8")):
            url=m.group(2).strip("<>")
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:",url) or url.startswith("#"): continue
            target=posixpath.normpath(posixpath.join(posixpath.dirname(key),unquote(url.partition("#")[0])))
            assert target in files,f"{key}: missing {target}"
    for item in registry["skills"]:
        assert item["entry"] in files and item["workflow"] in files
    assert registry["menuSkill"] in files
    skills=sorted(k for k in files if re.fullmatch(r"skills/[^/]+/SKILL.md",k))
    assert len(skills)==3
    import yaml
    for k in skills:
        text=files[k].decode("utf-8"); assert text.startswith("---\n") or text.startswith("---\r\n")
        fm=yaml.safe_load(text.split("---",2)[1])
        assert fm["name"]==k.split("/")[1] and isinstance(fm["description"],str) and fm["description"].strip()
    validation={"version":VERSION,"portableManifest":"passed","skills":skills,"registryAndMarkdownReferences":"passed","privateMedia":"excluded","windowsIsolatedInstall":"see external PLUGIN_VALIDATION.json","desktopMenuAndEditing":"pending"}
    files["VALIDATION.json"]=(json.dumps(validation,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    files["SHA256SUMS.json"]=(json.dumps({k:sha(v) for k,v in sorted(files.items())},ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    out=ROOT/"dist";out.mkdir(exist_ok=True)
    archive=out/(DISPLAY+"-v"+VERSION+".zip")
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(SLUG+"/"+name,(2026,10,19,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,data)
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert all(n.startswith(SLUG+"/") and ".." not in n.split("/") for n in z.namelist())
            z.extractall(td)
        assert {p.relative_to(Path(td)/SLUG).as_posix():p.read_bytes() for p in (Path(td)/SLUG).rglob("*") if p.is_file()}==files
    result={"archive":archive.name,"version":VERSION,"displayName":DISPLAY,"files":len(files),"sha256":sha(archive.read_bytes()),"bytes":archive.stat().st_size,"archiveReadback":"passed","manifestReferencesAndSkills":"passed"}
    (out/"PLUGIN_BUILD.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":build()
