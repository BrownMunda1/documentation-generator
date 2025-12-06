import ast
from pathlib import Path
from collections import defaultdict

def create_file_to_import_mapping(project_dir: Path):
    file_to_imports: dict[str, list[str]] = defaultdict(list)

    for file_path in project_dir.rglob(pattern="*.py"):
        file_content = file_path.read_text(encoding="utf-8")
        normalized_file_path = normalize_file_path(file_path=file_path, project_dir=project_dir)
        ast_tree = ast.parse(source=file_content)
        for node in ast.walk(ast_tree):
            # Capture only Imports for data creation
            if isinstance(node, ast.Import):
                direct_imports = [imp.name for imp in node.names]
                file_to_imports[normalized_file_path].extend(direct_imports)
            elif isinstance(node, ast.ImportFrom):
                from_module = node.module
                from_imports = [from_module + "." + imp.name for imp in node.names]
                file_to_imports[normalized_file_path].extend(from_imports)

    return file_to_imports

def normalize_file_path(file_path: Path, project_dir: Path) -> str:
    return str(Path(str(file_path).split(str(project_dir))[1][1:]).as_posix()).replace("/", ".").replace(".py", "")
