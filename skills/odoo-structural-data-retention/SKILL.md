---
name: odoo-structural-data-retention
description: A specialized workflow and script generator for migrating legacy Odoo databases (e.g., v14 to v19) where the client wants to retain structural data (fields, models) and views for historical reporting, but strip out complex, outdated Python workflows and business logic to prevent technical debt. Use this skill whenever a user mentions "middle ground migration", "retaining data without workflows", "dummy modules", or "migrating compute fields".
---

# Odoo Structural Data & View Retention Strategy

This skill guides you through migrating legacy Odoo data by separating the data schema and presentation layers from the behavioral logic layer. Instead of scaffolding new blank modules, this strategy revolves around **retaining the actual legacy custom modules** and surgically modifying them to work in the newer Odoo version.

It allows historical data to be safely preserved (and viewed) in newer Odoo versions without carrying over broken, processor-heavy Python workflows.

## Phase 1: Comprehensive Schema & Field Audit

**Goal:** Identify all custom models, fields (both stored and computed), and their dependencies in the currently installed custom modules.

### Step 1: Check Installed Modules
Identify which custom modules are actively installed in the database.
```bash
psql -d <db_name> -t -c "SELECT name FROM ir_module_module WHERE state='installed';"
```

### Step 2: Locate Modules in Addons Directories
Cross-reference the installed modules with the custom addons directories to isolate the client's specific custom code. Note: Odoo Core and Enterprise modules should be ignored here, as standard Odoo migration scripts handle their data retention natively.

### Step 3: Extract Models, Fields, and Compute Dependencies
Use an AST (Abstract Syntax Tree) parsing script in Python to extract the following from the installed non-core modules:
1. **Model Declarations:** `_name` and `_inherit`.
2. **Module Names:** The exact name of the specific module each model and field belongs to.
3. **Fields:** All custom fields and their attributes (crucially, `store=True/False`).
4. **Compute Dependencies:** For `compute=` fields, capture both explicit dependencies (from `@api.depends`) and implicit dependencies accessed in the method body.
5. **Compute Source Code:** Extract the raw Python source code for the compute methods so they can be retained later if deemed safe.

*(A sample script `extract_fields.py` should be used for this step to output a `field_audit_report.json`)*

## Phase 2: Module Retention & Python Commenting

**Goal:** Keep the original module structure but surgically comment out outdated business logic to preserve it for future investigation.

1. **Copy Legacy Modules:** Copy the physical directories of the identified active custom/OCA modules from the legacy source path into your target migration path (e.g., `odoo19_custom`).
2. **Analyze Computes for V19 Portability:**
   - **Stored Fields (`store=True`):** The data is already in PostgreSQL. Keep the field definitions but you can often drop the heavy compute logic if it's no longer needed for new records.
   - **Safe Non-Stored Fields:** If the compute dependencies still exist structurally in the new Odoo version, retain the original Python compute code.
   - **Broken Non-Stored Fields:** If the compute method relies on fields/models that Odoo removed (e.g., `move_lines` renaming to `move_ids`), flag these for manual code rewrites.
3. **Deactivate Workflows (The Comment-Out):** Manually or programmatically iterate through the `models/*.py` files inside the copied modules.
   - **Retain:** All class definitions (`_name`, `_inherit`) and field definitions (`fields.Char`, etc.).
   - **Retain:** Safe `compute` methods (and patch the broken ones).
   - **Comment Out:** All custom workflow logic instead of deleting it. This includes method overrides (`def create`, `def write`, `def action_post`), all `@api.onchange` decorators, and custom buttons/action logic that intercept standard Odoo flows. This preserves the code for future investigation.

**Result:** You now possess the original modules, but they only contain the data schema and the necessary logic to calculate display fields. They are completely stripped of the technical debt that would otherwise break the new Odoo version.

## Phase 3: View & Report Upgrades

**Goal:** Ensure the client can still view their historical data in the new system's UI perfectly.

1. **Migrate Form & List Views:** Iterate through the XML files in the copied modules. Upgrade their syntax to the target version's standards. For example, converting legacy v14 `attrs` and `states` to modern string-based boolean expressions (`invisible="..."`, `readonly="..."`), and updating OWL widget references.
2. **Migrate Reports:** Upgrade QWeb templates so historical PDFs and documents can still be printed exactly as they were in the legacy system.

**Result:** When the database upgrade engine runs, the custom modules will install cleanly. When the client logs into the new version, they can open an old invoice, see all their custom fields, and print their reports, allowing you to confidently prove that the data migration was a 100% success.