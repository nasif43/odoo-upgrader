"""Dynamic Odoo app installation tester.

Tests whether upgraded modules actually install without crashing the Odoo server.
Captures tracebacks, log errors, and returns a structured install test result.
"""

import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel


class InstallTestResult(BaseModel):
    module_name: str
    status: str  # "PASS" | "FAIL" | "SKIPPED"
    exit_code: int = 0
    duration_seconds: float = 0.0
    error_summary: Optional[str] = None
    log_output: str = ""


class OdooAppInstaller:
    """Executes dynamic installation tests using odoo-bin."""

    ERROR_PATTERN = re.compile(
        r"(?:ERROR|CRITICAL)\s+[\w\.\-]+:\s+(.+)",
        re.IGNORECASE
    )
    TRACEBACK_PATTERN = re.compile(
        r"(Traceback \(most recent call last\):[\s\S]+?(?:\w+Error|\w+Exception):[^\n]+)",
        re.MULTILINE
    )

    COMMON_ODOO_BIN_PATHS = [
        "/home/muhts/dev/Codes/metamorphosis/odoo/odoo/odoo-bin",
        "/opt/odoo/odoo-bin",
        "/usr/bin/odoo-bin",
        "/usr/local/bin/odoo-bin",
    ]

    def __init__(
        self,
        odoo_bin_path: Optional[str] = None,
        db_name: Optional[str] = None,
        config_path: Optional[str] = None,
        addons_paths: Optional[List[str]] = None,
    ):
        self.odoo_bin_path = self._resolve_odoo_bin(odoo_bin_path)
        self.db_name = db_name
        self.config_path = config_path
        self.addons_paths = addons_paths or []

    def _resolve_odoo_bin(self, explicit_path: Optional[str]) -> Optional[str]:
        if explicit_path and Path(explicit_path).exists():
            return str(Path(explicit_path).resolve())

        which_path = shutil.which("odoo-bin")
        if which_path:
            return which_path

        for candidate in self.COMMON_ODOO_BIN_PATHS:
            p = Path(candidate).expanduser()
            if p.is_file() and os.access(p, os.X_OK):
                return str(p)

        return None

    def is_available(self) -> bool:
        return self.odoo_bin_path is not None

    def test_install(
        self,
        module_name: str,
        module_path: Path,
        db_name: Optional[str] = None,
        timeout: int = 180,
    ) -> InstallTestResult:
        if not self.is_available():
            return InstallTestResult(
                module_name=module_name,
                status="SKIPPED",
                exit_code=0,
                error_summary="odoo-bin not found in PATH or standard locations.",
            )

        target_db = db_name or self.db_name
        if not target_db:
            return InstallTestResult(
                module_name=module_name,
                status="SKIPPED",
                exit_code=0,
                error_summary="No database specified for dynamic install test (use --db <name>).",
            )

        # Collect addons paths
        effective_addons = list(self.addons_paths)
        module_parent = str(module_path.parent.resolve())
        if module_parent not in effective_addons:
            effective_addons.append(module_parent)

        cmd = [
            self.odoo_bin_path,
            "-d", target_db,
            "-i", module_name,
            "--stop-after-init",
            "--no-http",
            "--log-level=warn",
        ]
        if effective_addons:
            cmd.extend(["--addons-path", ",".join(effective_addons)])
        if self.config_path and Path(self.config_path).exists():
            cmd.extend(["-c", self.config_path])

        start_time = time.time()
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
            )
            duration = round(time.time() - start_time, 2)
            log = res.stdout or ""

            if res.returncode == 0 and not self._has_critical_log_errors(log):
                return InstallTestResult(
                    module_name=module_name,
                    status="PASS",
                    exit_code=0,
                    duration_seconds=duration,
                    log_output=log,
                )
            else:
                error_sig = self._extract_error_summary(log, res.returncode)
                return InstallTestResult(
                    module_name=module_name,
                    status="FAIL",
                    exit_code=res.returncode or -1,
                    duration_seconds=duration,
                    error_summary=error_sig,
                    log_output=log,
                )

        except subprocess.TimeoutExpired:
            return InstallTestResult(
                module_name=module_name,
                status="FAIL",
                exit_code=-2,
                duration_seconds=timeout,
                error_summary=f"Installation timed out after {timeout}s.",
            )
        except Exception as e:
            return InstallTestResult(
                module_name=module_name,
                status="FAIL",
                exit_code=-3,
                duration_seconds=0.0,
                error_summary=f"Failed to execute odoo-bin: {str(e)}",
            )

    def _has_critical_log_errors(self, log: str) -> bool:
        for line in log.splitlines():
            if " ERROR " in line or " CRITICAL " in line:
                return True
        return False

    def _extract_error_summary(self, log: str, returncode: int) -> str:
        # Check for python traceback first
        tb_match = self.TRACEBACK_PATTERN.findall(log)
        if tb_match:
            last_tb = tb_match[-1].strip()
            # Return last 3 lines of traceback for concise summary
            lines = [l.strip() for l in last_tb.splitlines() if l.strip()]
            return " | ".join(lines[-2:]) if len(lines) >= 2 else lines[-1]

        # Check for Odoo structured error lines
        errors = self.ERROR_PATTERN.findall(log)
        if errors:
            return errors[-1].strip()

        # Fallback to last non-empty lines of log
        lines = [l.strip() for l in log.splitlines() if l.strip()]
        if lines:
            return lines[-1]

        return f"Process failed with exit code {returncode}"
