import ast
from pathlib import Path
from collections import defaultdict
from typing import DefaultDict
from importlib.machinery import PathFinder

def create_code_data(project_dir: Path):
    per_file_data: DefaultDict[str, dict[str, list[str | dict[str, str | list[str]]]]] = defaultdict(
        lambda: {"imports": [], "classes": [], "functions": []}
    )

    for file_path in project_dir.rglob(pattern="*.py"):
        file_content = file_path.read_text(encoding="utf-8")
        normalized_file_path = normalize_file_path(file_path=file_path, project_dir=project_dir)
        ast_tree = ast.parse(source=file_content)
        for node in ast.walk(ast_tree):
            # Capture only Imports for data creation
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                import_data = handle_imports(project_dir=project_dir, node=node)
                print(import_data)
                # direct_imports = [imp.name for imp in node.names]
                per_file_data[normalized_file_path]["imports"].extend(import_data)
            # elif isinstance(node, ast.ImportFrom):
            #     from_module = node.module
            #     from_imports = [from_module + "." + imp.name for imp in node.names]
            #     per_file_data[normalized_file_path]["imports"](from_imports)
            # elif isinstance(node, ast.ClassDef):
            #     # print(node.bases)
            #     class_data = handle_classes(node=node)
            #     per_file_data[normalized_file_path]["classes"].extend(class_data)
            # elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            #     function_data = handle_functions(node=node)
            #     per_file_data[normalized_file_path]["functions"].extend(function_data)
            #     # per_file_data[normalized_file_path]["functions"].extend(node.name)

    return per_file_data

def normalize_file_path(file_path: Path, project_dir: Path) -> str:
    return str(Path(str(file_path).split(str(project_dir))[1][1:]).as_posix()).replace("/", ".").replace(".py", "")

def handle_imports(project_dir: Path, node: ast.Import | ast.ImportFrom) -> list:
    """
    Filter all the third party imports, keep only in-project imports
    return [list of all imports]
    """
    import_list = []
    if isinstance(node, ast.Import):
        direct_imports = [imp.name for imp in node.names]
        for imp in direct_imports:
            if is_project_import(name=imp, project_dir=project_dir):
                import_list.append(imp)
    else:
        from_import = node.module
        if is_project_import(name=from_import, project_dir=project_dir):
            resolved_imports = [node.module + "." + imp.name for imp in node.names]
            for imp in resolved_imports:
                    import_list.append(imp)

    return import_list

def handle_classes(node: ast.ClassDef) -> dict:
    """
    return {
        "name": "class name",
        "inherited": [list of inherited class names],
        "": [],
        "functions": ["list of function names],
        "description": Use get_docstring here
    }
    """
    pass

def handle_functions(node: ast.FunctionDef) -> list:
    """
    return {
        "name": "function name",
        "sub functions": [list of all sub functions],
        "arguments": [list of all arguments],
        "returns": "What is the return type of the function",
        "description": Use get_docstring here
    }
    """
    pass

def handle_call_graph():

    ### Explore pyan library for call graph

    pass

def is_project_import(name: str, project_dir: Path) -> bool:
    
    search_paths = [str(project_dir)]

    spec = PathFinder.find_spec(name, search_paths)

    if not spec or not spec.origin:
        return False

    path = spec.origin

    if path.startswith(str(project_dir)):
        return True
    return False
