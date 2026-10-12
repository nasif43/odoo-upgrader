---
name: odoo-upgrade
description: |
  Comprehensive Odoo ERP upgrade assistant for migrating modules between Odoo versions (14-19). Handles XML views, Python API changes, JavaScript/OWL components, theme SCSS variables, manifest updates, security implementations, and database migrations. Use when user asks to upgrade Odoo modules, fix version compatibility issues, migrate themes between versions, or resolve Odoo 17/18/19 migration errors.
license: "MIT"
---

# Odoo Upgrade Assistant v5.0

## When to Use
Activate when upgrading Odoo modules between versions (14-19), fixing version compatibility errors, migrating themes, or resolving RPC service errors in the frontend. 

## Upgrade Workflow
1. **Analyze** - Read `__manifest__.py`, identify source version, scan files.
2. **Pre-check** - Run `scripts/cli.py precheck <path> --target <version>` to identify all issues.
3. **Transform** - Apply transforms.
4. **Validate** - Run `scripts/cli.py validate <path>` to check syntax.

## References
Detailed migration mappings and data script patterns are available in the references.
Always check these when migrating:
- [General Upgrade Guide](./reference/upgrade_guide.md)
- [Odoo 18 to 19 Patterns](./reference/odoo18_to_19.md)
- [Error Catalog](./reference/error_catalog.md)
