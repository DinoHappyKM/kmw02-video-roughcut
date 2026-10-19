# 黃嘉偉KMW02AI剪輯｜ZIP 安裝與使用

外掛版本：0.1.0。顯示名稱：黃嘉偉KMW02AI剪輯。技術識別：kmw02-ai-editing。

## 內容

- 0：影片主選單。
- 1：多機訪談剪輯（含雙機）。
- 2：MV 情緒敘事剪輯，含剪前方案確認、交付複選、hook／callback、踩點轉場及可恢復原聲。

這是本機工作流程外掛，沒有附影片、歌曲、剪輯軟體、帳號或連線憑證。實際剪輯需要本機素材與可用的 ChatCut／DaVinci 工具；安裝外掛不會自動安裝或連接這些軟體。

## Windows 安裝

1. 下載「黃嘉偉KMW02AI剪輯-v0.1.0.zip」，完整解壓縮到一般資料夾。
2. 進入 kmw02-ai-editing 資料夾，在此開啟 PowerShell。
3. 執行以下命令：

```powershell
powershell.exe -NoProfile -File .\Install-Windows.ps1
```

如系統限制腳本執行，確認套件來源後可只對這次程序執行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Windows.ps1
```

安裝器會檢查 SHA256，複製到 LocalAppData 的 KMW02AIEditing/0.1.0，註冊專用本機來源，再呼叫 Codex 安裝。遇到不同既有檔案會停止並保留原檔；不會修改影片或現有工程。

找不到 CLI 時，可加上 -CodexPath "codex.exe的完整路徑"；可用 -DestinationRoot "新的安裝資料夾" 改變安裝位置。-PrepareOnly 只準備檔案及目錄，不註冊或安裝外掛。

4. 重新啟動桌面版，在外掛目錄的本機來源找到「黃嘉偉KMW02AI剪輯」，核對已安裝／啟用。
5. 開啟新對話，選取這個外掛後輸入「0」。應看到技能1與技能2。

## 第一次使用

MV 範例：「請用技能2分析我的歌曲與初剪，先建議 hook、結尾 callback 與踩點規劃，等我確認再剪。這次交付 DRT。」

多機範例：「請用技能1，先檢查這批多機訪談素材及同步方式。」

提案確認與交付選擇是獨立步驟。選 DRT 時說明獨立交接工程的必要製作，不擅自回匯到使用者現有工程。未使用的原始同期聲保留、預設靜音且可恢復。

## 更新與移除

後續下載新版本並使用其安裝器；不要直接覆蓋不同內容或手改版本快取。移除可在外掛目錄操作，或使用支援此命令的 CLI：codex plugin remove kmw02-ai-editing@kmw02-ai-editing-local。素材及影片工程另行保留。

## 驗證範圍

ZIP 格式、引用完整性與 Windows 隔離安裝結果以同版 VALIDATION.json 為準。一般使用者桌面啟用、實際輸入0、不同電腦及新踩點規則的成片效果仍需驗收；本套件未宣稱 ChatCut My Skills 或 macOS 安裝已測完。

## 維護

[GitHub 倉庫](https://github.com/DinoHappyKM/kmw02-video-roughcut)。PR 尚未合併時，下載已提供的版本檔，不以 main 的內容推定版本。
[官方外掛封裝與本機來源說明](https://developers.openai.com/plugins/build/plugins)。

Notion 整理目標為使用者指定頁面；只有實際寫入並核對後才算保存完成。
