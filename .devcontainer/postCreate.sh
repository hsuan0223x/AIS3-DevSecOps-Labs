#!/usr/bin/env bash
set -uo pipefail

pip install -r requirements.txt

# pip-audit / semgrep / pre-commit 改用 pipx 個別裝進獨立的虛擬環境。
# 直接 `pip install --upgrade` 在共用環境下會被這個 Codespace 底層已預裝的其他套件
# （例如 mcp / jsonschema / pydantic 之類）卡住相依性解析，pip 為了不動到既有套件，
# 會一路往舊版本回退，導致「明明加了 --upgrade 還是裝到舊版」。pipx 讓每個工具各自
# 用自己的 venv，不跟其他套件共用相依性，就不會再發生這個回退問題。
python3 -m pip install --user --quiet --upgrade pipx
export PATH="$HOME/.local/bin:$PATH"
python3 -m pipx ensurepath >/dev/null 2>&1 || true

for tool in pip-audit semgrep pre-commit; do
  python3 -m pipx install --force "$tool"
done

GITLEAKS_VERSION="8.18.2"
ARCH="$(dpkg --print-architecture)"
[ "$ARCH" = "amd64" ] && GL_ARCH="x64" || GL_ARCH="arm64"

if curl -sSL -o /tmp/gitleaks.tar.gz \
  "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_${GL_ARCH}.tar.gz"; then
  sudo tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin gitleaks
  sudo chmod +x /usr/local/bin/gitleaks
  echo "gitleaks ${GITLEAKS_VERSION} installed via GitHub Releases binary"
else
  echo "WARNING: 下載固定版本二進位檔失敗，改用 apt 版本 gitleaks（版本可能不是 8.18.2）"
  sudo apt-get update -qq && sudo apt-get install -y gitleaks
fi

echo "=== 版本檢查 ==="
gitleaks version
pip-audit --version
semgrep --version
pre-commit --version
