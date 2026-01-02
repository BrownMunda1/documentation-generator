from pathlib import Path

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter


def create_documents(project_dir: Path):

    # Step 1: Load all docs from local folder into langchain Documents
    # Step 2: Split each doc for better processing

    loader = GenericLoader.from_filesystem(
        path=str(project_dir),
        glob="**/*.py",
        exclude=["**/test_*.py", "**/__init__.py"],
        parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
    )

    loaded_docs = loader.load()

    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=4000, chunk_overlap=200
    )

    split_docs = splitter.split_documents(documents=loaded_docs)

    return split_docs
