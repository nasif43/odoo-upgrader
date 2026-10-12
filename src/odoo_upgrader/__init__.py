"""odoo-upgrader: Unified Odoo ERP module upgrade and validation toolkit."""

__version__ = "1.0.0"

from .detector import VersionDetector, OdooModuleInfo
from .orchestrator import UpgradeOrchestrator
from .installer import OdooAppInstaller, InstallTestResult
from .reporting import UpgradeReporter, ModuleUpgradeResult

__all__ = [
    "VersionDetector",
    "OdooModuleInfo",
    "UpgradeOrchestrator",
    "OdooAppInstaller",
    "InstallTestResult",
    "UpgradeReporter",
    "ModuleUpgradeResult",
]
