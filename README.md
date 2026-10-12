# 🚀 Odoo Upgrader (`odoo-upgrader`)

> **Autonomous Odoo ERP Module Upgrade, AST Transformation, and Live Validation Pipeline**  
> Designed for human developers and autonomous AI coding agents (**Antigravity**, **Claude Code**, **Gemini**, **Cursor**).

---

## 🌟 Overview

`odoo-upgrader` is a portable, end-to-end framework to upgrade custom Odoo modules across major versions (e.g., **18 → 19** or **19 → 20**).

It bundles:
1. **The Core Python CLI Engine (`odoo-upgrader` / `upgrade-odoo`)**: Automatically analyzes module source versions, creates safety backups, applies AST/XML/Python/JS transforms, runs static rule checks, and performs live database installation tests via `odoo-bin`.
2. **Autonomous Agent Skills (`/upgrade-odoo`, `/odoo-19`, `/odoo-upgrade`, etc.)**: Portable skills compatible with Antigravity, Claude Code, Gemini CLI, and Cursor that enable an agent to independently study the module, execute the upgrade, debug tracebacks, and present a clear diagnostic table.
3. **Diagnostic Reporting**: Generates a clear terminal and Markdown summary table detailing what went right, what went wrong, and recommended action items.

---

## 📥 Quick Start (For You & Your Team)

### Step 1: Clone the Repository
```bash
git clone git@github.com:metamorphosis/odoo-upgrader.git
cd odoo-upgrader
```

### Step 2: Run the One-Click Installer
```bash
./install.sh
```
This script will:
- Install the `odoo-upgrader` Python package in editable mode (`pip install -e .`).
- Register all migration skills to `~/.agents/skills/` (recognized automatically by **Claude Code**, **Antigravity**, and **Gemini**).
- Configure Cursor IDE rules (`.cursorrules` and `.cursor/rules/upgrade-odoo.mdc`).

---

## 🤖 How to Use with AI Coding Agents

### In Antigravity, Claude Code, or Gemini CLI
Simply run the slash command and provide the path to your Odoo module or addons repository:

```text
/upgrade-odoo /path/to/your/custom_addons
```

Or specify a target version and test database:
```text
/upgrade-odoo /path/to/your/custom_addons --target 19 --db test_odoo19_db
```

#### What the Agent Will Do:
1. **Study Source Code**: Inspects `__manifest__.py`, detected ORM patterns, and XML view types to determine the original version.
2. **Run Transforms**: Converts `<tree>` to `<list>`, updates `attrs`/`states` to modern expressions, migrates `_sql_constraints` to `models.Constraint`, and updates frontend OWL bindings.
3. **Execute Static Validation**: Checks against official YAML rule catalogs (`ruleset/odoo_18_19_rules.yaml`).
4. **Test Dynamic App Installation**: Attempts to install the module on a running Odoo system using `odoo-bin`. If a traceback occurs, the agent reads the error from the report, consults the reference catalog, and fixes the issue.
5. **Output Overview Table**: Presents a clean summary table of the entire run.

---

## 💻 How to Use from the Terminal CLI (Without AI)

You can also run the pipeline directly from your bash shell:

### 1. Dry Run (Scan only, no files modified)
```bash
upgrade-odoo /path/to/your/addons --target 19 --dry-run
```

### 2. Full Upgrade with Code Transforms & Static Checks
```bash
upgrade-odoo /path/to/your/addons --target 19
```

### 3. Full Upgrade with Live App Installation Test
```bash
upgrade-odoo /path/to/your/addons --target 19 --test-install --db my_v19_test_db
```

#### CLI Options:
| Flag | Description | Default |
|---|---|---|
| `path` | Path to module or addons folder | Current directory (`.`) |
| `--target` | Target Odoo version (`14` through `20`) | `19` |
| `--test-install` | Run live install verification with `odoo-bin` | `False` |
| `--db` | PostgreSQL test database name | `None` |
| `--odoo-bin` | Explicit path to `odoo-bin` executable | Auto-detected |
| `--addons-path` | Extra comma-separated addons paths for `odoo-bin` | Auto-detected |
| `--dry-run` | Scan and report issues without modifying files | `False` |
| `--no-backup` | Skip creating timestamped backups | `False` |

---

## 📊 Summary & Diagnostic Report

Upon completion, `odoo-upgrader` outputs both a terminal table and a full Markdown report saved to `./upgrade_reports/upgrade_report_<timestamp>.md`.

### Example Overview Table:
```text
==========================================================================================
                 ODOO UPGRADE SUMMARY & VERDICT TABLE
==========================================================================================
Module               | Version    | Files Mod    | Static AST   | Install Test   | Verdict     
------------------------------------------------------------------------------------------
custom_crm           | v18->v19   | 5 files      | 0 blk / 1 wrn| PASS (3.4s)    | ✅ SUCCESS   
legacy_invoice_ext   | v16->v19   | 8 files      | 2 blk / 0 wrn| FAIL ❌        | ❌ FAILED    
==========================================================================================
```

### The Detailed Breakdown:
* **✅ What Went Right**:
  - Exact counts of XML, Python, and JavaScript files modified.
  - Manifest updated to target series (`19.0.1.0.0`).
  - Confirmation of clean backup location.
* **⚠️ What Went Wrong & Action Items**:
  - Static AST blocker rules that require manual attention.
  - Live install tracebacks (showing exact Python traceback and line numbers).
  - Recommended fixes from the bundled reference library.

---

## 🧠 Bundled Reference Skills

The repository includes a self-contained library in `./skills/`:

| Skill | Description |
|---|---|
| [`upgrade-odoo`](./skills/upgrade-odoo/SKILL.md) | **Master Chained Skill**: Drives autonomous agents through the 5-step upgrade loop. |
| [`odoo-19`](./skills/odoo-19/SKILL.md) | **18 Deep Architectural Guides**: Covers Actions, Controllers, Decorators, Fields, OWL, Reports, Views, Testing, and Migrations for Odoo 19. |
| [`odoo-upgrade`](./skills/odoo-upgrade/SKILL.md) | Toolkit reference and error catalog (`error_catalog.md`, `odoo18_to_19.md`). |
| [`odoo-structural-data-retention`](./skills/odoo-structural-data-retention/SKILL.md) | Strategy for retaining historical schemas/views while stripping broken business workflows. |
| [`odoo-legacy`](./skills/odoo-legacy/SKILL.md) | Reference boundary for legacy versions (12–15) to prevent modern syntax bleed. |
| [`odoo-server-tuner`](./skills/odoo-server-tuner/SKILL.md) | Anti-deadlock worker allocation and RAM tuning for production servers. |

---

## 👥 Training a Colleague: Recommended Workflow

1. **Step 1:** Have them clone this repository and run `./install.sh`.
2. **Step 2:** Instruct them to point the tool at their custom addons directory:
   ```bash
   /upgrade-odoo /path/to/custom_addons
   ```
3. **Step 3:** Review the resulting **Summary Table**.
4. **Step 4:** If the module fails the live install test, look at the **Detailed Diagnostics** section of the generated report to inspect the traceback. Use the guides in `skills/odoo-19/references/` to apply the recommended pattern.
5. **Step 5:** Re-test until the install column displays `✅ Pass`.
