#!/usr/bin/env python3
"""Security Quality Gate for SAST (semgrep) findings.

起司模型 · 第 2 層：CI 層的最後一關（Quality Gate）
這支腳本本身不掃描任何東西，它是 CI 層 pipeline 的「判官」：讀
semgrep 已經產生的 JSON 報告，決定這次的 finding 組合該不該擋下
部署。掃描（找問題）跟守門（決定要不要擋）是兩個獨立步驟，拆開來
才能在不重新掃描的情況下調整「擋不擋」的政策。

Reads a semgrep --json report and decides whether the finding set should
block the pipeline or merely warn. The decision uses semgrep's own
rule-assigned `extra.severity` field (ERROR / WARNING / INFO) -- that
field exists specifically for downstream tools to make this call, as
opposed to `extra.metadata.impact/confidence/likelihood`, which are a
separate, human-review-oriented risk assessment and do not agree with
`severity` on every finding.

Policy:
  ERROR            -> blocking     (exit 1, red GitHub Actions error annotations)
  WARNING / INFO    -> advisory     (exit 0, yellow annotations + $GITHUB_STEP_SUMMARY)

SCA (pip-audit) is out of scope for this gate; it is graded separately.
"""
import json
import os
import sys

# ═══════════════════════════════════════════════════════
# 判斷規則：這就是投影片「SECURITY QUALITY GATE」講的那個規則。
# ERROR 等級 -> 放進這個 set，擋部署（exit 1）。
# WARNING / INFO -> 不在這個 set 裡，只警告、照樣放行（exit 0）。
# 要調整「多嚴格才擋」，只需要改這一行，不用動下面的分類/輸出邏輯。
# ═══════════════════════════════════════════════════════
BLOCKING_SEVERITIES = {"ERROR"}

RESET = "\033[0m"
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"


def load_findings(report_path):
    with open(report_path) as f:
        report = json.load(f)
    return report.get("results", [])


# ─────────────────────────────────────────────
# 分類邏輯：把 semgrep 吐出的每一筆 finding 二分成「擋部署」或「只警告」
# ─────────────────────────────────────────────
def classify(findings):
    # 投影片「SECURITY QUALITY GATE」的核心邏輯：每個 finding 只依 severity 二分，
    # 落在 BLOCKING_SEVERITIES 裡的擋部署，其餘全部只當警告放行。
    blocking, advisory = [], []
    for finding in findings:
        severity = finding.get("extra", {}).get("severity", "WARNING")
        if severity in BLOCKING_SEVERITIES:
            blocking.append(finding)
        else:
            advisory.append(finding)
    return blocking, advisory


# ─────────────────────────────────────────────
# 輸出：把分類結果變成人看得懂的東西——console 顏色、GitHub Actions
# annotation（PR 上直接標紅/黃）、還有 job summary 頁面的表格。
# ─────────────────────────────────────────────
def describe(finding):
    path = finding.get("path", "?")
    line = finding.get("start", {}).get("line", "?")
    rule = finding.get("check_id", "?")
    message = finding.get("extra", {}).get("message", "").strip().splitlines()[0]
    return path, line, rule, message


def emit_gh_annotation(level, finding):
    path, line, rule, message = describe(finding)
    print(f"::{level} file={path},line={line}::[{rule}] {message}")


def print_console(color, label, finding):
    path, line, rule, message = describe(finding)
    print(f"{color}[{label}] {path}:{line} ({rule}){RESET}")
    print(f"  {message}")


def write_step_summary(blocking, advisory):
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a") as f:
        f.write("# Security Quality Gate: SAST\n\n")
        if blocking:
            f.write(f"## 🔴 Blocking findings ({len(blocking)})\n\n")
            f.write("| Rule | File | Line |\n|---|---|---|\n")
            for finding in blocking:
                path, line, rule, _ = describe(finding)
                f.write(f"| {rule} | {path} | {line} |\n")
            f.write("\n")
        if advisory:
            f.write(f"## 🟡 Advisory findings ({len(advisory)}, not blocking)\n\n")
            f.write("| Rule | File | Line |\n|---|---|---|\n")
            for finding in advisory:
                path, line, rule, _ = describe(finding)
                f.write(f"| {rule} | {path} | {line} |\n")
            f.write("\n")
        if not blocking and not advisory:
            f.write("No SAST findings.\n")


# ─────────────────────────────────────────────
# 入口：串起「讀報告 -> 分類 -> 輸出 -> 依結果決定 exit code」，
# exit code 就是 GitHub Actions 用來判斷這個 job 該不該算失敗的依據。
# ─────────────────────────────────────────────
def main():
    if len(sys.argv) != 2:
        print("usage: security_gate.py <semgrep-json-report>", file=sys.stderr)
        return 2

    findings = load_findings(sys.argv[1])
    blocking, advisory = classify(findings)

    print(
        f"Security Quality Gate: {len(findings)} SAST finding(s) "
        f"-- {len(blocking)} blocking (ERROR), {len(advisory)} advisory (WARNING/INFO)\n"
    )

    for finding in blocking:
        emit_gh_annotation("error", finding)
        print_console(RED, "BLOCKING", finding)

    for finding in advisory:
        emit_gh_annotation("warning", finding)
        print_console(YELLOW, "ADVISORY", finding)

    write_step_summary(blocking, advisory)

    if blocking:
        print(f"\n{RED}Gate FAILED: {len(blocking)} blocking (ERROR-severity) finding(s).{RESET}")
        return 1

    if advisory:
        print(
            f"\n{YELLOW}Gate PASSED with {len(advisory)} advisory (WARNING/INFO-severity) "
            f"finding(s) -- see step summary.{RESET}"
        )
        return 0

    print(f"{GREEN}Gate PASSED: no SAST findings.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
