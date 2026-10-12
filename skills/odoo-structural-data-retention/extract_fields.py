import ast
import os
import json

# Define the path to the custom addons and the list of installed modules
addons_path = "/home/niaj/odoo/precisiontex-qd-global/studio73/qdglobal-addons"
installed_modules_file = "/home/niaj/Documents/PrecisionTex-Odoo/installed_modules.txt"

# Read installed modules
with open(installed_modules_file, "r") as f:
    installed_modules = set(line.strip() for line in f if line.strip())

# Find custom installed modules
custom_modules = [
    d for d in os.listdir(addons_path)
    if os.path.isdir(os.path.join(addons_path, d)) and d in installed_modules
]

print(f"Found {len(custom_modules)} installed custom modules in {addons_path}.")

class OdooASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.models = {}
        self.current_model = None

    def visit_ClassDef(self, node):
        # We assume classes might be Odoo models if they have _inherit or _name
        model_name = None
        inherit_name = None
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id == '_name' and isinstance(item.value, ast.Constant):
                            model_name = item.value.value
                        elif target.id == '_inherit' and isinstance(item.value, ast.Constant):
                            inherit_name = item.value.value

        self.current_model = model_name or inherit_name
        if self.current_model:
            if self.current_model not in self.models:
                self.models[self.current_model] = {'fields': {}, 'methods': {}}
            self.generic_visit(node)
        self.current_model = None

    def visit_Assign(self, node):
        if not self.current_model:
            return
        
        # Look for field definitions: my_field = fields.Char(...)
        for target in node.targets:
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == 'fields':
                    field_name = target.id
                    field_type = func.attr
                    
                    is_compute = False
                    compute_method = None
                    # Check kwargs for 'compute'
                    for kw in node.value.keywords:
                        if kw.arg == 'compute' and isinstance(kw.value, ast.Constant):
                            is_compute = True
                            compute_method = kw.value.value
                    
                    self.models[self.current_model]['fields'][field_name] = {
                        'type': field_type,
                        'is_compute': is_compute,
                        'compute_method': compute_method,
                        'explicit_depends': [],
                        'implicit_depends': []
                    }
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if not self.current_model:
            return
        
        explicit_depends = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if dec.func.attr == 'depends':
                    for arg in dec.args:
                        if isinstance(arg, ast.Constant):
                            explicit_depends.append(arg.value)
        
        # Very simple heuristic for implicit dependencies: look for attribute access on variables
        # Usually 'self' or 'record' or 'rec'
        implicit_depends = set()
        for body_node in ast.walk(node):
            if isinstance(body_node, ast.Attribute) and isinstance(body_node.value, ast.Name):
                # If we access something like record.partner_id
                # This is a naive check but works for a basic audit
                implicit_depends.add(body_node.attr)
        
        self.models[self.current_model]['methods'][node.name] = {
            'explicit_depends': explicit_depends,
            'implicit_depends': list(implicit_depends)
        }
        self.generic_visit(node)

all_results = {}

for module in custom_modules:
    module_path = os.path.join(addons_path, module)
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    tree = ast.parse(source)
                    visitor = OdooASTVisitor()
                    visitor.visit(tree)
                    
                    # Merge results
                    for model, data in visitor.models.items():
                        if model not in all_results:
                            all_results[model] = {'fields': {}}
                        
                        for f_name, f_data in data['fields'].items():
                            # Link compute methods
                            if f_data['is_compute'] and f_data['compute_method'] in data['methods']:
                                method_info = data['methods'][f_data['compute_method']]
                                f_data['explicit_depends'] = method_info['explicit_depends']
                                # Filter out generic python methods from implicit depends
                                f_data['implicit_depends'] = [attr for attr in method_info['implicit_depends'] if attr not in ['env', 'ids', 'browse', 'search', 'read', 'write', 'create', 'unlink']]
                            
                            all_results[model]['fields'][f_name] = f_data
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")

# Save the audit report
output_file = "/home/niaj/Documents/PrecisionTex-Odoo/field_audit_report.json"
with open(output_file, 'w') as f:
    json.dump(all_results, f, indent=4)

print(f"Audit complete. Extracted {sum(len(m['fields']) for m in all_results.values())} fields across {len(all_results)} models.")
print(f"Report saved to {output_file}")
