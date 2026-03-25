import ast
import os
import sys

stdlib = sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else set()
def get_imports(path):
    imports = set()
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for name in node.names:
                                imports.add(name.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split('.')[0])
                except Exception:
                    pass
    return imports

third_party = set()
all_imports = get_imports('.')
for imp in all_imports:
    if imp not in stdlib and imp not in ['models', 'config', 'nlp', 'events', 'trust', 'ingestion', 'api', 'utils', 'streaming', 'search', 'schemas', 'workers', 'db', 'app']:
        third_party.add(imp)

print("FOUND IMPORTS:", sorted(list(third_party)))
