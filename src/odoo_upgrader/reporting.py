"""Reporting module for odoo-upgrader.

Generates comprehensive summary tables and actionable breakdown reports
showing what went right, what went wrong, and next steps for the developer.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .installer import InstallTestResult
from .static_checks import RuleMatch


class ModuleUpgradeResult(BaseModel):
    module_name: str
    source_version: int
    target_version: int
    backup_path: Optional[str] = None
    manifest_updated: bool = False
    xml_files_modified: int = 0
    py_files_modified: int = 0
    js_files_modified: int = 0
    precheck_total_issues: int = 0
    precheck_critical_issues: int = 0
    static_matches: List[RuleMatch] = Field(default_factory=list)
    install_result: Optional[InstallTestResult] = None
    errors: List[str] = Field(default_factory=list)
    success_notes: List[str] = Field(default_factory=list)

    @property
    def static_blockers_count(self) -> int:
        return sum(1 for m in self.static_matches if m.severity in ("blocking", "error"))

    @property
    def static_warnings_count(self) -> int:
        return sum(1 for m in self.static_matches if m.severity == "warning")

    @property
    def overall_status(self) -> str:
        if self.install_result and self.install_result.status == "FAIL":
            return "FAILED"
        if self.static_blockers_count > 0 or self.precheck_critical_issues > 0:
            return "ACTION_NEEDED"
        return "SUCCESS"


class UpgradeReporter:
    """Renders terminal tables and markdown reports."""

    def __init__(self, results: List[ModuleUpgradeResult], reports_dir: Optional[Path] = None):
        self.results = results
        self.reports_dir = reports_dir or Path.cwd() / "upgrade_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown_report(self) -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"upgrade_report_{ts}.md"

        lines = []
        lines.append("# 🚀 Odoo Upgrade Summary Report")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Table Section
        lines.append("## 📊 Overview Table")
        lines.append("| Module | Version | Files Modified | Pre-Check | Static Checks | App Install | Overall Verdict |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")

        for r in self.results:
            ver_str = f"v{r.source_version} → v{r.target_version}"
            files_str = f"XML:{r.xml_files_modified} PY:{r.py_files_modified} JS:{r.js_files_modified}"
            pre_str = f"Crit:{r.precheck_critical_issues} / Tot:{r.precheck_total_issues}"
            static_str = f"Block:{r.static_blockers_count} / Warn:{r.static_warnings_count}"

            if not r.install_result or r.install_result.status == "SKIPPED":
                install_str = "⚠️ Skipped"
            elif r.install_result.status == "PASS":
                install_str = f"✅ Pass ({r.install_result.duration_seconds}s)"
            else:
                install_str = "❌ Failed"

            if r.overall_status == "SUCCESS":
                status_badge = "✅ **SUCCESS**"
            elif r.overall_status == "ACTION_NEEDED":
                status_badge = "⚠️ **ACTION NEEDED**"
            else:
                status_badge = "❌ **FAILED**"

            lines.append(f"| **{r.module_name}** | {ver_str} | {files_str} | {pre_str} | {static_str} | {install_str} | {status_badge} |")

        lines.append("\n---\n")

        # Detailed Breakdown Section
        lines.append("## 🔍 Detailed Module Diagnostic & Action Items\n")

        for r in self.results:
            lines.append(f"### Module: `{r.module_name}`")
            if r.backup_path:
                lines.append(f"- **Backup Location:** `{r.backup_path}`")

            # What went right
            lines.append("\n#### ✅ What Went Right:")
            if r.manifest_updated:
                lines.append(f"- Manifest upgraded to target series v{r.target_version}.")
            if r.xml_files_modified > 0:
                lines.append(f"- Transformed {r.xml_files_modified} XML view file(s) (e.g. `<tree>` → `<list>`, `attrs` → inline conditions).")
            if r.py_files_modified > 0:
                lines.append(f"- Transformed {r.py_files_modified} Python file(s) (e.g. `@api.multi`, `_sql_constraints` migration).")
            if r.js_files_modified > 0:
                lines.append(f"- Transformed {r.js_files_modified} JavaScript/OWL file(s).")
            if r.install_result and r.install_result.status == "PASS":
                lines.append(f"- Dynamic test install passed with exit code 0 ({r.install_result.duration_seconds}s).")
            for note in r.success_notes:
                lines.append(f"- {note}")
            if not r.success_notes and r.xml_files_modified == 0 and r.py_files_modified == 0:
                lines.append("- Code syntax validated cleanly.")

            # What went wrong / Action Items
            has_issues = (
                r.precheck_critical_issues > 0
                or r.static_blockers_count > 0
                or (r.install_result and r.install_result.status == "FAIL")
                or len(r.errors) > 0
            )

            lines.append("\n#### ⚠️ What Went Wrong & Action Items:")
            if not has_issues:
                lines.append("- No critical blockers found! Module is ready for testing.")
            else:
                if r.install_result and r.install_result.status == "FAIL":
                    lines.append(f"- **App Installation Failure:** {r.install_result.error_summary}")
                    if r.install_result.log_output:
                        lines.append("  ```text")
                        lines.extend(f"  {line}" for line in r.install_result.log_output.splitlines()[-25:])
                        lines.append("  ```")

                if r.static_blockers_count > 0:
                    lines.append(f"- **Static Analysis Blockers ({r.static_blockers_count}):**")
                    for match in r.static_matches:
                        if match.severity in ("blocking", "error"):
                            rel_file = match.file_path.name
                            lines.append(f"  - `{rel_file}:{match.line_number}`: **{match.rule_id}** — {match.fix_hint}")
                            if match.snippet:
                                lines.append(f"    *Snippet:* `{match.snippet}`")

                if r.static_warnings_count > 0:
                    lines.append(f"- **Static Analysis Warnings ({r.static_warnings_count}):**")
                    for match in r.static_matches:
                        if match.severity == "warning":
                            rel_file = match.file_path.name
                            lines.append(f"  - `{rel_file}:{match.line_number}`: {match.fix_hint}")

                for err in r.errors:
                    lines.append(f"- {err}")

            lines.append("\n")

        report_file.write_text("\n".join(lines), encoding="utf-8")
        return report_file

    def print_terminal_summary(self):
        """Prints formatted console tables and summaries."""
        print("\n" + "=" * 90)
        print("                 ODOO UPGRADE SUMMARY & VERDICT TABLE")
        print("=" * 90)

        header = f"{'Module':<20} | {'Version':<10} | {'Files Mod':<12} | {'Static AST':<12} | {'Install Test':<14} | {'Verdict':<12}"
        print(header)
        print("-" * 90)

        for r in self.results:
            ver = f"v{r.source_version}->v{r.target_version}"
            files = f"{r.xml_files_modified + r.py_files_modified + r.js_files_modified} files"
            ast_stat = f"{r.static_blockers_count} blk / {r.static_warnings_count} wrn"

            if not r.install_result or r.install_result.status == "SKIPPED":
                inst = "SKIPPED"
            elif r.install_result.status == "PASS":
                inst = f"PASS ({r.install_result.duration_seconds}s)"
            else:
                inst = "FAIL ❌"

            verdict = r.overall_status
            if verdict == "SUCCESS":
                verdict_str = "✅ SUCCESS"
            elif verdict == "ACTION_NEEDED":
                verdict_str = "⚠️ ACTION"
            else:
                verdict_str = "❌ FAILED"

            row = f"{r.module_name[:19]:<20} | {ver:<10} | {files:<12} | {ast_stat:<12} | {inst:<14} | {verdict_str:<12}"
            print(row)

        print("=" * 90)
