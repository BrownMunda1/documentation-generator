from pathlib import Path

from knowledge_graph.prepare_data import create_file_to_import_mapping
from llm_utility.caller import call_llm


def create_kg(project_dir: Path):

    data: dict[str, list[str]] = create_file_to_import_mapping(project_dir=project_dir)

    response = call_llm(
        prompt=f"""Create a knowledge graph like structure for this data. The keys are the module paths and the values are the imported packages/functions. Here is the data:
        {data}"""
    )

    return response
