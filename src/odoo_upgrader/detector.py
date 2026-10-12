"""Module and version detection for Odoo projects."""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class OdooModuleInfo(BaseModel):
    name: str
    path: Path
    manifest_path: Path
    declared_version: Optional[str] = None
    detected_source_version: int = 18
    target_version: int = 19
    depends: List[str] = Field(default_factory=list)
    xml_files: List[Path] = Field(default_factory=list)
    py_files: List[Path] = Field(default_factory=list)
    js_files: List[Path] = Field(default_factory=list)
    has_models: bool = False
    has_views: bool = False
    has_frontend: bool = False


class VersionDetector:
    """Scans directories, detects Odoo modules, and infers source versions."""

    VERSION_SERIES_REGEX = re.compile(r"^(\d+)\.0")
    SKIP_DIRS = {
        ".git", ".venv", "venv", "node_modules", "__pycache__",
        ".pytest_cache", ".idea", ".vscode", "backup", ".backup"
    }

    def __init__(self, root_path: str | Path, target_version: int = 19):
        self.root_path = Path(root_path).resolve()
        self.target_version = target_version

    def find_modules(self) -> List[OdooModuleInfo]:
        """Find all Odoo modules in the given directory or handle a single module directory."""
        modules = []

        # Check if root itself is a module
        root_manifest = self._find_manifest(self.root_path)
        if root_manifest:
            modules.append(self._parse_module(self.root_path, root_manifest))
            return modules

        # Search child directories
        for path in self.root_path.rglob("*"):
            if not path.is_dir() or any(skip in path.parts for skip in self.SKIP_DIRS):
                continue

            manifest = self._find_manifest(path)
            if manifest:
                modules.append(self._parse_module(path, manifest))

        return modules

    def _find_manifest(self, folder: Path) -> Optional[Path]:
        for name in ("__manifest__.py", "__openerp__.py"):
            candidate = folder / name
            if candidate.is_file():
                return candidate
        return None

    def _parse_module(self, folder: Path, manifest_path: Path) -> OdooModuleInfo:
        manifest_data = self._read_manifest(manifest_path)
        declared_ver = manifest_data.get("version")
        detected_ver = self._detect_source_version(folder, declared_ver)

        xml_files = [f for f in folder.rglob("*.xml") if not any(skip in f.parts for skip in self.SKIP_DIRS)]
        py_files = [f for f in folder.rglob("*.py") if not any(skip in f.parts for skip in self.SKIP_DIRS) and f.name != "__manifest__.py"]
        js_files = [f for f in folder.rglob("*.js") if not any(skip in f.parts for skip in self.SKIP_DIRS)]

        return OdooModuleInfo(
            name=folder.name,
            path=folder,
            manifest_path=manifest_path,
            declared_version=str(declared_ver) if declared_ver else None,
            detected_source_version=detected_ver,
            target_version=self.target_version,
            depends=manifest_data.get("depends", []),
            xml_files=xml_files,
            py_files=py_files,
            js_files=js_files,
            has_models=len([f for f in py_files if "models" in f.parts]) > 0 or len(py_files) > 1,
            has_views=len(xml_files) > 0,
            has_frontend=len(js_files) > 0,
        )

    def _read_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        try:
            content = manifest_path.read_text(encoding="utf-8")
            return ast.literal_eval(content)
        except Exception:
            # Fallback regex parsing if literal_eval fails
            data: Dict[str, Any] = {}
            try:
                content = manifest_path.read_text(encoding="utf-8")
                ver_match = re.search(r'["\']version["\']\s*:\s*["\']([^"\']+)["\']', content)
                if ver_match:
                    data["version"] = ver_match.group(1)
                dep_match = re.search(r'["\']depends["\']\s*:\s*\[([^\]]*)\]', content)
                if dep_match:
                    deps = [d.strip().strip("'\"") for d in dep_match.group(1).split(",") if d.strip()]
                    data["depends"] = deps
            except Exception:
                pass
            return data

    def _detect_source_version(self, folder: Path, declared_version: Optional[str]) -> int:
        """Infer the source Odoo version from declared version or code heuristics."""
        if declared_version:
            m = self.VERSION_SERIES_REGEX.match(str(declared_version).strip())
            if m:
                try:
                    return int(m.group(1))
                except ValueError:
                    pass
            parts = str(declared_version).split(".")
            if parts and parts[0].isdigit():
                return int(parts[0])

        # Check for .odoo-version file
        odoo_ver_file = folder / ".odoo-version"
        if odoo_ver_file.exists():
            try:
                ver_text = odoo_ver_file.read_text().strip()
                return int(float(ver_text))
            except Exception:
                pass

        # Code Heuristics
        for xml_file in folder.rglob("*.xml"):
            try:
                txt = xml_file.read_text(encoding="utf-8", errors="ignore")
                if "<tree" in txt and "</tree>" in txt:
                    # <tree> was used up to v17/v18 before being renamed to <list> in v18/v19
                    return 18
            except Exception:
                pass

        # Default fallback
        return self.target_version - 1
