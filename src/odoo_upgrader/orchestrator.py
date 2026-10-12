"""Orchestrates the complete Odoo upgrade and validation pipeline."""

import os
from pathlib import Path
from typing import List, Optional

from .detector import VersionDetector, OdooModuleInfo
from .utils import create_backup
from .precheck import OdooPreChecker
from .transforms import ManifestUpgrader, XmlTransforms, PyTransforms, JsTransforms
from .static_checks import StaticAnalysisEngine
from .installer import OdooAppInstaller, InstallTestResult
from .reporting import ModuleUpgradeResult, UpgradeReporter


class UpgradeOrchestrator:
    """End-to-end upgrade pipeline coordinator."""

    def __init__(
        self,
        target_path: str | Path,
        target_version: int = 19,
        backup: bool = True,
        test_install: bool = False,
        db_name: Optional[str] = None,
        odoo_bin_path: Optional[str] = None,
        config_path: Optional[str] = None,
        addons_paths: Optional[List[str]] = None,
        ruleset_path: Optional[Path] = None,
    ):
        self.target_path = Path(target_path).resolve()
        self.target_version = target_version
        self.backup = backup
        self.test_install = test_install
        self.db_name = db_name
        self.odoo_bin_path = odoo_bin_path
        self.config_path = config_path
        self.addons_paths = addons_paths or []
        self.ruleset_path = ruleset_path

        self.static_engine = StaticAnalysisEngine(ruleset_path=self.ruleset_path)
        self.installer = OdooAppInstaller(
            odoo_bin_path=self.odoo_bin_path,
            db_name=self.db_name,
            config_path=self.config_path,
            addons_paths=self.addons_paths,
        )

    def run(self) -> List[ModuleUpgradeResult]:
        """Execute detection, transforms, static checks, installation tests, and reporting."""
        print(f"\n🚀 Starting Odoo Upgrade Pipeline for: {self.target_path}")
        print(f"Target Odoo Version: v{self.target_version}")
        print("=" * 80)

        # 1. Detection
        detector = VersionDetector(self.target_path, target_version=self.target_version)
        modules = detector.find_modules()

        if not modules:
            print(f"⚠️ No Odoo modules with manifests found in {self.target_path}")
            return []

        print(f"📦 Detected {len(modules)} module(s): {', '.join(m.name for m in modules)}")

        results: List[ModuleUpgradeResult] = []

        for mod in modules:
            res = self._upgrade_single_module(mod)
            results.append(res)

        # Render reports
        reporter = UpgradeReporter(results)
        report_file = reporter.generate_markdown_report()
        reporter.print_terminal_summary()

        print(f"\n📄 Full diagnostic report saved to: {report_file}")
        return results

    def _upgrade_single_module(self, mod: OdooModuleInfo) -> ModuleUpgradeResult:
        print(f"\n>>> Processing Module: {mod.name} (Detected source: v{mod.detected_source_version})")

        # 1. Backup
        backup_path_str = None
        if self.backup:
            try:
                b_path = create_backup(mod.path)
                backup_path_str = str(b_path)
                print(f"  [1/5] Backup created at: {b_path.name}")
            except Exception as e:
                print(f"  [1/5] ⚠️ Backup failed: {e}")

        # 2. Pre-check
        print(f"  [2/5] Running pre-upgrade compatibility scan...")
        prechecker = OdooPreChecker(mod.path, target_version=self.target_version)
        pre_results = prechecker.run()
        crit_count = pre_results.get("critical", 0)
        tot_count = pre_results.get("total", 0)
        print(f"        Pre-check: {tot_count} issues found ({crit_count} critical)")

        # 3. Transforms
        print(f"  [3/5] Applying AST, XML, JS, and Manifest transforms...")
        manifest_up = ManifestUpgrader(self.target_version)
        manifest_updated = manifest_up.process_module(mod.manifest_path)

        xml_trans = XmlTransforms(mod.path, target_version=self.target_version)
        xml_res = xml_trans.apply_all()
        xml_count = sum(xml_res.values())

        py_trans = PyTransforms(mod.path, target_version=self.target_version)
        py_res = py_trans.apply_all()
        py_count = sum(py_res.values())

        js_trans = JsTransforms(mod.path, target_version=self.target_version)
        js_res = js_trans.apply_all()
        js_count = sum(js_res.values())

        print(f"        Modified: XML={xml_count}, Python={py_count}, JS={js_count}, Manifest={manifest_updated}")

        # 4. Static Validation (YAML ruleset)
        print(f"  [4/5] Executing static AST rule checks...")
        rule_matches = self.static_engine.analyze_module(mod.path)
        blockers = sum(1 for m in rule_matches if m.severity in ("blocking", "error"))
        print(f"        Static rules: {len(rule_matches)} matches ({blockers} blocking)")

        # 5. Dynamic App Install Test
        install_res: Optional[InstallTestResult] = None
        if self.test_install or self.db_name:
            print(f"  [5/5] Testing dynamic app installation with odoo-bin...")
            install_res = self.installer.test_install(
                module_name=mod.name,
                module_path=mod.path,
                db_name=self.db_name,
            )
            print(f"        Install Test: {install_res.status} ({install_res.duration_seconds}s)")
            if install_res.status == "FAIL":
                print(f"        ❌ Error: {install_res.error_summary}")
        else:
            print(f"  [5/5] Skipping dynamic app install (pass --test-install --db <db> to enable)")

        return ModuleUpgradeResult(
            module_name=mod.name,
            source_version=mod.detected_source_version,
            target_version=self.target_version,
            backup_path=backup_path_str,
            manifest_updated=manifest_updated,
            xml_files_modified=xml_count,
            py_files_modified=py_count,
            js_files_modified=js_count,
            precheck_total_issues=tot_count,
            precheck_critical_issues=crit_count,
            static_matches=rule_matches,
            install_result=install_res,
        )
