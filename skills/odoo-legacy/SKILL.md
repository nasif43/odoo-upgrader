---
name: odoo-legacy
description: Expert knowledge for legacy Odoo versions (12.0 to 15.0). Use this skill strictly when the user is maintaining, bug fixing, or dealing with older Odoo codebases. Covers older ORM patterns, Python 3.6-3.8 constraints, classic JS widget framework (pre-OWL), and legacy XML view syntax.
---

# Odoo Legacy (v12 - v15) Development Guide

This skill is designed to prevent context bleed from modern Odoo implementations (v17+) into older client databases.

## Usage Instructions
1. **Verify Version:** Check if the project has a `.odoo-version` file or ask the user to confirm the target version.
2. **Restrict Patterns:** Do NOT use OWL, modern decorators (like `@api.ondelete`), or inline tree view `invisible="1"` attributes if working on v12-v15.
3. **Legacy JS:** Remember to use the `web.Widget` and `web.core` registry instead of OWL components.
4. **Python Compatibility:** Ensure code respects older Python version constraints common to these deployments.

## Core Legacy Differences to Remember
*   **Views:** In older versions, `attrs="{'invisible': [('field', '=', False)]}"` is the standard. Inline `invisible="..."` boolean evaluation is a newer feature.
*   **Javascript:** Use `odoo.define('module.name', function (require) { ... })` and extending widgets instead of OWL classes and templates.
*   **ORM:** `_sql_constraints` are standard; `models.Constraint` is modern. Be cautious with `read_group` limitations in older versions compared to newer ones.
