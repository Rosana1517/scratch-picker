# 刮刮樂選號器

手機瀏覽器直接使用：**https://rosana1517.github.io/scratch-picker/**

（GitHub 的 repo 頁面只是原始碼，無法當 App 使用；請開上面的網址。）

## 安裝到手機主畫面
- iPhone（Safari）：分享 → 加入主畫面
- Android（Chrome）：選單 → 安裝應用程式／加到主畫面

## 開發與部署
- 編輯 `index.html` 後執行 `python build.py`，會把可獨立部署的 PWA 輸出到 `docs/`。
- GitHub Pages 設定：Settings → Pages → Source 選 `Deploy from a branch`，Branch 選 `main`、資料夾選 `/docs`。
