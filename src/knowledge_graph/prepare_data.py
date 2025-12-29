import ast
import json
from collections import defaultdict
from importlib.machinery import PathFinder
from pathlib import Path
from typing import DefaultDict

from loguru import logger


def create_code_data(project_dir: Path):
    per_file_data: DefaultDict[
        str, dict[str, list[str | dict[str, str | list[str]]]]
    ] = defaultdict(lambda: {"imports": [], "classes": [], "functions": []})

    for file_path in project_dir.rglob(pattern="*.py"):
        file_content = file_path.read_text(encoding="utf-8")
        normalized_file_path = normalize_file_path(
            file_path=file_path, project_dir=project_dir
        )
        ast_tree = ast.parse(source=file_content)
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                import_data = handle_imports(project_dir=project_dir, node=node)
                # print(normalized_file_path, ast.unparse(node), import_data)
                per_file_data[normalized_file_path]["imports"].extend(import_data)
            elif isinstance(node, ast.ClassDef):
                class_data = handle_classes(node=node)
                per_file_data[normalized_file_path]["classes"].append(class_data)
            elif isinstance(node, ast.FunctionDef) or isinstance(
                node, ast.AsyncFunctionDef
            ):
                function_data = handle_functions(node=node)
                per_file_data[normalized_file_path]["functions"].append(function_data)

    save_results_path = project_dir / "code_structure.json"
    save_results_path.write_text(json.dumps(per_file_data, indent=4))

    return per_file_data


def normalize_file_path(file_path: Path, project_dir: Path) -> str:
    return (
        str(Path(str(file_path).split(str(project_dir))[1][1:]).as_posix())
        .replace("/", ".")
        .replace(".py", "")
    )


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
        "decorators": [list of decorators over the class names],
        "functions": ["list of function names],
        "description": Use get_docstring here
    }
    """
    class_name = node.name
    description = ast.get_docstring(node=node)
    inherted_classes = [ast.unparse(base) for base in node.bases]
    decorators = [ast.unparse(d) for d in node.decorator_list]

    functions_implemeted = []
    constructor_args = []
    for b in node.body:
        if isinstance(b, ast.FunctionDef):
            func_name = b.name
            if func_name == "__init__":
                arg_str = ast.unparse(b.args)
                args = [
                    {
                        arg.strip()
                        .split(":")[0]
                        .strip(): arg.strip()
                        .split(":")[1]
                        .strip()
                    }
                    if len(arg.strip().split(":")) > 1
                    else {arg.strip(): "Unknown"}
                    for arg in arg_str.split(",")[1:]
                ]
                constructor_args.extend(args)
            if not func_name.startswith("_"):
                functions_implemeted.append(func_name)

    return {
        "name": class_name,
        "description": description,
        "inherited": inherted_classes,
        "constructor_args": constructor_args,
        "public_functions": functions_implemeted,
        "decorators": decorators,
    }


def handle_functions(node: ast.FunctionDef) -> list:
    """
    return {
        "name": "function name",
        "decorators": [list of decorators],
        "arguments": [list of all arguments],
        "returns": "What is the return type of the function",
        "description": Use get_docstring here
    }
    """
    func_name = node.name
    description = ast.get_docstring(node=node)

    try:
        return_type = ast.unparse(node.returns)
    except Exception as e:
        return_type = "Unknown"

    decorators = [ast.unparse(d) for d in node.decorator_list]
    arg_str = ast.unparse(node.args)
    arguments = [
        {arg.strip().split(":")[0].strip(): arg.strip().split(":")[1].strip()}
        if len(arg.strip().split(":")) > 1
        else {arg.strip(): "Unknown"}
        for arg in arg_str.split(",")
    ]

    return {
        "name": func_name,
        "description": description,
        "return_type": return_type,
        "arguments": arguments,
        "decorators": decorators,
    }


def handle_call_graph():

    ### Explore pyan library for call graph

    pass


def is_project_import(name: str, project_dir: Path) -> bool:

    search_paths = [str(project_dir)]

    spec = PathFinder.find_spec(fullname=name, path=search_paths)

    if not spec or not spec.origin:
        return False

    path = spec.origin

    if path.startswith(str(project_dir)):
        return True
    return False
