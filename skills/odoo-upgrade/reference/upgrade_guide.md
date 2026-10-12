# Odoo Upgrade Guide (v14 - v19)

## XML/View Transformations
### Tree to List (Odoo 19)
`<!-- Tags -->        <tree> -> <list>,  </tree> -> </list>`
`<!-- view_mode -->   tree,form -> list,form`
`<!-- XPath -->       //tree -> //list`

### Search Views (Odoo 19)
Remove `<group>` tags - place filters at root level. Add `<separator/>` before group_by filters.

### Kanban Templates (Odoo 19)
`t-name="kanban-box"` -> `t-name="card"`. Remove `js_class="crm_kanban"`.

### Cron Jobs (Odoo 19)
Remove `<field name="numbercall">` - field no longer exists.

### Form View Context (Odoo 19)
`active_id` -> `id` in context expressions.

### Snippet Options (Odoo 19)
Remove templates inheriting `website.snippet_options` - system redesigned.

### Attrs to Inline (Odoo 18/19)
`attrs="{'invisible': [('state','=','draft')]}"` -> `invisible="state == 'draft'"`

## Python API Migrations
### Slug/Unslug (Odoo 18+)
`# New: use request.env['ir.http']._slug(value)`

### URL For (Odoo 19)
`# New: self.env['ir.http']._url_for('/path')`

### Controller Type (Odoo 19)
`type='json'` -> `type='jsonrpc'` in `@http.route` decorators.

## JavaScript/OWL Migrations
### RPC Service (Odoo 19)
RPC service is NOT available in frontend/public components. Replace `useService("rpc")` with a `_jsonRpc` helper method using the fetch API.

### OWL Lifecycle Hooks (Odoo 18+)
OWL 1.x -> OWL 2.0 (`constructor` -> `setup()`, `willStart` -> `onWillStart()`, etc.)

## Bootstrap 4 to 5 Class Migration
Bootstrap 4 classes like `ml-*`/`mr-*` map to `ms-*`/`me-*` in Bootstrap 5 (Odoo 15+).

## Data Migration Scripts
Place migration scripts under `module/migrations/VERSION/`.
- `pre-migrate.py` - Before ORM update (SQL only)
- `post-migrate.py` - After ORM update
- `end-migrate.py` - After all modules updated
