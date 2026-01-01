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
    ] = DefaultDict(lambda: {"imports": [], "classes": [], "functions": []})
    for file_path in project_dir.rglob(pattern="*.py"):
        file_content = file_path.read_text(encoding="utf-8")
        normalized_file_path = normalize_path(path=file_path, project_dir=project_dir)
        ast_tree = ast.parse(source=file_content)
        for node in ast.walk(ast_tree):
            for child in ast.iter_child_nodes(node=node):
                child.parent = node
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                resolved_imports_list = handle_imports(
                    project_dir=project_dir, file_path=file_path, node=node
                )
                per_file_data[normalized_file_path]["imports"].extend(
                    resolved_imports_list
                )
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


def is_path_dir(path: str, project_dir: Path):
    rel_path = path.replace(".", "/")
    dir_path = project_dir / Path(rel_path)

    if dir_path.exists():
        return "DIRECTORY"

    rel_path = rel_path + ".py"
    file_path = project_dir / Path(rel_path)
    if file_path.exists():
        return "FILE"

    return None


def normalize_path(path: Path, project_dir: Path) -> str:
    return (
        str(Path(str(path).split(str(project_dir))[1][1:]).as_posix())
        .replace("/", ".")
        .replace(".py", "")
    )


def handle_imports(
    project_dir: Path, file_path: Path, node: ast.Import | ast.ImportFrom
) -> list:
    """
    Filter all the third party imports, keep only in-project imports
    return [list of all imports]
    """
    import_list = []
    if isinstance(node, ast.Import):
        direct_imports = [imp.name for imp in node.names]
        for imp in direct_imports:
            is_valid, import_path = is_project_import(name=imp, project_dir=project_dir)
            if is_valid:
                import_list.append(import_path)
        return import_list
    elif isinstance(node, ast.ImportFrom):

        current_file_path = file_path

        import_module = node.module if node.module is not None else ""
        if node.level == 0:
            is_valid, import_path = is_project_import(
                name=import_module, project_dir=project_dir
            )
            if is_valid:

                # Handle like normal Import
                if ast.unparse(node.names) == "*":
                    resolved_imports = [import_path]

                else:
                    is_dir = is_path_dir(path=import_path, project_dir=project_dir)
                    if is_dir:
                        if is_dir.lower() == "directory":
                            resolved_imports = [
                                import_path + "." + imp.name for imp in node.names
                            ]
                        else:
                            resolved_imports = [import_path]
            else:
                resolved_imports = []
        else:
            level = node.level
            parent_import = current_file_path
            while level > 0:
                parent_import = parent_import.parent
                level -= 1

            normal_file_path = normalize_path(
                path=parent_import, project_dir=project_dir
            )

            import_module = node.module if node.module is not None else ""

            if normal_file_path == ".":
                abs_import = import_module
            elif import_module == "":
                abs_import = normal_file_path
            else:
                abs_import = normal_file_path + "." + import_module

            # Handle like normal Import
            if ast.unparse(node.names) == "*":
                resolved_imports = [abs_import]

            else:
                is_dir = is_path_dir(path=abs_import, project_dir=project_dir)
                if is_dir:
                    if is_dir.lower() == "directory":
                        resolved_imports = [
                            abs_import + "." + imp.name for imp in node.names
                        ]
                    else:
                        resolved_imports = [abs_import]
        return resolved_imports


def is_project_import(name: str, project_dir: Path) -> bool:

    module_parts = name.split(".")
    search_module = module_parts[0]

    # Handle the case where the import is a direct file
    file_module = search_module + ".py"

    is_valid = False
    abs_path = None
    matching_paths = project_dir.rglob(pattern=search_module, case_sensitive=True)
    if not matching_paths or len(list(matching_paths)) == 0:
        search_module = file_module

    for item in project_dir.rglob(pattern=search_module, case_sensitive=True):
        if item.is_dir():
            rem_parts = module_parts[1:]
            current_path = item
            for part in rem_parts:
                current_path = current_path / part
                if not current_path.exists():
                    is_valid = False
                    break
                elif not current_path.is_dir():
                    current_path = current_path.with_suffix(".py")
                    if current_path.is_file():
                        is_valid = True
                        abs_path = normalize_path(
                            path=current_path, project_dir=project_dir
                        )
                    break

            if not is_valid and current_path.exists():
                is_valid = True
                abs_path = normalize_path(path=current_path, project_dir=project_dir)

            if is_valid:
                break

        elif item.is_file():
            is_valid = True
            abs_path = normalize_path(path=item, project_dir=project_dir)
            break

    return is_valid, abs_path


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


def handle_functions(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list:
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
