"""Command-line interface for odoo-upgrader."""

import sys
import argparse
from pathlib import Path

from .orchestrator import UpgradeOrchestrator
from .precheck import OdooPreChecker
from .validate import SyntaxValidator
from .installer import OdooAppInstaller


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odoo-upgrader",
        description="Unified Odoo Module Upgrade, Transformation, and Validation Toolkit",
    )
    parser.add_argument("path", nargs="?", default=".", help="Path to Odoo module or addons repository (default: current directory)")
    parser.add_argument("--target", type=int, default=19, choices=[14, 15, 16, 17, 18, 19, 20], help="Target Odoo version (default: 19)")
    parser.add_argument("--test-install", action="store_true", default=True, help="Execute live installation test with odoo-bin (default: enabled if odoo-bin is found)")
    parser.add_argument("--skip-install", action="store_true", help="Skip dynamic installation test (static analysis & transforms only)")
    parser.add_argument("--db", type=str, default=None, help="PostgreSQL database name for test installation (default: auto-detected)")
    parser.add_argument("--odoo-bin", type=str, default=None, help="Explicit path to odoo-bin executable (default: auto-detected)")
    parser.add_argument("--config", "-c", type=str, default=None, help="Path to odoo.conf configuration file (default: auto-detected)")
    parser.add_argument("--addons-path", type=str, default=None, help="Comma-separated addons paths for odoo-bin")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup copies before making changes")
    parser.add_argument("--dry-run", action="store_true", help="Scan and detect issues without writing changes")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}")
        sys.exit(1)

    if args.dry_run:
        print(f"🔍 [DRY-RUN] Running pre-check scan on {target_path} for target v{args.target}...")
        checker = OdooPreChecker(target_path, target_version=args.target)
        results = checker.run()
        crit = results.get("critical", 0)
        tot = results.get("total", 0)
        print(f"\nDry-run complete. Found {tot} issues ({crit} critical). No files were modified.")
        sys.exit(1 if crit > 0 else 0)

    addons_list = [p.strip() for p in args.addons_path.split(",")] if args.addons_path else []

    orchestrator = UpgradeOrchestrator(
        target_path=target_path,
        target_version=args.target,
        backup=not args.no_backup,
        test_install=not args.skip_install,
        skip_install=args.skip_install,
        db_name=args.db,
        odoo_bin_path=args.odoo_bin,
        config_path=args.config,
        addons_paths=addons_list,
    )

    results = orchestrator.run()

    # Determine exit code based on blockers
    has_failure = any(r.overall_status == "FAILED" for r in results)
    sys.exit(1 if has_failure else 0)


if __name__ == "__main__":
    main()
