# 倉庫名稱、技能與 PR 維護

目標倉庫名稱：`kmw02-video-roughcut`；原名：`tool-video-roughcut`。

## 主選單與技能編號

在本儲存庫的影片對話輸入「0」或「主選單」，由 [選單技能](../../.agents/skills/video-workflow-menu/SKILL.md) 讀取 [技能登錄表](SKILLS.json) 並核對實際入口。技能1沿用 `video-production-pilot`，技能2為 `mv-emotional-editing`；主選單不占剪輯技能編號。新增技能時登錄固定編號、名稱、entry 與 workflow，不重編已有技能。

## 這次使用新 PR

技能2與主選單是技能1之後的獨立變更，從最新 main 建立 `codex/mv-skill-menu` 分支，再開新 PR。既有未合併的 PR #2 是另一項程式功能，本次不合併或覆蓋它。新技能不必新建倉庫，也不必一個檔案開一個 PR。

流程：修改與驗證 → 只提交通用技能／文件／必要名稱引用 → 推送分支 → 建立以 main 為 base 的 PR → 檢視 Files changed → 合併。PR 建立後的修正繼續推送同一分支，會更新同一 PR。建立 PR 不等於已合併；合併另依使用者指示。

私人影片、歌曲、字幕逐字稿、工程包、登入資料與測試暫存保存在忽略的 production-work，不加入 PR。

## 倉庫改名的影響

GitHub 支援具有管理權限者改名。一般網頁及 Git clone／fetch／push 的舊位置會轉址；本機 origin 仍應更新。GitHub Pages 專案網站與使用此倉庫作為 Action 的引用不能直接依賴一般轉址，改名前另查。

本次同步修正 package.json 套件名稱、README／文件連結、通用範例路徑及打包腳本的 GitHub 來源網址。程式以相對位置讀取的檔案不因遠端倉庫名稱改變而搬移。

本機已存在的資料夾保留原路徑，既有影音工程可能引用該資料夾的絕對媒體路徑；GitHub 改名不要求同步搬動本機資料夾。若未來要改本機資料夾名，另檢查工程來源、工作區設定及工具路徑，再分開遷移。

完成遠端改名後，在原本本機資料夾執行：

```powershell
git remote set-url origin https://github.com/DinoHappyKM/kmw02-video-roughcut.git
git remote -v
git fetch origin
```

已開的 PR 及提交仍屬同一倉庫；改名是倉庫設定，不是 PR 內的檔案變更。不要建立同名的新倉庫冒充改名，也不要日後重用舊名而破壞轉址。

依 [GitHub 倉庫改名文件](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository) 維護；實際改名與 PR 連結另以當次完成結果為準。
