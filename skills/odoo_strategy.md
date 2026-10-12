# Odoo Agent Skills Optimization Strategy

## Context & Objectives
Niaj Shishir (Head of Technology, Metamorphosis Ltd) requires an agent configuration optimized for:
1. **Modern Odoo Development (v18+)**: High-performance, clean implementations.
2. **Legacy Odoo Support (v12+)**: Bug fixing and maintaining older client databases.
3. **Complex Upgrades (v12 -> v18+)**: Bridging the gap between legacy and modern APIs.
4. **VPS Performance**: Checking and tuning infrastructure.

**The Problem:** The current `.agents/skills` directory contains multiple overlapping Odoo skills (`odoo`, `odoo-development`, `odoo-orm-expert`, `odoo-19`, `odoo-upgrade`). This causes:
- **Skill Conflicts:** The agent's system prompt gets bloated with overlapping triggers.
- **Context Confusion:** The agent applies modern OWL/ORM patterns to v12 codebases, or legacy patterns to v19 codebases.
- **Token Inefficiency:** Large, bloated SKILL.md files (e.g., `odoo`, `odoo-upgrade`, `odoo-commit-message-guidelines` are 170-220+ lines long).

## Execution Plan

### 1. Archiving Redundancies
Move the following to an `archive` directory to remove them from the active discovery path, eliminating trigger overlap:
- `odoo`
- `odoo-development`
- `odoo-orm-expert`

### 2. Creating Explicit Version Boundaries
- **`odoo-legacy` (New)**: Focused strictly on Odoo 12-15 APIs, older XML syntax, Python 3.6/3.7 constraints, and older JS frameworks.
- **`odoo-19` (Keep)**: Focused on modern Odoo (v17-v19), OWL, new ORM.
- **Version Sensing Mechanism**: Advise the user to place `.odoo-version` files in project roots. The agent will read this file to determine whether to consult `odoo-legacy` or `odoo-19`.

### 3. Pruning Bloat
Reduce the line count and token weight of remaining active skills:
- **`odoo-upgrade`**: Simplify the SKILL.md, move heavy reference content to a `references/` folder.
- **`odoo-commit-message-guidelines`**: Make the prompt much shorter and punchier.
- **`odoo-19`**: Ensure its triggers are strictly scoped to modern versions.

### 4. Specialization Retention
Keep the following specific tools active as they serve distinct operational needs without confusing the development context:
- `odoo-server-tuner`
- `odoo-upgrade` (Optimized)
