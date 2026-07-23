# devsecops-lab

AIS3 DevSecOps CI/CD 課程 Lab Repo

## 快速開始

1. Fork 這個 repo 到你自己的帳號
2. 開啟 GitHub Codespaces（或 clone 到本機）
3. 確認工具：
   ```bash
   gitleaks version
   pip-audit --version
   semgrep --version
   ```

## Lab 結構

| 檔案 | 說明 |
|------|------|
| `app/main.py` | Flask 主程式（有一個問題）|
| `app/database.py` | 資料庫操作（閱讀教材）|
| `app/config.py` | 設定檔（有一個問題）|
| `requirements.txt` | 依賴套件（有問題）|
| `.github/workflows/security-incomplete.yml` | Phase 1+2：找缺口、跑工具 |
| `.pre-commit-config.yaml` | Phase 2：本機自動化層 |

## Phase 說明

- **Phase 1+2**：讀 incomplete.yml 找缺口，手動跑三個工具，裝 pre-commit
- **Phase 3**：用 AI 修掉 eval() 漏洞，再跑 semgrep 驗證警告消失
- **Phase 4**：到 GitHub Settings 開啟 Secret Scanning、Dependabot、CodeQL
- **Phase 5**：寫一條 semgrep rule 抓 database.py 的 SQL injection
